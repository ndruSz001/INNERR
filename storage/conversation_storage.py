"""
Conversation Storage - Guardar conversaciones en DB
Sprint 3 - FASE 8

Responsabilidad: Persistencia de conversaciones
- Guardar conversaciones en DB
- Índices por user_id, timestamp
- Limpieza automática >30 días
- Search fulltext
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from storage.db_manager import DatabaseManager, Conversation, Message

logger = logging.getLogger(__name__)


class ConversationStorage:
    """Almacenamiento persistente de conversaciones"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Args:
            db_manager: Instancia de DatabaseManager
        """
        self.db = db_manager
        logger.info("✅ Conversation Storage inicializado")
    
    def save_conversation(
        self,
        user_id: str,
        title: str,
        messages: List[Dict]
    ) -> str:
        """
        Guardar nueva conversación con mensajes
        
        Args:
            user_id: ID del usuario
            title: Título de la conversación
            messages: Lista de mensajes [{role, content}, ...]
            
        Returns:
            ID de la conversación guardada
        """
        conv_id = str(uuid.uuid4())
        
        try:
            # Crear conversación
            self.db.create_conversation(conv_id, user_id, title)
            
            # Agregar mensajes
            for i, msg in enumerate(messages):
                msg_id = str(uuid.uuid4())
                self.db.add_message(
                    msg_id,
                    conv_id,
                    msg.get('role', 'user'),
                    msg.get('content', '')
                )
            
            logger.info(f"✅ Conversación guardada: {conv_id} ({len(messages)} mensajes)")
            return conv_id
        
        except Exception as e:
            logger.error(f"❌ Error guardando conversación: {e}")
            return ""
    
    def add_message_to_conversation(
        self,
        conversation_id: str,
        role: str,
        content: str
    ) -> str:
        """
        Agregar un nuevo mensaje a conversación existente
        
        Args:
            conversation_id: ID de la conversación
            role: 'user' o 'assistant'
            content: Contenido del mensaje
            
        Returns:
            ID del mensaje
        """
        msg_id = str(uuid.uuid4())
        
        try:
            self.db.add_message(msg_id, conversation_id, role, content)
            logger.info(f"✅ Mensaje agregado: {msg_id}")
            return msg_id
        
        except Exception as e:
            logger.error(f"❌ Error agregando mensaje: {e}")
            return ""
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """
        Obtener historial completo de una conversación
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            Lista de mensajes en orden cronológico
        """
        try:
            messages = self.db.get_messages(conversation_id)
            return [
                {
                    'id': msg.id,
                    'role': msg.role,
                    'content': msg.content,
                    'timestamp': msg.created_at.isoformat()
                }
                for msg in messages
            ]
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo historial: {e}")
            return []
    
    def list_user_conversations(
        self,
        user_id: str,
        limit: int = 10,
        include_messages: bool = False
    ) -> List[Dict]:
        """
        Listar conversaciones de un usuario
        
        Args:
            user_id: ID del usuario
            limit: Máximo de conversaciones
            include_messages: Incluir mensajes en cada conversación
            
        Returns:
            Lista de conversaciones
        """
        try:
            conversations = self.db.list_conversations(user_id, limit)
            
            result = []
            for conv in conversations:
                conv_dict = {
                    'id': conv.id,
                    'title': conv.title,
                    'created_at': conv.created_at.isoformat(),
                    'updated_at': conv.updated_at.isoformat(),
                    'message_count': conv.message_count
                }
                
                if include_messages:
                    conv_dict['messages'] = self.get_conversation_history(conv.id)
                
                result.append(conv_dict)
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Error listando conversaciones: {e}")
            return []
    
    def search_conversations(
        self,
        user_id: str,
        query: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Buscar conversaciones por texto
        
        Args:
            user_id: ID del usuario
            query: Texto a buscar
            limit: Máximo de resultados
            
        Returns:
            Conversaciones coincidentes
        """
        try:
            conversations = self.db.list_conversations(user_id, limit=100)
            
            matching = []
            for conv in conversations:
                # Buscar en título
                if query.lower() in conv.title.lower():
                    matching.append(conv)
                    continue
                
                # Buscar en mensajes
                messages = self.db.get_messages(conv.id)
                for msg in messages:
                    if query.lower() in msg.content.lower():
                        matching.append(conv)
                        break
            
            return [
                {
                    'id': c.id,
                    'title': c.title,
                    'created_at': c.created_at.isoformat(),
                    'message_count': c.message_count
                }
                for c in matching[:limit]
            ]
        
        except Exception as e:
            logger.error(f"❌ Error buscando conversaciones: {e}")
            return []
    
    def cleanup_old_conversations(self, days: int = 30) -> int:
        """
        Limpiar conversaciones antiguas
        
        Args:
            days: Días de antigüedad para limpiar
            
        Returns:
            Número de conversaciones eliminadas
        """
        try:
            deleted = self.db.cleanup_old_conversations(days)
            logger.info(f"🧹 {deleted} conversaciones antiguas eliminadas")
            return deleted
        
        except Exception as e:
            logger.error(f"❌ Error limpiando conversaciones: {e}")
            return 0
    
    def export_conversation(self, conversation_id: str, format: str = "json") -> str:
        """
        Exportar conversación en diferentes formatos
        
        Args:
            conversation_id: ID de la conversación
            format: 'json' o 'txt'
            
        Returns:
            Conversación formateada
        """
        try:
            conv = self.db.get_conversation(conversation_id)
            messages = self.db.get_messages(conversation_id)
            
            if format == "json":
                import json
                data = {
                    'id': conv.id,
                    'title': conv.title,
                    'created_at': conv.created_at.isoformat(),
                    'messages': [
                        {'role': m.role, 'content': m.content, 'time': m.created_at.isoformat()}
                        for m in messages
                    ]
                }
                return json.dumps(data, indent=2, ensure_ascii=False)
            
            elif format == "txt":
                lines = [f"# {conv.title}", f"Created: {conv.created_at.isoformat()}", ""]
                for msg in messages:
                    lines.append(f"[{msg.role.upper()}]")
                    lines.append(msg.content)
                    lines.append("")
                return "\n".join(lines)
            
            else:
                return ""
        
        except Exception as e:
            logger.error(f"❌ Error exportando conversación: {e}")
            return ""


# Ejemplo de uso
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
    )
    
    db = DatabaseManager()
    storage = ConversationStorage(db)
    
    # Guardar conversación
    messages = [
        {'role': 'user', 'content': 'Hola'},
        {'role': 'assistant', 'content': 'Hola! ¿Cómo estás?'},
        {'role': 'user', 'content': 'Bien, gracias'}
    ]
    
    conv_id = storage.save_conversation("user1", "Chat Test", messages)
    print(f"\n✅ Conversación guardada: {conv_id}")
    
    # Listar conversaciones
    convs = storage.list_user_conversations("user1")
    print(f"\n📊 Conversaciones: {len(convs)}")
    
    # Obtener historial
    history = storage.get_conversation_history(conv_id)
    print(f"\n💬 Historial ({len(history)} mensajes):")
    for msg in history:
        print(f"  [{msg['role']}] {msg['content'][:50]}...")
