"""
config.py
Configuración centralizada para TARS.
Incluye rutas, parámetros y settings globales.

Ejemplo de uso:
    from core.config import DATA_DIR, DEFAULT_TEXT_MODEL
    print(DATA_DIR)
"""
import os
from pathlib import Path

# Rutas base
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROJECTS_DIR = DATA_DIR / "projects"
HARDWARE_DIR = DATA_DIR / "hardware"

# Parámetros globales
DEFAULT_BACKUP_DIR = BASE_DIR / "backups"
DEFAULT_LOG_LEVEL = os.environ.get("TARS_LOG_LEVEL", "INFO")

# Modelos por defecto
DEFAULT_TEXT_MODEL = "microsoft/phi-2"
DEFAULT_VISION_MODEL = "llava-v1"

# Otros settings
MAX_CONVERSATIONS = 10
CONVERSATION_TTL_HOURS = 24

# Cargar variables de entorno si existe .env
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass
