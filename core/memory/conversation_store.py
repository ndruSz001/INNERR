"""
Conversation Store - Gestiona últimas 10 conversaciones activas (RAM)

Responsabilidad: Almacenar y recuperar conversaciones recientes
- Máximo 10 conversaciones activas por usuario
- Se limpian automáticamente después de 24 horas
- Metadata: timestamp, usuario, relaciones

NO almacena raw text largo, solo resúmenes + metadata
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid
import json


class ConversationStore:
    """Gestiona conversaciones activas en memoria (RAM)"""
    
    def __init__(self, max_conversations: int = 10, ttl_hours: int = 24):
        """
        Args:
            max_conversations: Máximo número de conversaciones por usuario
            ttl_hours: Time-to-live en horas
        """
        self.max_conversations = max_conversations
        self.ttl_hours = ttl_hours
        self.conversations: Dict[str, Dict[str, Any]] = {}  # {conversation_id: data}
        self.user_conversations: Dict[str, List[str]] = {}  # {user_id: [conv_ids]}
    
    def add_conversation(
        self,
        user_id: str,
        title: str,
        initial_message: Optional[str] = None
    ) -> str:
        """
        Crear nueva conversación
        
        Args:
            user_id: ID del usuario
            title: Título de la conversación
            initial_message: Mensaje inicial opcional
            
        Returns:
            ID de la conversación creada
        """
        conv_id = str(uuid.uuid4())
        
        self.conversations[conv_id] = {
            'id': conv_id,
            'user_id': user_id,
            'title': title,
            'created_at': datetime.now().isoformat(),
            'last_interaction': datetime.now().isoformat(),
            'messages': [initial_message] if initial_message else [],
            'metadata': {}
        }
        
        if user_id not in self.user_conversations:
            self.user_conversations[user_id] = []
        
        self.user_conversations[user_id].append(conv_id)
        
        # Limpiar conversaciones viejas si hay más de max
        self._cleanup_old_conversations(user_id)
        
        return conv_id
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener conversación por ID
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            Datos de conversación o None si no existe
        """
        return self.conversations.get(conversation_id)
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str
    ) -> bool:
        """
        Agregar mensaje a conversación
        
        Args:
            conversation_id: ID de la conversación
            role: "user" o "assistant"
            content: Contenido del mensaje
            
        Returns:
            True si fue agregado, False si conversación no existe
        """
        if conversation_id not in self.conversations:
            return False
        
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        self.conversations[conversation_id]['messages'].append(message)
        self.conversations[conversation_id]['last_interaction'] = datetime.now().isoformat()
        
        return True
    
    def list_conversations(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Listar conversaciones de usuario
        
        Args:
            user_id: ID del usuario
            limit: Máximo a retornar
            
        Returns:
            Lista de conversaciones ordenada por fecha
        """
        conv_ids = self.user_conversations.get(user_id, [])
        convs = [self.conversations[cid] for cid in conv_ids if cid in self.conversations]
        
        # Ordenar por last_interaction descendente
        convs.sort(
            key=lambda c: c['last_interaction'],
            reverse=True
        )
        
        return convs[:limit]
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Eliminar conversación
        
        Args:
            conversation_id: ID a eliminar
            
        Returns:
            True si fue eliminada, False si no existía
        """
        if conversation_id not in self.conversations:
            return False
        
        user_id = self.conversations[conversation_id]['user_id']
        del self.conversations[conversation_id]
        
        if user_id in self.user_conversations:
            self.user_conversations[user_id].remove(conversation_id)
        
        return True
    
    def clear_old(self, hours: Optional[int] = None) -> int:
        """
        Eliminar conversaciones más viejas que X horas
        
        Args:
            hours: Horas de antigüedad (si None, usa ttl_hours)
            
        Returns:
            Número de conversaciones eliminadas
        """
        if hours is None:
            hours = self.ttl_hours
        
        cutoff = datetime.now() - timedelta(hours=hours)
        deleted = 0
        
        conv_ids_to_delete = []
        for conv_id, conv in self.conversations.items():
            last_interaction = datetime.fromisoformat(conv['last_interaction'])
            if last_interaction < cutoff:
                conv_ids_to_delete.append(conv_id)
        
        for conv_id in conv_ids_to_delete:
            self.delete_conversation(conv_id)
            deleted += 1
        
        return deleted
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del store"""
        return {
            'total_conversations': len(self.conversations),
            'total_users': len(self.user_conversations),
            'avg_messages_per_conv': (
                sum(len(c.get('messages', [])) for c in self.conversations.values()) /
                max(1, len(self.conversations))
            ),
            'total_messages': sum(
                len(c.get('messages', [])) for c in self.conversations.values()
            )
        }
    
    def _cleanup_old_conversations(self, user_id: str) -> None:
        """Mantener máximo max_conversations por usuario"""
        if user_id not in self.user_conversations:
            return
        
        conv_ids = self.user_conversations[user_id]
        
        if len(conv_ids) > self.max_conversations:
            # Ordenar por fecha y eliminar las más viejas
            convs_with_dates = [
                (cid, self.conversations[cid]['last_interaction'])
                for cid in conv_ids
                if cid in self.conversations
            ]
            
            convs_with_dates.sort(key=lambda x: x[1])
            
            # Eliminar las más viejas
            for cid, _ in convs_with_dates[:-self.max_conversations]:
                self.delete_conversation(cid)
