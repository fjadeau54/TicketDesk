import logging
from logging.handlers import RotatingFileHandler
from ..config import LOG_PATH


def setup_logging():
    """Configure a simple rotating file + console logger."""
    LOG_PATH.parent.mkdir(exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )

    file_handler = RotatingFileHandler(LOG_PATH, maxBytes=500_000, backupCount=3)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    root = logging.getLogger()
    if not root.handlers:
        root.setLevel(logging.INFO)
        root.addHandler(file_handler)
        root.addHandler(console_handler)
