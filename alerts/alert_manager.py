"""
Alert Manager - Sistema centralizado de alertas
Sprint 3 - FASE 9

Responsabilidad: Gestionar alertas del sistema
- Sistema centralizado de alertas
- Crítico, Warning, Info, Debug
- Canales: email, slack, webhook
- Rate limiting
"""

import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Callable, Optional
from enum import Enum
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Niveles de alerta"""
    DEBUG = 0
    INFO = 1
    WARNING = 2
    CRITICAL = 3


class AlertChannel(Enum):
    """Canales de notificación"""
    LOG = "log"
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"


@dataclass
class Alert:
    """Alerta del sistema"""
    id: str
    timestamp: datetime
    level: AlertLevel
    title: str
    message: str
    source: str
    context: Dict
    sent: bool = False


class AlertManager:
    """Gestor centralizado de alertas"""
    
    def __init__(self, rate_limit_minutes: int = 5):
        """
        Args:
            rate_limit_minutes: Minutos entre alertas del mismo tipo
        """
        self.alerts: List[Alert] = []
        self.rate_limit_minutes = rate_limit_minutes
        self.handlers: Dict[AlertChannel, Callable] = {
            AlertChannel.LOG: self._handle_log,
            AlertChannel.EMAIL: self._handle_email,
            AlertChannel.SLACK: self._handle_slack,
            AlertChannel.WEBHOOK: self._handle_webhook
        }
        self.subscribers: Dict[AlertLevel, List[AlertChannel]] = {
            AlertLevel.DEBUG: [AlertChannel.LOG],
            AlertLevel.INFO: [AlertChannel.LOG],
            AlertLevel.WARNING: [AlertChannel.LOG, AlertChannel.SLACK],
            AlertLevel.CRITICAL: [AlertChannel.LOG, AlertChannel.EMAIL, AlertChannel.SLACK]
        }
        self.last_alert: Dict[str, datetime] = {}
        
        logger.info("✅ Alert Manager inicializado")
    
    def trigger_alert(
        self,
        level: AlertLevel,
        title: str,
        message: str,
        source: str = "system",
        context: Optional[Dict] = None
    ) -> str:
        """
        Disparar una alerta
        
        Args:
            level: Nivel de alerta
            title: Título
            message: Mensaje
            source: Fuente de la alerta
            context: Contexto adicional
            
        Returns:
            ID de la alerta
        """
        alert_key = f"{source}:{title}"
        
        # Rate limiting
        if alert_key in self.last_alert:
            time_since = datetime.now() - self.last_alert[alert_key]
            if time_since < timedelta(minutes=self.rate_limit_minutes):
                logger.debug(f"⏳ Alerta suprimida por rate limiting: {alert_key}")
                return ""
        
        alert_id = f"alert-{datetime.now().timestamp()}"
        alert = Alert(
            id=alert_id,
            timestamp=datetime.now(),
            level=level,
            title=title,
            message=message,
            source=source,
            context=context or {}
        )
        
        self.alerts.append(alert)
        self.last_alert[alert_key] = datetime.now()
        
        # Enviar a canales suscriptos
        for channel in self.subscribers.get(level, []):
            try:
                self.handlers[channel](alert)
                alert.sent = True
            except Exception as e:
                logger.error(f"❌ Error enviando alerta a {channel.value}: {e}")
        
        logger.info(f"🚨 Alerta {level.name}: {title}")
        return alert_id
    
    def _handle_log(self, alert: Alert) -> None:
        """Enviar alerta a logs"""
        log_func = {
            AlertLevel.DEBUG: logger.debug,
            AlertLevel.INFO: logger.info,
            AlertLevel.WARNING: logger.warning,
            AlertLevel.CRITICAL: logger.critical
        }.get(alert.level, logger.info)
        
        log_func(f"[{alert.source}] {alert.title}: {alert.message}")
    
    def _handle_email(self, alert: Alert) -> None:
        """Enviar alerta por email"""
        logger.info(f"📧 Email enviado (simulado): {alert.title}")
        # En producción: integrar con servicio de email
    
    def _handle_slack(self, alert: Alert) -> None:
        """Enviar alerta a Slack"""
        logger.info(f"💬 Slack enviado (simulado): {alert.title}")
        # En producción: integrar con Slack webhook
    
    def _handle_webhook(self, alert: Alert) -> None:
        """Enviar alerta a webhook"""
        logger.info(f"🔗 Webhook enviado (simulado): {alert.title}")
        # En producción: hacer POST a webhook configurado
    
    def subscribe(
        self,
        level: AlertLevel,
        channel: AlertChannel
    ) -> None:
        """
        Suscribir un canal a un nivel de alerta
        
        Args:
            level: Nivel de alerta
            channel: Canal de notificación
        """
        if level not in self.subscribers:
            self.subscribers[level] = []
        
        if channel not in self.subscribers[level]:
            self.subscribers[level].append(channel)
            logger.info(f"✅ Suscripción: {level.name} → {channel.value}")
    
    def unsubscribe(
        self,
        level: AlertLevel,
        channel: AlertChannel
    ) -> None:
        """
        Desuscribir un canal de un nivel
        
        Args:
            level: Nivel de alerta
            channel: Canal de notificación
        """
        if level in self.subscribers and channel in self.subscribers[level]:
            self.subscribers[level].remove(channel)
            logger.info(f"✅ Desuscripción: {level.name} ← {channel.value}")
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """
        Obtener alertas recientes
        
        Args:
            limit: Número máximo de alertas
            
        Returns:
            Lista de alertas recientes
        """
        return [
            {
                'id': a.id,
                'timestamp': a.timestamp.isoformat(),
                'level': a.level.name,
                'title': a.title,
                'message': a.message,
                'source': a.source
            }
            for a in sorted(self.alerts, key=lambda x: x.timestamp, reverse=True)[:limit]
        ]
    
    def get_alert_stats(self) -> Dict:
        """
        Estadísticas de alertas
        
        Returns:
            Dict con estadísticas
        """
        level_counts = {}
        for alert in self.alerts:
            level = alert.level.name
            level_counts[level] = level_counts.get(level, 0) + 1
        
        return {
            'total_alerts': len(self.alerts),
            'by_level': level_counts,
            'rate_limit_minutes': self.rate_limit_minutes
        }
    
    def clear_old_alerts(self, days: int = 7) -> int:
        """
        Limpiar alertas antiguas
        
        Args:
            days: Días de antigüedad para limpiar
            
        Returns:
            Número de alertas eliminadas
        """
        cutoff = datetime.now() - timedelta(days=days)
        old_count = len(self.alerts)
        
        self.alerts = [a for a in self.alerts if a.timestamp > cutoff]
        
        deleted = old_count - len(self.alerts)
        logger.info(f"🧹 {deleted} alertas antiguas eliminadas")
        
        return deleted


# Ejemplo de uso
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
    )
    
    manager = AlertManager()
    
    # Disparar alertas de diferentes niveles
    manager.trigger_alert(
        AlertLevel.INFO,
        "Sistema iniciado",
        "TARS está operacional"
    )
    
    manager.trigger_alert(
        AlertLevel.WARNING,
        "Memoria alta",
        "Uso de memoria en 75%",
        source="health_check"
    )
    
    manager.trigger_alert(
        AlertLevel.CRITICAL,
        "PC2 caído",
        "El nodo de procesamiento no responde",
        source="watchdog"
    )
    
    # Ver estadísticas
    print("\n📊 Estadísticas:")
    print(json.dumps(manager.get_alert_stats(), indent=2))
    
    print("\n📋 Alertas recientes:")
    print(json.dumps(manager.get_recent_alerts(), indent=2, default=str))
