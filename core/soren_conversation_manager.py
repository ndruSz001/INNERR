# Migración de ConversationManager para Soren
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import uuid

class SorenConversationManager:
    """
    Gestor de conversaciones con memoria persistente para Soren
    Permite crear, listar, retomar, archivar conversaciones, filtros, resúmenes, grafo de relaciones.
    """
    ...existing code...

# Punto de entrada
def main():
    manager = SorenConversationManager()
    print("Soren Conversation Manager iniciado.")
    # ...existing code...
