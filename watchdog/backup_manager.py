"""
Backup Manager - Backup automático de índices
Sprint 3 - FASE 7

Responsabilidad: Garantizar recoverabilidad
- Backup automático de FAISS cada 6 horas
- Versionado de snapshots
- Restauración desde backups
- Compresión con gzip
- Limpieza automática de backups antiguos
"""

import os
import shutil
import gzip
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class BackupInfo:
    """Información sobre un backup"""
    name: str
    timestamp: datetime
    size_bytes: int
    compressed_size_bytes: int
    version: str
    file_path: str
    compressed: bool


class BackupManager:
    """Gestiona backups de índices y bases de datos"""
    
    def __init__(self, backup_dir: str = "/tmp/tars_backups", retention_days: int = 30):
        """
        Args:
            backup_dir: Directorio donde guardar backups
            retention_days: Días para mantener backups
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.retention_days = retention_days
        self.backups: Dict[str, List[BackupInfo]] = {}
        
        logger.info(f"✅ Backup Manager inicializado: {backup_dir}")
    
    def create_backup(
        self,
        source_path: str,
        backup_name: str,
        version: str = "1.0",
        compress: bool = True
    ) -> Optional[BackupInfo]:
        """
        Crear un backup de un archivo o directorio
        
        Args:
            source_path: Ruta del archivo/directorio a respaldar
            backup_name: Nombre del backup
            version: Versión del backup
            compress: Comprimir con gzip
            
        Returns:
            BackupInfo con detalles del backup
        """
        source = Path(source_path)
        
        if not source.exists():
            logger.error(f"❌ Fuente no existe: {source_path}")
            return None
        
        try:
            timestamp = datetime.now()
            backup_filename = f"{backup_name}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
            backup_path = self.backup_dir / backup_filename
            
            # Copiar archivo/directorio
            if source.is_file():
                shutil.copy2(source, backup_path)
                original_size = backup_path.stat().st_size
            else:
                shutil.copytree(source, backup_path)
                original_size = sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file())
            
            compressed_size = original_size
            
            # Comprimir si aplica
            if compress and source.is_file():
                compressed_path = Path(str(backup_path) + '.gz')
                with open(backup_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                backup_path.unlink()
                backup_path = compressed_path
                compressed_size = backup_path.stat().st_size
            
            backup_info = BackupInfo(
                name=backup_name,
                timestamp=timestamp,
                size_bytes=original_size,
                compressed_size_bytes=compressed_size,
                version=version,
                file_path=str(backup_path),
                compressed=compress
            )
            
            # Registrar backup
            if backup_name not in self.backups:
                self.backups[backup_name] = []
            self.backups[backup_name].append(backup_info)
            
            logger.info(
                f"✅ Backup creado: {backup_name} "
                f"({original_size} → {compressed_size} bytes)"
            )
            
            return backup_info
        
        except Exception as e:
            logger.error(f"❌ Error creando backup: {e}")
            return None
    
    def restore_backup(
        self,
        backup_name: str,
        restore_path: str,
        backup_index: int = -1
    ) -> bool:
        """
        Restaurar desde un backup
        
        Args:
            backup_name: Nombre del backup
            restore_path: Ruta donde restaurar
            backup_index: Índice del backup (-1 = más reciente)
            
        Returns:
            True si restauración exitosa
        """
        if backup_name not in self.backups or not self.backups[backup_name]:
            logger.error(f"❌ No hay backups para: {backup_name}")
            return False
        
        try:
            backup_list = self.backups[backup_name]
            backup_info = backup_list[backup_index]
            backup_path = Path(backup_info.file_path)
            
            if not backup_path.exists():
                logger.error(f"❌ Archivo de backup no existe: {backup_path}")
                return False
            
            # Descomprimir si aplica
            if backup_info.compressed:
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(restore_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(backup_path, restore_path)
            
            logger.info(f"✅ Backup restaurado: {backup_name} → {restore_path}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error restaurando backup: {e}")
            return False
    
    def list_backups(self, backup_name: Optional[str] = None) -> Dict:
        """
        Listar backups disponibles
        
        Args:
            backup_name: Nombre específico (None = todos)
            
        Returns:
            Dict con info de backups
        """
        if backup_name:
            if backup_name in self.backups:
                return {
                    backup_name: [asdict(b) for b in self.backups[backup_name]]
                }
            else:
                return {}
        
        return {
            name: [asdict(b) for b in backups]
            for name, backups in self.backups.items()
        }
    
    def cleanup_old_backups(self, days: Optional[int] = None) -> int:
        """
        Limpiar backups más antiguos que X días
        
        Args:
            days: Días (None = usar retention_days)
            
        Returns:
            Cantidad de backups eliminados
        """
        days = days or self.retention_days
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        for backup_name, backups in self.backups.items():
            remaining = []
            
            for backup_info in backups:
                if backup_info.timestamp < cutoff_date:
                    try:
                        Path(backup_info.file_path).unlink()
                        deleted_count += 1
                        logger.info(f"🗑️  Backup eliminado: {backup_info.name}")
                    except Exception as e:
                        logger.error(f"❌ Error eliminando backup: {e}")
                else:
                    remaining.append(backup_info)
            
            self.backups[backup_name] = remaining
        
        logger.info(f"🧹 {deleted_count} backups antiguos eliminados")
        return deleted_count
    
    def get_backup_stats(self) -> Dict:
        """
        Estadísticas de backups
        
        Returns:
            Dict con estadísticas
        """
        total_backups = sum(len(b) for b in self.backups.values())
        total_original_size = sum(
            b.size_bytes for backups in self.backups.values() for b in backups
        )
        total_compressed_size = sum(
            b.compressed_size_bytes for backups in self.backups.values() for b in backups
        )
        
        return {
            'total_backups': total_backups,
            'total_original_size_mb': total_original_size / (1024**2),
            'total_compressed_size_mb': total_compressed_size / (1024**2),
            'compression_ratio': (1 - total_compressed_size / max(total_original_size, 1)) * 100,
            'backup_groups': list(self.backups.keys())
        }


# Ejemplo de uso
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
    )
    
    manager = BackupManager()
    
    # Crear backup de ejemplo
    test_file = "/tmp/test_vector_index.faiss"
    with open(test_file, 'w') as f:
        f.write("dummy vector index data" * 1000)
    
    backup_info = manager.create_backup(
        source_path=test_file,
        backup_name="vector_index",
        compress=True
    )
    
    # Listar backups
    print("\n📊 Backups disponibles:")
    print(json.dumps(manager.list_backups(), indent=2, default=str))
    
    # Estadísticas
    print("\n📈 Estadísticas:")
    print(json.dumps(manager.get_backup_stats(), indent=2))
