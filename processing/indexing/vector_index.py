"""
Vector Index - Índice vectorial con FAISS

Responsabilidad: Almacenar embeddings y búsqueda por similaridad
usando FAISS (Facebook AI Similarity Search).

Interfaz:
  add(id, embedding) → void
  search(embedding, top_k) → List[{id, score}]
  delete(id) → void
"""

from typing import List, Dict, Any, Optional, Tuple
import logging
import numpy as np
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class VectorIndex:
    """Índice vectorial con FAISS"""
    
    def __init__(self, dimension: int = 384, index_type: str = "flat"):
        """
        Args:
            dimension: Dimensión de embeddings (384 para all-MiniLM-L6-v2)
            index_type: "flat" (búsqueda exacta) o "hnsw" (aproximada, más rápida)
        """
        self.dimension = dimension
        self.index_type = index_type
        self.index = None
        self.id_to_metadata: Dict[int, Dict[str, Any]] = {}
        self.vector_count = 0
        
        self._initialize_index()
    
    def _initialize_index(self) -> None:
        """Inicializar índice FAISS"""
        try:
            import faiss
            
            if self.index_type == "flat":
                # Búsqueda exhaustiva (exacta, lenta para millones)
                self.index = faiss.IndexFlatL2(self.dimension)
            elif self.index_type == "hnsw":
                # Búsqueda aproximada (rápida, pero menos exacta)
                quantizer = faiss.IndexFlatL2(self.dimension)
                self.index = faiss.IndexHNSWFlat(quantizer, self.dimension, 32)
            else:
                raise ValueError(f"Unknown index type: {self.index_type}")
            
            logger.info(f"✅ FAISS index inicializado: {self.index_type}")
        
        except ImportError:
            logger.warning("⚠️ FAISS no instalado. Modo simulación.")
            logger.info("   Instala con: pip install faiss-cpu")
            self.index = None
    
    def add(
        self,
        embedding: np.ndarray,
        metadata: Dict[str, Any]
    ) -> int:
        """
        Agregar embedding al índice
        
        Args:
            embedding: Array numpy de 384 dimensiones
            metadata: {text, doc_id, title, ...}
            
        Returns:
            ID del vector en el índice
        """
        if not isinstance(embedding, np.ndarray):
            embedding = np.array(embedding, dtype=np.float32)
        
        # Asegurar float32 y shape correcto
        embedding = np.array(embedding, dtype=np.float32).reshape(1, -1)
        
        if self.index:
            try:
                self.index.add(embedding)
                vector_id = self.vector_count
                self.vector_count += 1
                
                # Guardar metadata
                self.id_to_metadata[vector_id] = metadata
                
                logger.debug(f"✅ Vector {vector_id} agregado")
                return vector_id
            
            except Exception as e:
                logger.error(f"❌ Error agregando vector: {e}")
                return -1
        
        else:
            # Simulación sin FAISS
            vector_id = self.vector_count
            self.vector_count += 1
            self.id_to_metadata[vector_id] = metadata
            return vector_id
    
    def search(
        self,
        embedding: np.ndarray,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Buscar vectores similares
        
        Args:
            embedding: Query embedding
            top_k: Número de resultados
            
        Returns:
            Lista de {id, distance, score, metadata}
        """
        if self.vector_count == 0:
            logger.warning("⚠️ Índice vacío")
            return []
        
        if not isinstance(embedding, np.ndarray):
            embedding = np.array(embedding, dtype=np.float32)
        
        embedding = np.array(embedding, dtype=np.float32).reshape(1, -1)
        
        if self.index:
            try:
                distances, indices = self.index.search(embedding, min(top_k, self.vector_count))
                
                results = []
                for i, (idx, distance) in enumerate(zip(indices[0], distances[0])):
                    if idx == -1:  # Índice inválido
                        continue
                    
                    score = 1.0 / (1.0 + distance)  # Convertir distancia a score
                    
                    result = {
                        'id': int(idx),
                        'distance': float(distance),
                        'score': float(score),
                        'metadata': self.id_to_metadata.get(int(idx), {})
                    }
                    results.append(result)
                
                return results
            
            except Exception as e:
                logger.error(f"❌ Error buscando: {e}")
                return []
        
        else:
            # Simulación: devolver IDs aleatorios
            logger.debug("⚠️ Búsqueda en modo simulación")
            results = []
            for i in range(min(top_k, self.vector_count)):
                results.append({
                    'id': i,
                    'distance': float(i * 0.1),
                    'score': float(1.0 - i * 0.1),
                    'metadata': self.id_to_metadata.get(i, {})
                })
            return results
    
    def delete(self, vector_id: int) -> bool:
        """
        Eliminar vector (FAISS no soporta borrado directo)
        
        Para Sprint 2, solo marca como eliminado
        """
        if vector_id in self.id_to_metadata:
            self.id_to_metadata[vector_id]['deleted'] = True
            logger.debug(f"Marcado como borrado: {vector_id}")
            return True
        return False
    
    def size(self) -> int:
        """Número de vectores en índice"""
        return self.vector_count
    
    def save(self, filepath: str) -> bool:
        """
        Guardar índice a disco
        
        Args:
            filepath: Ruta para guardar
            
        Returns:
            True si se guardó exitosamente
        """
        try:
            if self.index:
                import faiss
                faiss.write_index(self.index, str(filepath))
            
            # Guardar metadata como JSON
            metadata_path = Path(filepath).with_suffix('.json')
            with open(metadata_path, 'w') as f:
                # Convertir numpy arrays a listas para JSON
                meta_serializable = {}
                for k, v in self.id_to_metadata.items():
                    v_copy = v.copy()
                    if 'vector' in v_copy and isinstance(v_copy['vector'], np.ndarray):
                        v_copy['vector'] = v_copy['vector'].tolist()
                    meta_serializable[str(k)] = v_copy
                
                json.dump(meta_serializable, f, indent=2)
            
            logger.info(f"✅ Índice guardado en {filepath}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error guardando índice: {e}")
            return False
    
    def load(self, filepath: str) -> bool:
        """
        Cargar índice desde disco
        
        Args:
            filepath: Ruta del índice
            
        Returns:
            True si se cargó exitosamente
        """
        try:
            if self.index:
                import faiss
                self.index = faiss.read_index(str(filepath))
            
            # Cargar metadata
            metadata_path = Path(filepath).with_suffix('.json')
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    meta = json.load(f)
                    self.id_to_metadata = {int(k): v for k, v in meta.items()}
                    self.vector_count = max(self.id_to_metadata.keys()) + 1 if self.id_to_metadata else 0
            
            logger.info(f"✅ Índice cargado desde {filepath}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error cargando índice: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del índice"""
        return {
            'vector_count': self.vector_count,
            'dimension': self.dimension,
            'index_type': self.index_type,
            'has_faiss': self.index is not None,
            'metadata_count': len(self.id_to_metadata)
        }
