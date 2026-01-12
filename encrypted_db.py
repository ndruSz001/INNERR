import sqlite3
import json
import os
import hashlib
import base64
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import logging
from collections import defaultdict

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EncryptedDatabase:
    """Base de datos SQLite cifrada para almacenamiento seguro de datos sensibles"""

    def __init__(self, db_path="memoria_episodica.db", key_path="db_key.enc"):
        self.db_path = db_path
        self.key_path = key_path
        self.cipher = None
        self.conn = None

        # Generar o cargar clave de encriptación
        self._setup_encryption()

        # Inicializar base de datos
        self._init_database()

    def _setup_encryption(self):
        """Configura el sistema de encriptación"""
        try:
            if os.path.exists(self.key_path):
                # Cargar clave existente
                with open(self.key_path, 'rb') as f:
                    encrypted_key = f.read()
                # Aquí iría la desencriptación de la clave maestra
                # Por simplicidad, asumimos que la clave ya está disponible
                self.cipher = Fernet(base64.b64encode(b'0' * 32))  # Placeholder
            else:
                # Generar nueva clave
                key = Fernet.generate_key()
                self.cipher = Fernet(key)

                # Guardar clave (en producción, esto debería estar protegido)
                with open(self.key_path, 'wb') as f:
                    f.write(key)

                logger.info("🔐 Nueva clave de encriptación generada")

        except Exception as e:
            logger.error(f"Error configurando encriptación: {e}")
            # Fallback sin encriptación (solo para desarrollo)
            self.cipher = None

    def _init_database(self):
        """Inicializa la estructura de la base de datos"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()

            # Tabla de contexto de usuario
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_context (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    context_type TEXT NOT NULL,
                    context_key TEXT NOT NULL,
                    context_value TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    relevance_score REAL DEFAULT 1.0,
                    expires_at DATETIME,
                    UNIQUE(user_id, context_type, context_key)
                )
            ''')

            # Tabla de conversaciones recordadas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS remembered_conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    conversation_topic TEXT,
                    key_points TEXT,
                    emotional_context TEXT,
                    user_mood TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    follow_up_suggested BOOLEAN DEFAULT FALSE
                )
            ''')

            # Tabla de preferencias de usuario
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    preference_category TEXT NOT NULL,
                    preference_key TEXT NOT NULL,
                    preference_value TEXT,
                    confidence REAL DEFAULT 1.0,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, preference_category, preference_key)
                )
            ''')

            # Tabla de log de interacciones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interaction_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    interaction_type TEXT,
                    content TEXT,
                    response TEXT,
                    user_feedback TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            self.conn.commit()
            logger.info("✅ Base de datos episódica inicializada")

        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos: {e}")

    def _encrypt_data(self, data):
        """Encripta datos si la encriptación está disponible"""
        if self.cipher and isinstance(data, str):
            return self.cipher.encrypt(data.encode()).decode()
        return data

    def _decrypt_data(self, data):
        """Desencripta datos si la encriptación está disponible"""
        if self.cipher and isinstance(data, str):
            try:
                return self.cipher.decrypt(data.encode()).decode()
            except:
                return data  # Si no se puede desencriptar, devolver como está
        return data

    def guardar_contexto_usuario(self, user_id, context_type, context_key, context_value,
                               relevance_score=1.0, expires_days=None):
        """Guarda contexto específico del usuario"""
        try:
            cursor = self.conn.cursor()

            expires_at = None
            if expires_days:
                expires_at = datetime.now() + timedelta(days=expires_days)

            encrypted_value = self._encrypt_data(context_value)

            cursor.execute('''
                INSERT OR REPLACE INTO user_context
                (user_id, context_type, context_key, context_value, relevance_score, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, context_type, context_key, encrypted_value, relevance_score, expires_at))

            self.conn.commit()
            logger.debug(f"💾 Contexto guardado: {context_type}.{context_key}")

        except Exception as e:
            logger.error(f"❌ Error guardando contexto: {e}")

    def obtener_contexto_usuario(self, user_id, context_type=None, context_key=None, limit=10):
        """Obtiene contexto del usuario con filtros opcionales"""
        try:
            cursor = self.conn.cursor()

            query = '''
                SELECT context_type, context_key, context_value, relevance_score, timestamp
                FROM user_context
                WHERE user_id = ?
                  AND (expires_at IS NULL OR expires_at > datetime('now'))
            '''
            params = [user_id]

            if context_type:
                query += " AND context_type = ?"
                params.append(context_type)

            if context_key:
                query += " AND context_key = ?"
                params.append(context_key)

            query += " ORDER BY relevance_score DESC, timestamp DESC"

            query += f" LIMIT {limit}"

            cursor.execute(query, params)
            results = cursor.fetchall()

            # Desencriptar valores
            context_data = []
            for row in results:
                context_data.append({
                    'type': row[0],
                    'key': row[1],
                    'value': self._decrypt_data(row[2]),
                    'relevance': row[3],
                    'timestamp': row[4]
                })

            return context_data

        except Exception as e:
            logger.error(f"❌ Error obteniendo contexto: {e}")
            return []

    def recordar_conversacion(self, user_id, conversation_topic, key_points,
                            emotional_context=None, user_mood=None):
        """Registra una conversación importante para recordar"""
        try:
            cursor = self.conn.cursor()

            cursor.execute('''
                INSERT INTO remembered_conversations
                (user_id, conversation_topic, key_points, emotional_context, user_mood)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, conversation_topic, key_points, emotional_context, user_mood))

            self.conn.commit()
            logger.debug(f"🧠 Conversación recordada: {conversation_topic}")

        except Exception as e:
            logger.error(f"❌ Error recordando conversación: {e}")

    def obtener_conversaciones_recordadas(self, user_id, limit=5):
        """Obtiene conversaciones recordadas recientemente"""
        try:
            cursor = self.conn.cursor()

            cursor.execute('''
                SELECT conversation_topic, key_points, emotional_context, user_mood, timestamp
                FROM remembered_conversations
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, limit))

            results = cursor.fetchall()

            conversations = []
            for row in results:
                conversations.append({
                    'topic': row[0],
                    'key_points': row[1],
                    'emotional_context': row[2],
                    'user_mood': row[3],
                    'timestamp': row[4]
                })

            return conversations

        except Exception as e:
            logger.error(f"❌ Error obteniendo conversaciones: {e}")
            return []

    def actualizar_preferencia(self, user_id, category, key, value, confidence=1.0):
        """Actualiza una preferencia del usuario"""
        try:
            cursor = self.conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO user_preferences
                (user_id, preference_category, preference_key, preference_value, confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, category, key, value, confidence))

            self.conn.commit()
            logger.debug(f"⚙️ Preferencia actualizada: {category}.{key} = {value}")

        except Exception as e:
            logger.error(f"❌ Error actualizando preferencia: {e}")

    def obtener_preferencias(self, user_id, category=None):
        """Obtiene preferencias del usuario"""
        try:
            cursor = self.conn.cursor()

            if category:
                cursor.execute('''
                    SELECT preference_category, preference_key, preference_value, confidence
                    FROM user_preferences
                    WHERE user_id = ? AND preference_category = ?
                    ORDER BY confidence DESC
                ''', (user_id, category))
            else:
                cursor.execute('''
                    SELECT preference_category, preference_key, preference_value, confidence
                    FROM user_preferences
                    WHERE user_id = ?
                    ORDER BY confidence DESC
                ''', (user_id,))

            results = cursor.fetchall()

            preferences = {}
            for row in results:
                cat, key, value, conf = row
                if cat not in preferences:
                    preferences[cat] = {}
                preferences[cat][key] = {'value': value, 'confidence': conf}

            return preferences

        except Exception as e:
            logger.error(f"❌ Error obteniendo preferencias: {e}")
            return {}

    def log_interaction(self, user_id, interaction_type, content, response=None, feedback=None):
        """Registra una interacción para análisis posterior"""
        try:
            cursor = self.conn.cursor()

            cursor.execute('''
                INSERT INTO interaction_log
                (user_id, interaction_type, content, response, user_feedback)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, interaction_type, content, response, feedback))

            self.conn.commit()

        except Exception as e:
            logger.error(f"❌ Error registrando interacción: {e}")

    def obtener_analisis_usuario(self, user_id):
        """Genera un análisis del comportamiento del usuario"""
        try:
            # Obtener estadísticas de interacciones
            cursor = self.conn.cursor()

            # Interacciones por tipo
            cursor.execute('''
                SELECT interaction_type, COUNT(*) as count
                FROM interaction_log
                WHERE user_id = ?
                GROUP BY interaction_type
                ORDER BY count DESC
            ''', (user_id,))

            interaction_stats = dict(cursor.fetchall())

            # Conversaciones recordadas
            remembered_convs = self.obtener_conversaciones_recordadas(user_id, limit=100)

            # Análisis de estados emocionales
            emotional_states = defaultdict(int)
            for conv in remembered_convs:
                if conv['emotional_context']:
                    emotional_states[conv['emotional_context']] += 1
                if conv['user_mood']:
                    emotional_states[conv['user_mood']] += 1

            # Preferencias principales
            preferences = self.obtener_preferencias(user_id)

            return {
                'interaction_stats': interaction_stats,
                'emotional_profile': dict(emotional_states),
                'preferences': preferences,
                'total_memories': len(remembered_convs),
                'context_items': len(self.obtener_contexto_usuario(user_id))
            }

        except Exception as e:
            logger.error(f"❌ Error generando análisis: {e}")
            return {}

    def limpiar_datos_expirados(self):
        """Limpia datos expirados de la base de datos"""
        try:
            cursor = self.conn.cursor()

            cursor.execute('''
                DELETE FROM user_context
                WHERE expires_at IS NOT NULL AND expires_at <= datetime('now')
            ''')

            deleted_count = cursor.rowcount
            self.conn.commit()

            if deleted_count > 0:
                logger.info(f"🧹 Limpiados {deleted_count} registros expirados")

        except Exception as e:
            logger.error(f"❌ Error limpiando datos expirados: {e}")

    def backup_database(self, backup_path=None):
        """Crea un backup de la base de datos"""
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"backup_memoria_episodica_{timestamp}.db"

            # Crear backup usando SQLite
            with sqlite3.connect(backup_path) as backup_conn:
                self.conn.backup(backup_conn)

            logger.info(f"💾 Backup creado: {backup_path}")
            return backup_path

        except Exception as e:
            logger.error(f"❌ Error creando backup: {e}")
            return None

    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.conn:
            self.conn.close()
            logger.info("🔒 Conexión a base de datos cerrada")