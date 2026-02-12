"""
Logging Configuration - Configuración centralizada de logs

Responsabilidad: Logging uniforme en toda la aplicación
con rotation de archivos y múltiples niveles.
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
import sys


class LoggerConfig:
    """Configuración centralizada de logging"""
    
    def __init__(
        self,
        log_dir: str = "/tmp/tars_logs",
        level: str = "INFO",
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5
    ):
        """
        Args:
            log_dir: Directorio para logs
            level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_bytes: Tamaño máximo antes de rotar
            backup_count: Número de backups a mantener
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.level = getattr(logging, level.upper())
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.loggers = {}
    
    def get_logger(
        self,
        name: str,
        log_file: str = None
    ) -> logging.Logger:
        """
        Obtener logger configurado
        
        Args:
            name: Nombre del logger (ej: __name__)
            log_file: Archivo específico para este logger
            
        Returns:
            Logger configurado
        """
        if name in self.loggers:
            return self.loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(self.level)
        logger.propagate = True
        
        # Remover handlers anteriores
        logger.handlers.clear()
        
        # Formato
        formatter = logging.Formatter(
            '%(asctime)s [%(name)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler a stdout
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Handler a archivo
        if not log_file:
            log_file = f"{name.replace('.', '_')}.log"
        
        log_path = self.log_dir / log_file
        
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                log_path,
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(self.level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"⚠️ No se pudo crear handler a archivo: {e}")
        
        self.loggers[name] = logger
        return logger


# Instancia global
_logger_config: LoggerConfig = None


def init_logging(
    log_dir: str = "/tmp/tars_logs",
    level: str = "INFO"
) -> LoggerConfig:
    """
    Inicializar sistema de logging global
    
    Debe llamarse una sola vez al inicio
    
    Args:
        log_dir: Directorio para logs
        level: Nivel mínimo de logging
        
    Returns:
        Instancia de LoggerConfig
    """
    global _logger_config
    _logger_config = LoggerConfig(log_dir=log_dir, level=level)
    return _logger_config


def get_logger(name: str) -> logging.Logger:
    """
    Obtener logger (debe llamarse después de init_logging)
    
    Args:
        name: Nombre del logger (típicamente __name__)
        
    Returns:
        Logger configurado
    """
    global _logger_config
    if _logger_config is None:
        init_logging()
    
    return _logger_config.get_logger(name)


# Config para diferentes módulos
def get_module_logger(module_name: str) -> logging.Logger:
    """Obtener logger para módulo específico"""
    return get_logger(module_name)
