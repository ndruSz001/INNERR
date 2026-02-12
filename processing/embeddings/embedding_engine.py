"""
Embedding Engine - Genera embeddings vectoriales de texto

Responsabilidad: Convertir chunks de texto en vectores densos
usando Sentence Transformers (all-MiniLM-L6-v2).

Interfaz:
  embed_text(text) → List[float]  # Vector 384-dim
  embed_batch(texts) → List[List[float]]
"""

from typing import List, Optional, Dict, Any
import logging
import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Embedding:
    """Un embedding vectorial"""
    text: str
    vector: np.ndarray  # 384 dimensiones
    length: int
    model: str = "all-MiniLM-L6-v2"


class EmbeddingEngine:
    """Motor de embeddings usando Sentence Transformers"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Args:
            model_name: Nombre del modelo (todos de sentence-transformers)
        """
        self.model_name = model_name
        self.model = None
        self.loaded = False
        self.embedding_dim = 384  # Dimensión de all-MiniLM-L6-v2
        
        self._load_model()
    
    def _load_model(self) -> bool:
        """Cargar modelo de Sentence Transformers"""
        try:
            # En producción, descomenta:
            # from sentence_transformers import SentenceTransformer
            # self.model = SentenceTransformer(self.model_name)
            
            # En sprint 2 sin dependencias, simulamos:
            logger.warning(
                "⚠️ Sentence Transformers no instalado. Modo simulación."
            )
            logger.info(
                "   Instala con: pip install sentence-transformers"
            )
            self.model = None
            self.loaded = False
            return False
            
        except Exception as e:
            logger.error(f"❌ Error cargando modelo: {e}")
            self.model = None
            self.loaded = False
            return False
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generar embedding de un texto
        
        Args:
            text: Texto a embedear
            
        Returns:
            Array numpy de 384 dimensiones
        """
        if not text or len(text) < 3:
            # Embedding vacío
            return np.zeros(self.embedding_dim, dtype=np.float32)
        
        if self.loaded and self.model:
            # Usar modelo real
            try:
                embedding = self.model.encode(text)
                return np.array(embedding, dtype=np.float32)
            except Exception as e:
                logger.error(f"❌ Error embedeando: {e}")
                return np.zeros(self.embedding_dim, dtype=np.float32)
        
        else:
            # Simulación: generar embedding fake basado en hash
            # Para tests, es suficiente
            np.random.seed(hash(text) % (2**31))
            return np.random.randn(self.embedding_dim).astype(np.float32)
    
    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generar embeddings para múltiples textos
        
        Args:
            texts: Lista de textos
            
        Returns:
            Lista de arrays numpy
        """
        if not self.loaded or not self.model:
            # Simulación
            return [self.embed_text(t) for t in texts]
        
        try:
            embeddings = self.model.encode(texts, show_progress_bar=False)
            return [np.array(e, dtype=np.float32) for e in embeddings]
        except Exception as e:
            logger.error(f"❌ Error en batch embed: {e}")
            return [self.embed_text(t) for t in texts]
    
    def get_embedding_dimension(self) -> int:
        """Obtener dimensión de embeddings"""
        return self.embedding_dim
    
    def similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Calcular similaridad coseno entre dos embeddings
        
        Args:
            emb1: Primer embedding
            emb2: Segundo embedding
            
        Returns:
            Score de -1 a 1 (1 = idénticos)
        """
        # Normalizar
        emb1_norm = emb1 / (np.linalg.norm(emb1) + 1e-8)
        emb2_norm = emb2 / (np.linalg.norm(emb2) + 1e-8)
        
        # Similitud coseno
        return float(np.dot(emb1_norm, emb2_norm))
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del engine"""
        return {
            'model': self.model_name,
            'dimension': self.embedding_dim,
            'loaded': self.loaded,
            'status': '✅ Ready' if self.loaded else '⚠️ Simulation mode'
        }


class EmbeddingCache:
    """Cache simple de embeddings para evitar recalcular"""
    
    def __init__(self, max_size: int = 10000):
        """
        Args:
            max_size: Máximo número de embeddings en cache
        """
        self.max_size = max_size
        self.cache: Dict[str, np.ndarray] = {}
    
    def get(self, text: str) -> Optional[np.ndarray]:
        """Obtener embedding del cache"""
        return self.cache.get(text)
    
    def set(self, text: str, embedding: np.ndarray) -> None:
        """Guardar embedding en cache"""
        if len(self.cache) >= self.max_size:
            # Limpiar mitad del cache
            keys_to_delete = list(self.cache.keys())[:self.max_size // 2]
            for k in keys_to_delete:
                del self.cache[k]
        
        self.cache[text] = embedding
    
    def clear(self) -> None:
        """Limpiar cache"""
        self.cache.clear()
    
    def size(self) -> int:
        """Tamaño actual del cache"""
        return len(self.cache)
