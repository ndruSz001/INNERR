import json
import os
import sqlite3
from datetime import datetime

class DatabaseHandler:
    def __init__(self, db_path="tars_database.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Inicializa la base de datos con tablas necesarias."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla para historial de cálculos (ej. torque)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historial_calculos (
                id INTEGER PRIMARY KEY,
                tipo TEXT,
                descripcion TEXT,
                fecha TEXT,
                usuario TEXT
            )
        ''')
        
        # Tabla para preferencias de usuario
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferencias_usuario (
                id INTEGER PRIMARY KEY,
                usuario TEXT,
                categoria TEXT,
                preferencia TEXT,
                fecha TEXT
            )
        ''')
        
        # Tabla para logs médicos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs_medicos (
                id INTEGER PRIMARY KEY,
                paciente TEXT,
                descripcion TEXT,
                fecha TEXT,
                usuario TEXT
            )
        ''')
        
        conn.commit()
        conn.close()

    def guardar_calculo(self, tipo, descripcion, usuario):
        """Guarda un cálculo en el historial."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        fecha = datetime.now().isoformat()
        cursor.execute('INSERT INTO historial_calculos (tipo, descripcion, fecha, usuario) VALUES (?, ?, ?, ?)',
                       (tipo, descripcion, fecha, usuario))
        conn.commit()
        conn.close()

    def guardar_preferencia(self, usuario, categoria, preferencia):
        """Guarda una preferencia de usuario."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        fecha = datetime.now().isoformat()
        cursor.execute('INSERT INTO preferencias_usuario (usuario, categoria, preferencia, fecha) VALUES (?, ?, ?, ?)',
                       (usuario, categoria, preferencia, fecha))
        conn.commit()
        conn.close()

    def guardar_log_medico(self, paciente, descripcion, usuario):
        """Guarda un log médico."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        fecha = datetime.now().isoformat()
        cursor.execute('INSERT INTO logs_medicos (paciente, descripcion, fecha, usuario) VALUES (?, ?, ?, ?)',
                       (paciente, descripcion, fecha, usuario))
        conn.commit()
        conn.close()

    def obtener_preferencias(self, usuario, categoria=None):
        """Obtiene preferencias de un usuario."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if categoria:
            cursor.execute('SELECT preferencia FROM preferencias_usuario WHERE usuario = ? AND categoria = ? ORDER BY fecha DESC LIMIT 1',
                           (usuario, categoria))
        else:
            cursor.execute('SELECT categoria, preferencia FROM preferencias_usuario WHERE usuario = ? ORDER BY fecha DESC',
                           (usuario,))
        results = cursor.fetchall()
        conn.close()
        return results

    def obtener_historial(self, tipo=None, usuario=None):
        """Obtiene historial de cálculos."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = 'SELECT tipo, descripcion, fecha FROM historial_calculos WHERE 1=1'
        params = []
        if tipo:
            query += ' AND tipo = ?'
            params.append(tipo)
        if usuario:
            query += ' AND usuario = ?'
            params.append(usuario)
        query += ' ORDER BY fecha DESC LIMIT 10'
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results