"""
Pruebas unitarias para helpers de base de datos de conversation_manager.
"""
import unittest
from pathlib import Path
from conversation_manager.db import init_database, execute_query
import os

class TestConversationManagerDB(unittest.TestCase):
    def setUp(self):
        self.test_db = Path("test_conversations.db")
        if self.test_db.exists():
            os.remove(self.test_db)
        init_database(self.test_db)

    def tearDown(self):
        if self.test_db.exists():
            os.remove(self.test_db)

    def test_insert_and_query_conversation(self):
        # Insertar conversación
        execute_query(
            self.test_db,
            '''INSERT INTO conversaciones (id, titulo, descripcion, categoria, fecha_inicio, fecha_ultima_actividad, estado, tags, proyecto_relacionado, metadata) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            ["testid", "Test Título", "desc", "general", "2026-02-16T00:00:00", "2026-02-16T00:00:00", "activa", "[]", None, "{}"],
            commit=True
        )
        # Consultar conversación
        result = execute_query(
            self.test_db,
            'SELECT * FROM conversaciones WHERE id = ?',
            ["testid"],
            fetchone=True
        )
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "testid")
        self.assertEqual(result[1], "Test Título")

if __name__ == '__main__':
    unittest.main()
