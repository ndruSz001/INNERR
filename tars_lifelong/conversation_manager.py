"""
Módulo: conversation_manager.py
Responsable de la lógica de gestión de conversaciones, sesiones y contexto.
"""

from typing import Optional, List, Dict

class ConversationManager:
    def __init__(self):
        self.conversations = []  # Lista de conversaciones (puede ser dicts o instancias)
        self.current_conversation = None

    def start_new_conversation(self, topic: str = "", category: str = "general", tags: Optional[List[str]] = None) -> Dict:
        """Inicia una nueva conversación y la selecciona como actual."""
        conv = {
            "id": len(self.conversations) + 1,
            "topic": topic,
            "category": category,
            "tags": tags or [],
            "messages": []
        }
        self.conversations.append(conv)
        self.current_conversation = conv
        return conv

    def add_message(self, message: str, sender: str = "user"):
        """Agrega un mensaje a la conversación actual."""
        if self.current_conversation:
            self.current_conversation["messages"].append({"sender": sender, "text": message})

    def get_current_conversation(self) -> Optional[Dict]:
        return self.current_conversation

    def list_conversations(self) -> List[Dict]:
        return self.conversations

    def switch_conversation(self, conv_id: int) -> bool:
        for conv in self.conversations:
            if conv["id"] == conv_id:
                self.current_conversation = conv
                return True
        return False
