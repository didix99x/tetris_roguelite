"""logger.py - cria o arquivo logs/game.log (ou logs/launcher.log)."""
import logging
from logging.handlers import RotatingFileHandler

from paths import logs_dir


def setup_logging(filename="game.log"):
    """Configura o log e devolve o caminho do arquivo."""
    path = logs_dir() / filename
    handler = RotatingFileHandler(path, maxBytes=500_000, backupCount=1, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    root.addHandler(handler)
    return path
