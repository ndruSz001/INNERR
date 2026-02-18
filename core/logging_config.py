"""
logging_config.py
Configuración centralizada de logging para TARS.

Ejemplo de uso:
    from core.logging_config import get_logger
    logger = get_logger(__name__)
    logger.info("Mensaje de prueba")
"""
import logging
import os

LOG_LEVEL = os.environ.get("TARS_LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
