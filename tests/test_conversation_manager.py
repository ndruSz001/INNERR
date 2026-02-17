"""
Pruebas de integración para ConversationManager completo (métodos migrados).
"""
import unittest
from pathlib import Path
from conversation_manager import ConversationManager
import os
import json

class TestConversationManagerIntegration(unittest.TestCase):
    def setUp(self):
        self.test_db = Path("test_conversations_full.db")
        if self.test_db.exists():
            os.remove(self.test_db)
        self.manager = ConversationManager(db_path=self.test_db)
        self.manager.init_database()

    def tearDown(self):
        if self.test_db.exists():
            os.remove(self.test_db)

    def test_nueva_y_listar_conversacion(self):
        conv_id = self.manager.nueva_conversacion(titulo="Test", categoria="prueba", tags=["tag1", "tag2"])
        convs = self.manager.listar_conversaciones()
        self.assertTrue(any(c["id"] == conv_id for c in convs))

    def test_agregar_y_continuar_conversacion(self):
        conv_id = self.manager.nueva_conversacion(titulo="Test2")
        self.manager.agregar_mensaje(conv_id, "user", "Hola mundo")
        data = self.manager.continuar_conversacion(conv_id)
        self.assertEqual(data["id"], conv_id)
        self.assertGreaterEqual(len(data["ultimos_mensajes"]), 1)

    def test_guardar_y_buscar_contexto(self):
        conv_id = self.manager.nueva_conversacion(titulo="Test3")
        self.manager.guardar_contexto(conv_id, "llave", "valor")
        data = self.manager.continuar_conversacion(conv_id)
        self.assertIn("llave", data["contexto"])
        self.assertEqual(data["contexto"]["llave"], "valor")

    def test_archivar_conversacion(self):
        conv_id = self.manager.nueva_conversacion(titulo="Test4")
        self.manager.archivar_conversacion(conv_id)
        convs = self.manager.listar_conversaciones(estado="archivada")
        self.assertTrue(any(c["id"] == conv_id for c in convs))

    def test_buscar_conversaciones(self):
        conv_id = self.manager.nueva_conversacion(titulo="BusquedaTest", descripcion="PalabraClaveUnica")
        resultados = self.manager.buscar_conversaciones("PalabraClaveUnica")
        self.assertTrue(any(r["id"] == conv_id for r in resultados))

if __name__ == '__main__':
    unittest.main()
