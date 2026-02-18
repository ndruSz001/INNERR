# conversation_manager/__init__.py
"""
Módulo de gestión de conversaciones para TARS.
Incluye administración, búsqueda, resumen y grafo de conversaciones.

Ejemplo de uso:
	from conversation_manager import ConversationManager
	cm = ConversationManager()
	cm.nueva_conversacion("Proyecto IA")
"""

from .manager import ConversationManager