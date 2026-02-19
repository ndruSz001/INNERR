"""
Módulo de caché distribuido para inferencias.
Permite almacenar y recuperar resultados de inferencia para evitar recomputación.
"""
from typing import Any, Dict, Optional
import threading
import hashlib
import json

class CacheManager:
    def __init__(self, persist_path: str = "cache_data.json"):
        # Simple caché en memoria (thread-safe) con persistencia opcional
        self._cache: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self.persist_path = persist_path
        self.load()
    def save(self):
        # Guarda el caché en disco (JSON)
        with self._lock:
            try:
                with open(self.persist_path, "w") as f:
                    json.dump(self._cache, f)
            except Exception:
                pass

    def load(self):
        # Carga el caché desde disco (JSON)
        try:
            with open(self.persist_path, "r") as f:
                self._cache = json.load(f)
        except Exception:
            self._cache = {}

    def _make_key(self, input_data: Dict[str, Any]) -> str:
        # Serializa y hashea los datos de entrada para obtener una clave única
        key_str = json.dumps(input_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()

    def get(self, input_data: Dict[str, Any]) -> Optional[Any]:
        key = self._make_key(input_data)
        with self._lock:
            return self._cache.get(key)

    def set(self, input_data: Dict[str, Any], result: Any):
        key = self._make_key(input_data)
        with self._lock:
            self._cache[key] = result
