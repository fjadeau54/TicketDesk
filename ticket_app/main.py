import sys
from pathlib import Path

# Permet l'exécution directe du fichier ou depuis un binaire PyInstaller
if __package__ in (None, ""):
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    for p in (base_path, base_path.parent):
        p_str = str(p)
        if p_str not in sys.path:
            sys.path.insert(0, p_str)
    __package__ = "ticket_app"

from PySide6.QtWidgets import QApplication
from ticket_app.db.database import init_db
from ticket_app.ui.main_window import MainWindow
from ticket_app.utils.logging_utils import setup_logging
from ticket_app.config import STYLES_PATH

def main():
    setup_logging()
    init_db()

    app = QApplication(sys.argv)

    # feuille de style
    if STYLES_PATH.exists():
        with open(STYLES_PATH, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
