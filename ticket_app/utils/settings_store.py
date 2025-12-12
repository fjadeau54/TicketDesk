import copy
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
    "appearance": {
        "mode": "light",
        "kanban_column": "#f6f6f6",
    },
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


def _deep_merge(base: dict, override: dict | None) -> dict:
    """
    Merge two dicts without mutating inputs.
    Nested dicts are merged recursively, other values are replaced.
    """
    result = copy.deepcopy(base)
    if not override:
        return result
    for key, val in override.items():
        if isinstance(val, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = copy.deepcopy(val)
    return result


def load_settings() -> dict:
    if not SETTINGS_PATH.exists():
        return copy.deepcopy(DEFAULT_SETTINGS)
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}
    return _deep_merge(DEFAULT_SETTINGS, data)


def save_settings(data: dict):
    SETTINGS_PATH.parent.mkdir(exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_alert_settings() -> dict:
    settings = load_settings()
    return settings.get("alerts", DEFAULT_SETTINGS["alerts"]).copy()
