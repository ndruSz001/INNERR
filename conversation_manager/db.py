"""
Copyright (c) 2026 ndrz02
Todos los derechos reservados.
Licencia MIT: ver LICENSE y AUTORÍA_Y_LICENCIA.md
"""

"""
db.py
Gestión de conexión y migración de base de datos para conversaciones.

Ejemplo de uso:
    from conversation_manager.db import execute_query
    resultado = execute_query("conversations.db", "SELECT * FROM conversaciones", fetchall=True)
    print(resultado)
"""

def get_cursor(db_path):
    """Devuelve un cursor y conexión a la base de datos (debe cerrarse manualmente)."""
    import sqlite3
    conn = sqlite3.connect(str(db_path))
    return conn, conn.cursor()

def execute_query(db_path, query, params=None, fetchone=False, fetchall=False, commit=False):
    """
    Ejecuta un query SQL y retorna resultados si corresponde.
    """
    import sqlite3
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    if params is None:
        params = []
    cursor.execute(query, params)
    result = None
    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()
    if commit:
        conn.commit()
    conn.close()
    return result
"""
db.py
Gestión de conexión y migración de base de datos para conversaciones.
"""
import sqlite3
from pathlib import Path

def get_connection(db_path: Path):
    return sqlite3.connect(str(db_path))


def init_database(db_path):
    """Inicializa base de datos de conversaciones y sus tablas."""
    import sqlite3
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Tabla de conversaciones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversaciones (
            id TEXT PRIMARY KEY,
            titulo TEXT,
            descripcion TEXT,
            categoria TEXT,
            fecha_inicio TEXT,
            fecha_ultima_actividad TEXT,
            num_mensajes INTEGER DEFAULT 0,
            estado TEXT DEFAULT 'activa',
            tags TEXT,
            proyecto_relacionado TEXT,
            importancia INTEGER DEFAULT 5,
            metadata TEXT,
            es_integradora INTEGER DEFAULT 0,
            objetivo TEXT,
            conclusiones TEXT,
            resultados TEXT
        )
    ''')

    # Tabla de mensajes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversacion_id TEXT,
            timestamp TEXT,
            tipo TEXT,
            contenido TEXT,
            metadata TEXT,
            FOREIGN KEY(conversacion_id) REFERENCES conversaciones(id)
        )
    ''')

    # Tabla de contexto de conversación
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contexto_conversacion (
            conversacion_id TEXT,
            clave TEXT,
            valor TEXT,
            timestamp TEXT,
            PRIMARY KEY (conversacion_id, clave),
            FOREIGN KEY(conversacion_id) REFERENCES conversaciones(id)
        )
    ''')

    # Tabla de resúmenes (opcional, para tests avanzados)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resumenes (
            conversacion_id TEXT PRIMARY KEY,
            resumen_corto TEXT,
            resumen_largo TEXT,
            palabras_clave TEXT,
            temas_principales TEXT,
            fecha_generacion TEXT,
            FOREIGN KEY(conversacion_id) REFERENCES conversaciones(id)
        )
    ''')

    conn.commit()
    conn.close()
