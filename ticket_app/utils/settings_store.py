import json
from pathlib import Path
from ..config import DATA_DIR

SETTINGS_PATH = DATA_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "alerts": {
        "one_day_before": True,
        "day_of": True,
        "overdue": True,
    },
    "language": "fr",
    "shortcuts": {
        "palette": "Ctrl+K",
        "new": "Ctrl+N",
        "edit": "Ctrl+E",
        "delete": "Del",
        "archive": "Ctrl+Shift+A",
        "refresh": "F5",
        "focus_search": "Ctrl+F",
        "settings": "Ctrl+,",
        "kanban": "Ctrl+B",
    },
}


def load_settings() -> dict:
    if not SETTINGS_PATH.exists():
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}
    merged = DEFAULT_SETTINGS.copy()
    merged.update(data)
    merged.setdefault("alerts", {}).update(data.get("alerts", {}))
    return merged


def save_settings(data: dict):
    SETTINGS_PATH.parent.mkdir(exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_alert_settings() -> dict:
    settings = load_settings()
    return settings.get("alerts", DEFAULT_SETTINGS["alerts"]).copy()
