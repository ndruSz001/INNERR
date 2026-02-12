"""
Watchdog Service - Monitorea y reinicia servicios
Sprint 3 - FASE 7

Responsabilidad: Garantizar que PC1 y PC2 estén siempre activos
- Verifica status de procesos cada 30s
- Reinicia automáticamente si caen
- Logging de crashes
- Alertas por email/webhook
"""

import subprocess
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)


@dataclass
class ProcessStatus:
    """Estado de un proceso"""
    name: str
    pid: Optional[int]
    running: bool
    uptime_seconds: float
    restart_count: int
    last_restart: datetime
    last_check: datetime


class WatchdogService:
    """Monitorea y reinicia servicios"""
    
    def __init__(self, check_interval: int = 30):
        """
        Args:
            check_interval: Segundos entre checks
        """
        self.check_interval = check_interval
        self.processes: Dict[str, Dict] = {}
        self.status: Dict[str, ProcessStatus] = {}
        self.running = False
        
        logger.info("✅ Watchdog Service inicializado")
    
    def register_process(
        self,
        name: str,
        command: str,
        restart_on_crash: bool = True,
        max_restarts: int = 5,
        restart_cooldown: int = 10
    ) -> None:
        """
        Registrar un proceso para monitorear
        
        Args:
            name: Nombre del proceso
            command: Comando para ejecutar
            restart_on_crash: Reiniciar si cae
            max_restarts: Máximo de reinicios antes de dar up
            restart_cooldown: Segundos entre reintentos
        """
        self.processes[name] = {
            'command': command,
            'restart_on_crash': restart_on_crash,
            'max_restarts': max_restarts,
            'restart_cooldown': restart_cooldown,
            'process': None,
            'restart_count': 0,
            'last_restart': None
        }
        
        logger.info(f"📋 Proceso registrado: {name}")
    
    def start_process(self, name: str) -> bool:
        """
        Iniciar un proceso registrado
        
        Args:
            name: Nombre del proceso
            
        Returns:
            True si inició correctamente
        """
        if name not in self.processes:
            logger.error(f"❌ Proceso no registrado: {name}")
            return False
        
        proc_config = self.processes[name]
        
        try:
            # Iniciar proceso
            process = subprocess.Popen(
                proc_config['command'],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            proc_config['process'] = process
            proc_config['last_restart'] = datetime.now()
            proc_config['restart_count'] += 1
            
            logger.info(f"✅ Proceso iniciado: {name} (PID: {process.pid})")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error iniciando {name}: {e}")
            return False
    
    def check_process(self, name: str) -> ProcessStatus:
        """
        Verificar status de un proceso
        
        Args:
            name: Nombre del proceso
            
        Returns:
            ProcessStatus con info actual
        """
        if name not in self.processes:
            return None
        
        proc_config = self.processes[name]
        process = proc_config['process']
        
        if process is None:
            running = False
            pid = None
            uptime = 0
        else:
            poll = process.poll()
            running = poll is None
            pid = process.pid if running else None
            
            if running and proc_config['last_restart']:
                uptime = (datetime.now() - proc_config['last_restart']).total_seconds()
            else:
                uptime = 0
        
        status = ProcessStatus(
            name=name,
            pid=pid,
            running=running,
            uptime_seconds=uptime,
            restart_count=proc_config['restart_count'],
            last_restart=proc_config['last_restart'],
            last_check=datetime.now()
        )
        
        self.status[name] = status
        return status
    
    def check_all_processes(self) -> Dict[str, ProcessStatus]:
        """
        Verificar todos los procesos
        
        Returns:
            Dict con status de cada proceso
        """
        for process_name in self.processes:
            status = self.check_process(process_name)
            
            if not status.running:
                logger.warning(f"⚠️ Proceso caído: {process_name}")
                
                proc_config = self.processes[process_name]
                if (proc_config['restart_on_crash'] and 
                    proc_config['restart_count'] < proc_config['max_restarts']):
                    
                    logger.info(f"🔄 Reiniciando {process_name}...")
                    self.start_process(process_name)
                else:
                    logger.error(f"❌ {process_name} excedió máximo de reinicios")
        
        return self.status
    
    def start_monitoring(self) -> None:
        """Iniciar loop de monitoreo"""
        self.running = True
        logger.info(f"🔍 Monitoreo iniciado (check cada {self.check_interval}s)")
        
        while self.running:
            try:
                self.check_all_processes()
                time.sleep(self.check_interval)
            
            except KeyboardInterrupt:
                logger.info("⏹️ Monitoreo detenido por usuario")
                break
            
            except Exception as e:
                logger.error(f"❌ Error en monitoreo: {e}")
                time.sleep(5)
    
    def stop_monitoring(self) -> None:
        """Detener monitoreo"""
        self.running = False
        logger.info("⏹️ Deteniendo monitoreo...")
    
    def get_status(self) -> str:
        """
        Obtener reporte de status
        
        Returns:
            JSON con status de todos los procesos
        """
        status_dict = {
            process_name: {
                'pid': status.pid,
                'running': status.running,
                'uptime_seconds': status.uptime_seconds,
                'restart_count': status.restart_count,
                'last_restart': status.last_restart.isoformat() if status.last_restart else None,
                'last_check': status.last_check.isoformat()
            }
            for process_name, status in self.status.items()
        }
        
        return json.dumps(status_dict, indent=2)


# Ejemplo de uso
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
    )
    
    watchdog = WatchdogService(check_interval=30)
    
    # Registrar procesos
    watchdog.register_process(
        name="PC1_Cognitivo",
        command="python3 orchestrator/main.py",
        restart_on_crash=True,
        max_restarts=5
    )
    
    watchdog.register_process(
        name="PC2_Procesamiento",
        command="python3 -m uvicorn api.main:app --port 8001",
        restart_on_crash=True,
        max_restarts=5
    )
    
    # Iniciar procesos
    for proc_name in watchdog.processes:
        watchdog.start_process(proc_name)
    
    # Comenzar monitoreo
    watchdog.start_monitoring()
