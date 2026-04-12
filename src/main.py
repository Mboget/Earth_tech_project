import importlib.util
import os
import subprocess
import sys
from pathlib import Path
import venv
import shutil
from codecarbon import EmissionsTracker


def _ensure_requirements():
    required_modules = ["pygame", "cv2"]
    missing = [name for name in required_modules if importlib.util.find_spec(name) is None]
    if not missing:
        return
    req_path = Path(__file__).resolve().parents[1] / "requirements.txt"
    if not req_path.exists():
        return
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req_path)])


def _ensure_venv():
    project_root = Path(__file__).resolve().parents[1]
    venv_dir = project_root / "venv"
    if not venv_dir.exists():
        builder = venv.EnvBuilder(with_pip=True)
        builder.create(venv_dir)

    if sys.prefix != sys.base_prefix:
        return

    python_path = venv_dir / "Scripts" / "python.exe"
    if not python_path.exists():
        python_path = venv_dir / "bin" / "python"
    if python_path.exists():
        subprocess.check_call([str(python_path)] + sys.argv)
        sys.exit(0)


def _generate_intro_if_missing():
    project_root = Path(__file__).resolve().parents[1]
    intro_path = project_root / "asset" / "intro.mp4"
    if intro_path.exists():
        return intro_path
    media_dir = project_root / "asset" / ".manim_media"
    lock_path = project_root / "asset" / ".intro_building"
    if media_dir.exists():
        candidates = list(media_dir.rglob("intro.mp4"))
        if candidates:
            newest = max(candidates, key=lambda p: p.stat().st_mtime)
            intro_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(newest, intro_path)
            if lock_path.exists():
                try:
                    lock_path.unlink()
                except OSError:
                    pass
            return intro_path
    script_path = project_root / "asset" / "intro_manim.py"
    if not script_path.exists():
        return intro_path
    if importlib.util.find_spec("manim") is None:
        req_path = project_root / "requirements.txt"
        if req_path.exists():
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "manim"])
            except (OSError, subprocess.CalledProcessError):
                return intro_path
        else:
            return intro_path

    media_dir.mkdir(parents=True, exist_ok=True)
    if lock_path.exists():
        return intro_path
    lock_path.write_text("building", encoding="utf-8")
    try:
        subprocess.Popen(
            [
                sys.executable,
                "-m",
                "manim",
                "-qm",
                "--media_dir",
                str(media_dir),
                "-o",
                "intro.mp4",
                str(script_path),
                "IntroText",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        try:
            lock_path.unlink()
        except OSError:
            pass
        return intro_path
    return intro_path


def main():
    _ensure_venv()
    _ensure_requirements()

    intro_path = _generate_intro_if_missing()

    import pygame

    from app.game import run as run_game
    from app.intro_video import play_intro
    from app.menu import run as run_menu, run_level_select, run_controls
    from app.progress import load_progress, save_progress, detect_default_controls

    pygame.init()
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h))
    pygame.display.set_caption("Waste Sorter")

    max_level = 6
    progress = load_progress()
    unlocked_level = progress.get("unlocked_level", 1)
    controls = progress.get("controls")
    level_stars = progress.get("level_stars", {})
    if not controls:
        controls = detect_default_controls()
        save_progress(unlocked_level, controls, level_stars)

    play_intro(screen, str(intro_path), show_missing=False)

    while True:
        choice = run_menu(screen)
        if choice == "play_solo":
            completed, completed_stars = run_game(screen, start_level=1, max_level=max_level, controls=controls)
            if isinstance(completed, int):
                for lvl, stars in completed_stars.items():
                    level_stars[str(lvl)] = max(level_stars.get(str(lvl), 0), stars)
                if completed >= unlocked_level:
                    unlocked_level = min(max_level, completed + 1)
                save_progress(unlocked_level, controls, level_stars)
        elif choice == "play_duo":
            run_game(screen, start_level=1, max_level=max_level, controls=controls, two_players=True)
        elif choice == "levels":
            selection = run_level_select(screen, max_level=max_level, unlocked_level=unlocked_level, level_stars=level_stars)
            if selection == "back":
                continue
            if isinstance(selection, int):
                completed, completed_stars = run_game(screen, start_level=selection, max_level=max_level, controls=controls)
                if isinstance(completed, int):
                    for lvl, stars in completed_stars.items():
                        level_stars[str(lvl)] = max(level_stars.get(str(lvl), 0), stars)
                    if completed >= unlocked_level:
                        unlocked_level = min(max_level, completed + 1)
                    save_progress(unlocked_level, controls, level_stars)
        elif choice == "controls":
            new_controls = run_controls(screen, current_controls=controls)
            if new_controls in ("wasd", "zqsd"):
                controls = new_controls
                save_progress(unlocked_level, controls, level_stars)
        else:
            break

    pygame.quit()
    sys.exit()

tracker= EmissionsTracker
tracker.start()
try:
    if __name__ == "__main__":
     main()
finally:
    tracker.stop()