import logging
from ..config import LOG_PATH

def setup_logging():
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logging.getLogger().info("Application démarrée")
