import json
import locale
from pathlib import Path


def _progress_path():
    return Path(__file__).resolve().parent / "progress.json"


def load_progress():
    path = _progress_path()
    if not path.exists():
        return {"unlocked_level": 1, "controls": None}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        unlocked = int(data.get("unlocked_level", 1))
        controls = data.get("controls")
        return {"unlocked_level": max(1, unlocked), "controls": controls}
    except (ValueError, json.JSONDecodeError):
        return {"unlocked_level": 1, "controls": None}


def detect_default_controls():
    try:
        loc = locale.getdefaultlocale()[0] or ""
    except (AttributeError, TypeError):
        loc = ""
    loc = loc.lower()
    if loc.startswith("fr") or "fr_" in loc:
        return "zqsd"
    return "wasd"


def save_progress(unlocked_level, controls=None):
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
    path.write_text(json.dumps(data), encoding="utf-8")
