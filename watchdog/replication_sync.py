"""
Replication Sync - Sincroniza índices entre PCs
Sprint 3 - FASE 7

Responsabilidad: Mantener replicas sincronizadas
- Sincroniza índices entre PC2 → PC3/PC4
- Detección de cambios (delta sync)
- Sincronización bidireccional
- Versionado de cambios
"""

import hashlib
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class FileChecksum:
    """Checksum de un archivo"""
    file_path: str
    size: int
    hash: str
    timestamp: datetime


class ReplicationSync:
    """Sincroniza datos entre nodos"""
    
    def __init__(self, chunk_size: int = 1024 * 1024):  # 1MB chunks
        """
        Args:
            chunk_size: Tamaño de chunks para sincronización
        """
        self.chunk_size = chunk_size
        self.checksum_cache: Dict[str, FileChecksum] = {}
        self.last_sync: Dict[str, datetime] = {}
        
        logger.info("✅ Replication Sync inicializado")
    
    def calculate_file_checksum(self, file_path: str) -> str:
        """
        Calcular SHA256 de un archivo
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Hash hexadecimal
        """
        hash_obj = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
        
        except Exception as e:
            logger.error(f"❌ Error calculando checksum: {e}")
            return ""
    
    def detect_changes(
        self,
        source_dir: str,
        target_dir: str
    ) -> Dict[str, List[str]]:
        """
        Detectar qué archivos han cambiado
        
        Args:
            source_dir: Directorio fuente
            target_dir: Directorio destino
            
        Returns:
            {
                'added': [files],
                'modified': [files],
                'deleted': [files]
            }
        """
        source_path = Path(source_dir)
        target_path = Path(target_dir)
        
        source_files = {f.name: f for f in source_path.rglob('*') if f.is_file()}
        target_files = {f.name: f for f in target_path.rglob('*') if f.is_file()}
        
        changes = {
            'added': [],
            'modified': [],
            'deleted': []
        }
        
        # Detectar nuevos y modificados
        for filename, source_file in source_files.items():
            if filename not in target_files:
                changes['added'].append(filename)
            else:
                source_hash = self.calculate_file_checksum(str(source_file))
                target_hash = self.calculate_file_checksum(str(target_files[filename]))
                
                if source_hash != target_hash:
                    changes['modified'].append(filename)
        
        # Detectar eliminados
        for filename in target_files:
            if filename not in source_files:
                changes['deleted'].append(filename)
        
        logger.info(
            f"🔍 Cambios detectados: "
            f"+{len(changes['added'])} "
            f"~{len(changes['modified'])} "
            f"-{len(changes['deleted'])}"
        )
        
        return changes
    
    def sync_files(
        self,
        source_dir: str,
        target_dir: str,
        changes: Optional[Dict[str, List[str]]] = None
    ) -> bool:
        """
        Sincronizar cambios detectados
        
        Args:
            source_dir: Directorio fuente
            target_dir: Directorio destino
            changes: Dict de cambios (None = detectar automáticamente)
            
        Returns:
            True si sincronización exitosa
        """
        source_path = Path(source_dir)
        target_path = Path(target_dir)
        
        if changes is None:
            changes = self.detect_changes(source_dir, target_dir)
        
        try:
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Copiar nuevos y modificados
            for filename in changes['added'] + changes['modified']:
                source_file = source_path / filename
                target_file = target_path / filename
                
                if source_file.exists():
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    import shutil
                    shutil.copy2(source_file, target_file)
                    logger.info(f"📤 Sincronizado: {filename}")
            
            # Eliminar archivos que ya no existen
            for filename in changes['deleted']:
                target_file = target_path / filename
                if target_file.exists():
                    target_file.unlink()
                    logger.info(f"🗑️  Eliminado: {filename}")
            
            self.last_sync[target_dir] = datetime.now()
            logger.info(f"✅ Sincronización completada: {source_dir} → {target_dir}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error sincronizando: {e}")
            return False
    
    def bidirectional_sync(
        self,
        dir1: str,
        dir2: str,
        conflict_strategy: str = "source_wins"
    ) -> bool:
        """
        Sincronizar bidireccional entre dos directorios
        
        Args:
            dir1: Primer directorio
            dir2: Segundo directorio
            conflict_strategy: 'source_wins' o 'target_wins'
            
        Returns:
            True si sincronización exitosa
        """
        try:
            logger.info(f"🔄 Sincronización bidireccional: {dir1} ↔ {dir2}")
            
            # Dir1 → Dir2
            changes1 = self.detect_changes(dir1, dir2)
            self.sync_files(dir1, dir2, changes1)
            
            # Dir2 → Dir1 (solo si no hay conflictos o strategy específica)
            changes2 = self.detect_changes(dir2, dir1)
            if conflict_strategy == "source_wins":
                # No sobrescribir cambios en dir1
                changes2['modified'] = [
                    f for f in changes2['modified'] 
                    if f not in changes1['added'] + changes1['modified']
                ]
            
            self.sync_files(dir2, dir1, changes2)
            
            logger.info("✅ Sincronización bidireccional completada")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error en sincronización bidireccional: {e}")
            return False
    
    def get_sync_status(self) -> Dict:
        """
        Obtener estado de sincronizaciones
        
        Returns:
            Dict con info de últimas sincronizaciones
        """
        return {
            'last_syncs': {
                dir: sync_time.isoformat()
                for dir, sync_time in self.last_sync.items()
            },
            'total_syncs': len(self.last_sync)
        }
    
    
                ## Bloque de pruebas eliminado para producción
    
    def create_manifest(self, directory: str) -> str:
        """
        Crear manifest de todos los archivos
        
        Args:
            directory: Directorio a documentar
            
        Returns:
            JSON con manifest
        """
        dir_path = Path(directory)
        manifest = {}
        
        for file_path in dir_path.rglob('*'):
            if file_path.is_file():
                rel_path = file_path.relative_to(dir_path)
                manifest[str(rel_path)] = {
                    'size': file_path.stat().st_size,
                    'hash': self.calculate_file_checksum(str(file_path)),
                    'modified': datetime.fromtimestamp(
                        file_path.stat().st_mtime
                    ).isoformat()
                }
        
        return json.dumps(manifest, indent=2)


# Ejemplo de uso
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
    )
    
    sync = ReplicationSync()
    
    # Crear directorios de prueba
    import tempfile
    import shutil
    
    with tempfile.TemporaryDirectory() as tmpdir:
        source = Path(tmpdir) / "source"
        target = Path(tmpdir) / "target"
        
        source.mkdir()
        (source / "file1.txt").write_text("content1")
        (source / "file2.txt").write_text("content2")
        
        # Sync
        sync.sync_files(str(source), str(target))
        
        # Realizar cambios
        (source / "file1.txt").write_text("modified content1")
        (source / "file3.txt").write_text("new file")
        
        # Detectar cambios
        changes = sync.detect_changes(str(source), str(target))
        print(f"\n📊 Cambios detectados: {json.dumps(changes, indent=2)}")
        
        # Sync nuevamente
        sync.sync_files(str(source), str(target))
