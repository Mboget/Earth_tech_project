import json
import locale
from pathlib import Path


def _progress_path():
    return Path(__file__).resolve().parent / "progress.json"


def load_progress():
    path = _progress_path()
    if not path.exists():
        return {"unlocked_level": 1, "controls": None, "level_stars": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        unlocked = int(data.get("unlocked_level", 1))
        controls = data.get("controls")
        level_stars = data.get("level_stars", {}) or {}
        # Normalize keys as strings and values as ints
        normalized = {str(k): int(v) for k, v in level_stars.items() if v is not None}
        return {"unlocked_level": max(1, unlocked), "controls": controls, "level_stars": normalized}
    except (ValueError, json.JSONDecodeError):
        return {"unlocked_level": 1, "controls": None, "level_stars": {}}


def detect_default_controls():
    try:
        loc = locale.getdefaultlocale()[0] or ""
    except (AttributeError, TypeError):
        loc = ""
    loc = loc.lower()
    if loc.startswith("fr") or "fr_" in loc:
        return "zqsd"
    return "wasd"


def save_progress(unlocked_level, controls=None, level_stars=None):
    path = _progress_path()
    data = {"unlocked_level": int(unlocked_level)}
    if controls:
        data["controls"] = controls
    else:
        if path.exists():
            try:
                existing = json.loads(path.read_text(encoding="utf-8"))
                if existing.get("controls"):
                    data["controls"] = existing["controls"]
            except (ValueError, json.JSONDecodeError):
                pass
    if level_stars is not None:
        data["level_stars"] = {str(k): int(v) for k, v in level_stars.items()}
    else:
        if path.exists():
            try:
                existing = json.loads(path.read_text(encoding="utf-8"))
                if existing.get("level_stars"):
                    data["level_stars"] = existing["level_stars"]
            except (ValueError, json.JSONDecodeError):
                pass
    path.write_text(json.dumps(data), encoding="utf-8")
