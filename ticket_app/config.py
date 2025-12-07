import sys
from pathlib import Path

APP_NAME = "Ticket Manager"

# Répertoire où les fichiers de l'app sont situés (code/ressources)
RUNTIME_BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))

# Répertoire de données/logs : dans HOME quand l'app est packagée, sinon local
if getattr(sys, "frozen", False):
    APP_DATA_ROOT = Path.home() / ".ticket_app"
else:
    APP_DATA_ROOT = RUNTIME_BASE

DATA_DIR = APP_DATA_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "ticket_app.db"
LOG_DIR = APP_DATA_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "app.log"

ASSETS_DIR = RUNTIME_BASE / "assets"
STYLES_PATH = ASSETS_DIR / "styles.qss"
