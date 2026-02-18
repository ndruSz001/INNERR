"""
Notification Service - Notificaciones por evento
Sprint 3 - FASE 9

Responsabilidad: Distribuir notificaciones
- Notificaciones por evento
- Suscriptores por tipo
- Queue de mensajes
- Entrega garantizada

Ejemplo de uso:
    from alerts.notification_service import NotificationService, EventType
    service = NotificationService()
    service.subscribe(EventType.USER_LOGIN, lambda n: print(n))
    service.notify(EventType.USER_LOGIN, {"user": "test"})
"""

import logging
import json
import uuid
from datetime import datetime
from typing import Dict, List, Callable, Optional, Any
from enum import Enum
from dataclasses import dataclass
from collections import defaultdict
import asyncio

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Tipos de eventos"""
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    CONVERSATION_CREATED = "conversation.created"
    CONVERSATION_DELETED = "conversation.deleted"
    MESSAGE_RECEIVED = "message.received"
    PROJECT_CREATED = "project.created"
    DOCUMENT_ADDED = "document.added"
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"


@dataclass
class Notification:
    """Notificación"""
    id: str
    event_type: EventType
    timestamp: datetime
    data: Dict[str, Any]
    delivered: bool = False
    retry_count: int = 0


class NotificationService:
    """Servicio centralizado de notificaciones"""
    
    def __init__(self, max_queue_size: int = 1000, max_retries: int = 3):
        """
        Args:
            max_queue_size: Tamaño máximo de la cola
            max_retries: Máximo de reintentos de entrega
        """
        self.queue: List[Notification] = []
        self.max_queue_size = max_queue_size
        self.max_retries = max_retries
        self.subscribers: Dict[EventType, List[Callable]] = defaultdict(list)
        self.notification_history: List[Notification] = []
        
        logger.info("✅ Notification Service inicializado")
    
    def subscribe(
        self,
        event_type: EventType,
        handler: Callable
    ) -> str:
        """
        Suscribir a un tipo de evento
        
        Args:
            event_type: Tipo de evento
            handler: Función manejadora
            
        Returns:
            ID de la suscripción
        """
        self.subscribers[event_type].append(handler)
        sub_id = f"sub-{uuid.uuid4()}"
        logger.info(f"✅ Suscriptor registrado: {sub_id} → {event_type.value}")
        return sub_id
    
    def unsubscribe(
        self,
        event_type: EventType,
        handler: Callable
    ) -> None:
        """
        Desuscribir de un tipo de evento
        
        Args:
            event_type: Tipo de evento
            handler: Función manejadora
        """
        if event_type in self.subscribers and handler in self.subscribers[event_type]:
            self.subscribers[event_type].remove(handler)
            logger.info(f"✅ Suscriptor removido: {event_type.value}")
    
    def emit(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        async_mode: bool = False
    ) -> str:
        """
        Emitir un evento
        
        Args:
            event_type: Tipo de evento
            data: Datos del evento
            async_mode: Entregar de forma asíncrona
            
        Returns:
            ID de la notificación
        """
        notification = Notification(
            id=f"notif-{uuid.uuid4()}",
            event_type=event_type,
            timestamp=datetime.now(),
            data=data
        )
        
        # Agregar a cola
        if len(self.queue) < self.max_queue_size:
            self.queue.append(notification)
        else:
            logger.warning("⚠️ Cola de notificaciones llena")
            return ""
        
        # Entregar
        if async_mode:
            # En producción: usar asyncio.create_task()
            self._deliver_async(notification)
        else:
            self._deliver_sync(notification)
        
        logger.info(f"📬 Evento emitido: {event_type.value}")
        return notification.id
    
    def _deliver_sync(self, notification: Notification) -> None:
        """Entregar notificación de forma síncrona"""
        handlers = self.subscribers.get(notification.event_type, [])
        
        for handler in handlers:
            try:
                handler(notification)
                notification.delivered = True
            except Exception as e:
                logger.error(f"❌ Error en handler: {e}")
                notification.retry_count += 1
    
    def _deliver_async(self, notification: Notification) -> None:
        """Entregar notificación de forma asíncrona (simulado)"""
        logger.info(f"🔄 Entrega asíncrona: {notification.id}")
        self._deliver_sync(notification)
    
    def retry_failed(self) -> int:
        """
        Reintentar entregas fallidas
        
        Returns:
            Número de notificaciones reentregadas
        """
        failed = [
            n for n in self.queue
            if not n.delivered and n.retry_count < self.max_retries
        ]
        
        for notification in failed:
            self._deliver_sync(notification)
        
        logger.info(f"🔄 {len(failed)} notificaciones reentregadas")
        return len(failed)
    
    def get_pending(self) -> List[Dict]:
        """
        Obtener notificaciones pendientes
        
        Returns:
            Lista de notificaciones sin entregar
        """
        pending = [n for n in self.queue if not n.delivered]
        
        return [
            {
                'id': n.id,
                'event_type': n.event_type.value,
                'timestamp': n.timestamp.isoformat(),
                'retry_count': n.retry_count
            }
            for n in pending
        ]
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """
        Obtener historial de notificaciones
        
        Args:
            limit: Número máximo de notificaciones
            
        Returns:
            Historial ordenado por timestamp
        """
        all_notifs = self.queue + self.notification_history
        sorted_notifs = sorted(all_notifs, key=lambda x: x.timestamp, reverse=True)
        
        return [
            {
                'id': n.id,
                'event_type': n.event_type.value,
                'timestamp': n.timestamp.isoformat(),
                'delivered': n.delivered,
                'data': n.data
            }
            for n in sorted_notifs[:limit]
        ]
    
    def cleanup_delivered(self) -> int:
        """
        Limpiar notificaciones entregadas
        
        Returns:
            Número de notificaciones movidas al historial
        """
        delivered = [n for n in self.queue if n.delivered]
        failed = [n for n in self.queue if not n.delivered and n.retry_count >= self.max_retries]
        
        moved = delivered + failed
        self.notification_history.extend(moved)
        self.queue = [n for n in self.queue if n not in moved]
        
        logger.info(f"🧹 {len(moved)} notificaciones archivadas")
        return len(moved)
    
    def get_stats(self) -> Dict:
        """
        Estadísticas del servicio
        
        Returns:
            Dict con métricas
        """
        delivered = sum(1 for n in self.queue if n.delivered)
        failed = sum(1 for n in self.queue if not n.delivered)
        
        return {
            'queue_size': len(self.queue),
            'pending': failed,
            'delivered': delivered,
            'subscribers': {
                event_type.value: len(handlers)
                for event_type, handlers in self.subscribers.items()
            },
            'history_size': len(self.notification_history)
        }


# Ejemplo de uso
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
    )
    
    service = NotificationService()
    
    # Crear handlers
    def on_message_received(notif):
        logger.info(f"📨 Mensaje recibido: {notif.data.get('message_id')}")
    
    def on_system_error(notif):
        logger.error(f"🚨 Error del sistema: {notif.data.get('error')}")
    
    # Suscribir
    service.subscribe(EventType.MESSAGE_RECEIVED, on_message_received)
    service.subscribe(EventType.SYSTEM_ERROR, on_system_error)
    
    # Emitir eventos
    service.emit(
        EventType.USER_LOGIN,
        {'user_id': 'user1', 'timestamp': datetime.now().isoformat()}
    )
    
    service.emit(
        EventType.MESSAGE_RECEIVED,
        {'message_id': 'msg-001', 'from_user': 'user1', 'content': 'Hola'}
    )
    
    service.emit(
        EventType.SYSTEM_ERROR,
        {'error': 'Connection timeout', 'service': 'PC2'}
    )
    
    # Estadísticas
    print("\n📊 Estadísticas:")
    print(json.dumps(service.get_stats(), indent=2))
    
    print("\n📋 Historial:")
    print(json.dumps(service.get_history(), indent=2, default=str))
