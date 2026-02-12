"""
Health Checker - Verifica que todos los componentes estén sanos

Responsabilidad: Health checks periódicos de PC1 y PC2
retorna estado en /health endpoint
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class HealthStatus:
    """Estado de salud de componente"""
    name: str
    healthy: bool
    uptime_seconds: float
    last_check: str
    details: Dict[str, Any]
    
    def __repr__(self) -> str:
        status = "✅" if self.healthy else "❌"
        return f"{status} {self.name}: {self.details.get('message', '')}"


class HealthChecker:
    """Verificador de salud de sistema"""
    
    def __init__(self):
        """Inicializar checker"""
        self.start_time = datetime.now()
        self.last_check: Dict[str, HealthStatus] = {}
    
    def check_all(
        self,
        orchestrator=None,
        conversation_store=None,
        project_store=None,
        vector_index=None,
        embedding_engine=None
    ) -> Dict[str, Any]:
        """
        Ejecutar todos los health checks
        
        Args:
            orchestrator: Instancia de Orchestrator
            conversation_store: Instancia de ConversationStore
            project_store: Instancia de ProjectStore
            vector_index: Instancia de VectorIndex
            embedding_engine: Instancia de EmbeddingEngine
            
        Returns:
            {overall_healthy, components, timestamp}
        """
        statuses = []
        
        # Check Orchestrator
        if orchestrator:
            status = self._check_orchestrator(orchestrator)
            statuses.append(status)
            self.last_check['orchestrator'] = status
        
        # Check Conversation Store
        if conversation_store:
            status = self._check_conversation_store(conversation_store)
            statuses.append(status)
            self.last_check['conversation_store'] = status
        
        # Check Project Store
        if project_store:
            status = self._check_project_store(project_store)
            statuses.append(status)
            self.last_check['project_store'] = status
        
        # Check Vector Index
        if vector_index:
            status = self._check_vector_index(vector_index)
            statuses.append(status)
            self.last_check['vector_index'] = status
        
        # Check Embedding Engine
        if embedding_engine:
            status = self._check_embedding_engine(embedding_engine)
            statuses.append(status)
            self.last_check['embedding_engine'] = status
        
        # Resumen
        overall_healthy = all(s.healthy for s in statuses)
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        result = {
            'overall_healthy': overall_healthy,
            'uptime_seconds': uptime,
            'timestamp': datetime.now().isoformat(),
            'components': {
                s.name: {
                    'healthy': s.healthy,
                    'details': s.details,
                    'last_check': s.last_check
                }
                for s in statuses
            }
        }
        
        status_symbol = "✅" if overall_healthy else "⚠️"
        logger.info(f"{status_symbol} Health check completado: {len(statuses)} componentes")
        
        return result
    
    def _check_orchestrator(self, orchestrator) -> HealthStatus:
        """Check del orquestador"""
        try:
            status = orchestrator.get_status()
            return HealthStatus(
                name='orchestrator',
                healthy=True,
                uptime_seconds=status.get('uptime_seconds', 0),
                last_check=datetime.now().isoformat(),
                details={'message': 'Orchestrator activo', **status}
            )
        except Exception as e:
            return HealthStatus(
                name='orchestrator',
                healthy=False,
                uptime_seconds=0,
                last_check=datetime.now().isoformat(),
                details={'error': str(e)}
            )
    
    def _check_conversation_store(self, store) -> HealthStatus:
        """Check del conversation store"""
        try:
            stats = store.get_stats()
            return HealthStatus(
                name='conversation_store',
                healthy=True,
                uptime_seconds=0,
                last_check=datetime.now().isoformat(),
                details={
                    'message': 'Conversation store activo',
                    **stats
                }
            )
        except Exception as e:
            return HealthStatus(
                name='conversation_store',
                healthy=False,
                uptime_seconds=0,
                last_check=datetime.now().isoformat(),
                details={'error': str(e)}
            )
    
    def _check_project_store(self, store) -> HealthStatus:
        """Check del project store"""
        try:
            stats = store.get_stats()
            return HealthStatus(
                name='project_store',
                healthy=True,
                uptime_seconds=0,
                last_check=datetime.now().isoformat(),
                details={
                    'message': 'Project store activo',
                    **stats
                }
            )
        except Exception as e:
            return HealthStatus(
                name='project_store',
                healthy=False,
                uptime_seconds=0,
                last_check=datetime.now().isoformat(),
                details={'error': str(e)}
            )
    
    def _check_vector_index(self, index) -> HealthStatus:
        """Check del índice vectorial"""
        try:
            stats = index.get_stats()
            return HealthStatus(
                name='vector_index',
                healthy=True,
                uptime_seconds=0,
                last_check=datetime.now().isoformat(),
                details={
                    'message': f"Vector index con {stats['vector_count']} vectores",
                    **stats
                }
            )
        except Exception as e:
            return HealthStatus(
                name='vector_index',
                healthy=False,
                uptime_seconds=0,
                last_check=datetime.now().isoformat(),
                details={'error': str(e)}
            )
    
    def _check_embedding_engine(self, engine) -> HealthStatus:
        """Check del embedding engine"""
        try:
            stats = engine.get_stats()
            return HealthStatus(
                name='embedding_engine',
                healthy=stats.get('loaded', True),
                uptime_seconds=0,
                last_check=datetime.now().isoformat(),
                details={
                    'message': stats.get('status', 'Unknown'),
                    **stats
                }
            )
        except Exception as e:
            return HealthStatus(
                name='embedding_engine',
                healthy=False,
                uptime_seconds=0,
                last_check=datetime.now().isoformat(),
                details={'error': str(e)}
            )


# Health check endpoint (para FastAPI)
def get_health_endpoint(health_checker: HealthChecker, **components) -> Dict[str, Any]:
    """
    Función para usar en FastAPI
    
    @app.get("/health")
    def health():
        return get_health_endpoint(checker, orchestrator=orch, ...)
    """
    return health_checker.check_all(**components)
