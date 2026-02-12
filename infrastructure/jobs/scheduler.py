"""
Job Scheduler - Ejecuta trabajos periódicos (nightly synthesis, etc)

Responsabilidad: Usar APScheduler para ejecutar jobs automáticamente
- Síntesis noctorna a las 02:00 AM
- Health checks cada 5 minutos
- Cleanup de datos cada 6 horas
"""

from typing import Optional, Callable, Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class JobScheduler:
    """Planificador de tareas con APScheduler"""
    
    def __init__(self):
        """Inicializar scheduler"""
        self.scheduler = BackgroundScheduler()
        self.jobs: Dict[str, Any] = {}
    
    def start(self) -> None:
        """Iniciar scheduler"""
        try:
            self.scheduler.start()
            logger.info("✅ Job scheduler iniciado")
        except Exception as e:
            logger.error(f"❌ Error iniciando scheduler: {e}")
    
    def stop(self) -> None:
        """Detener scheduler"""
        try:
            self.scheduler.shutdown(wait=False)
            logger.info("✅ Job scheduler detenido")
        except Exception as e:
            logger.error(f"❌ Error deteniendo scheduler: {e}")
    
    def add_job(
        self,
        func: Callable,
        trigger: str = "cron",
        job_id: Optional[str] = None,
        **trigger_args
    ) -> Optional[str]:
        """
        Agregar job al scheduler
        
        Args:
            func: Función a ejecutar
            trigger: "cron", "interval", etc
            job_id: ID único para el job
            **trigger_args: Argumentos para el trigger
            
        Returns:
            Job ID
            
        Ejemplos:
            # Síntesis cada noche a las 02:00
            add_job(nightly_job, trigger='cron', hour=2, minute=0)
            
            # Health check cada 5 minutos
            add_job(health_check, trigger='interval', minutes=5)
        """
        try:
            if trigger == "cron":
                cron_trigger = CronTrigger(**trigger_args)
                job = self.scheduler.add_job(
                    func,
                    cron_trigger,
                    id=job_id,
                    replace_existing=True
                )
            elif trigger == "interval":
                interval_trigger = IntervalTrigger(**trigger_args)
                job = self.scheduler.add_job(
                    func,
                    interval_trigger,
                    id=job_id,
                    replace_existing=True
                )
            else:
                raise ValueError(f"Unknown trigger: {trigger}")
            
            job_id = job.id
            self.jobs[job_id] = {
                'function': func.__name__,
                'trigger': trigger,
                'args': trigger_args,
                'created_at': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Job agregado: {job_id}")
            return job_id
        
        except Exception as e:
            logger.error(f"❌ Error agregando job: {e}")
            return None
    
    def remove_job(self, job_id: str) -> bool:
        """Remover job"""
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self.jobs:
                del self.jobs[job_id]
            logger.info(f"✅ Job removido: {job_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error removiendo job: {e}")
            return False
    
    def get_jobs(self) -> Dict[str, Any]:
        """Obtener lista de todos los jobs"""
        return self.jobs.copy()
    
    def get_job_info(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Obtener info de job específico"""
        return self.jobs.get(job_id)


# Funciones wrapper para jobs

def nightly_synthesis_job(
    conversation_store=None,
    project_store=None,
    embedding_engine=None,
    vector_index=None
) -> None:
    """
    Job de síntesis noctorna
    
    Se ejecuta automáticamente a las 02:00 AM
    """
    from infrastructure.jobs.nightly_synthesis import NightlySynthesisJob
    
    job = NightlySynthesisJob()
    result = job.execute(
        conversation_store=conversation_store,
        project_store=project_store,
        embedding_engine=embedding_engine,
        vector_index=vector_index
    )
    
    if result['success']:
        logger.info(f"✅ Nightly synthesis completa: {result['stats']}")
    else:
        logger.error(f"❌ Nightly synthesis falló")


def health_check_job(health_checker=None, **components) -> None:
    """
    Job de health check
    
    Se ejecuta cada 5 minutos
    """
    if health_checker:
        result = health_checker.check_all(**components)
        if result['overall_healthy']:
            logger.debug("✅ Health check: todos los sistemas OK")
        else:
            logger.warning("⚠️ Health check: algunos sistemas con problemas")


def cleanup_job(conversation_store=None, project_store=None) -> None:
    """
    Job de limpieza de datos antiguos
    
    Se ejecuta cada 6 horas
    """
    cleaned_conversations = 0
    cleaned_projects = 0
    
    if conversation_store:
        cleaned_conversations = conversation_store.clear_old(hours=48)
    
    if project_store:
        # En futuro: eliminar proyectos muy viejos
        pass
    
    total = cleaned_conversations + cleaned_projects
    logger.info(f"🗑️  Cleanup completado: {total} items eliminados")


# Factory para crear scheduler configurado

def create_configured_scheduler(
    nightly_job_func: Optional[Callable] = None,
    health_job_func: Optional[Callable] = None,
    cleanup_job_func: Optional[Callable] = None
) -> JobScheduler:
    """
    Crear scheduler pre-configurado con jobs estándar
    
    Args:
        nightly_job_func: Función para síntesis noctorna
        health_job_func: Función para health checks
        cleanup_job_func: Función para cleanup
        
    Returns:
        JobScheduler configurado y listo para iniciar
        
    Uso:
        scheduler = create_configured_scheduler()
        scheduler.start()
    """
    scheduler = JobScheduler()
    
    if nightly_job_func:
        scheduler.add_job(
            nightly_job_func,
            trigger='cron',
            job_id='nightly_synthesis',
            hour=2,
            minute=0
        )
    
    if health_job_func:
        scheduler.add_job(
            health_job_func,
            trigger='interval',
            job_id='health_check',
            minutes=5
        )
    
    if cleanup_job_func:
        scheduler.add_job(
            cleanup_job_func,
            trigger='interval',
            job_id='cleanup',
            hours=6
        )
    
    return scheduler
