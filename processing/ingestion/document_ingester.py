"""
Document Ingester - Procesa y limpia documentos para indexación

Responsabilidad: Tomar documentos crudos (PDF, TXT, etc.)
y convertirlos en texto limpio listo para embeddings.

Interfaz simple:
  ingest(document) → {text, metadata, chunks}
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ProcessedDocument:
    """Documento procesado listo para embeddings"""
    text: str
    metadata: Dict[str, Any]
    chunks: List[str]  # Texto dividido en chunks
    chunk_size: int = 512


class DocumentIngester:
    """Ingesta y limpia documentos"""
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        min_length: int = 10
    ):
        """
        Args:
            chunk_size: Tamaño de chunks en caracteres
            chunk_overlap: Solapamiento entre chunks
            min_length: Longitud mínima de texto válido
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_length = min_length
    
    def ingest(
        self,
        text: str,
        title: Optional[str] = None,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[ProcessedDocument]:
        """
        Procesar documento
        
        Args:
            text: Texto crudo
            title: Título del documento
            source: Fuente del documento
            metadata: Metadatos adicionales
            
        Returns:
            ProcessedDocument o None si texto no válido
        """
        # Limpiar
        cleaned = self._clean_text(text)
        
        if len(cleaned) < self.min_length:
            logger.warning(f"⚠️ Documento demasiado corto: {len(cleaned)} chars")
            return None
        
        # Dividir en chunks
        chunks = self._create_chunks(cleaned)
        
        if not chunks:
            logger.warning("⚠️ No se crearon chunks")
            return None
        
        # Metadatos
        meta = metadata or {}
        meta.update({
            'title': title or 'Sin título',
            'source': source or 'desconocida',
            'ingested_at': datetime.now().isoformat(),
            'char_count': len(cleaned),
            'chunk_count': len(chunks)
        })
        
        result = ProcessedDocument(
            text=cleaned,
            metadata=meta,
            chunks=chunks,
            chunk_size=self.chunk_size
        )
        
        logger.info(
            f"✅ Documento procesado: {meta['title']} "
            f"({len(cleaned)} chars, {len(chunks)} chunks)"
        )
        
        return result
    
    def _clean_text(self, text: str) -> str:
        """Limpiar texto (remover espacios extras, etc)"""
        
        # Remover caracteres de control
        text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
        
        # Normalizar espacios en blanco
        text = re.sub(r'\s+', ' ', text)
        
        # Remover espacios al principio y final
        text = text.strip()
        
        return text
    
    def _create_chunks(self, text: str) -> List[str]:
        """Dividir texto en chunks con overlap"""
        
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk = text[start:end]
            
            chunks.append(chunk)
            
            # Mover por chunk_size - overlap
            start += self.chunk_size - self.chunk_overlap
        
        return chunks
    
    def batch_ingest(
        self,
        documents: List[Tuple[str, Optional[str]]]  # (text, title)
    ) -> List[ProcessedDocument]:
        """
        Procesar lote de documentos
        
        Args:
            documents: Lista de (texto, título)
            
        Returns:
            Lista de ProcessedDocument válidos
        """
        results = []
        
        for i, (text, title) in enumerate(documents, 1):
            result = self.ingest(text, title=title)
            if result:
                results.append(result)
            
            if i % 10 == 0:
                logger.debug(f"   Procesados {i} documentos...")
        
        logger.info(f"✅ Procesados {len(results)}/{len(documents)} documentos")
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de ingesta"""
        return {
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'min_length': self.min_length
        }


# ========== Helpers para leer diferentes formatos ==========

def read_text_file(filepath: str) -> str:
    """Leer archivo de texto"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"❌ Error leyendo {filepath}: {e}")
        return ""


def read_multiple_files(directory: str) -> List[Tuple[str, str]]:
    """Leer múltiples archivos de un directorio"""
    import os
    from pathlib import Path
    
    results = []
    
    for filepath in Path(directory).glob('*.txt'):
        text = read_text_file(str(filepath))
        if text:
            results.append((text, filepath.stem))
    
    return results
