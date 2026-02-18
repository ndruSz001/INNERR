# storage/__init__.py
"""
Módulo de almacenamiento persistente para TARS.
Incluye gestión de conversaciones, proyectos y base de datos.

Ejemplo de uso:
	from storage.conversation_storage import ConversationStorage
	from storage.db_manager import DatabaseManager
	db = DatabaseManager()
	storage = ConversationStorage(db)
	storage.save_conversation("user", "Título", [])
"""
