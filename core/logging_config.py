"""
Configuración centralizada de logging para TARS
"""
import logging
import os

LOG_LEVEL = os.environ.get("TARS_LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
