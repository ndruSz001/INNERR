"""
Módulo de métricas y monitoreo para nodos distribuidos.
Permite recolectar y exponer métricas básicas del sistema.
"""
from typing import Dict
import threading
import time

class MetricsManager:
    def __init__(self):
        self._lock = threading.Lock()
        self.metrics = {
            "inference_requests_total": 0,
            "inference_latency_sum": 0.0,
            "inference_latency_count": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0
        }

    def record_inference(self, latency: float):
        with self._lock:
            self.metrics["inference_requests_total"] += 1
            self.metrics["inference_latency_sum"] += latency
            self.metrics["inference_latency_count"] += 1

    def record_cache_hit(self):
        with self._lock:
            self.metrics["cache_hits"] += 1

    def record_cache_miss(self):
        with self._lock:
            self.metrics["cache_misses"] += 1

    def record_error(self):
        with self._lock:
            self.metrics["errors"] += 1

    def get_metrics(self) -> Dict[str, float]:
        with self._lock:
            return dict(self.metrics)

    def prometheus_format(self) -> str:
        # Exponer métricas en formato Prometheus
        lines = []
        for k, v in self.get_metrics().items():
            lines.append(f"# TYPE {k} counter")
            lines.append(f"{k} {v}")
        return "\n".join(lines)
