"""
Módulo de balanceo de carga para nodos distribuidos.
Permite decidir si una inferencia se procesa localmente o se delega a un nodo superior.
"""
from typing import Dict, Any

class LoadBalancer:
    def __init__(self, large_models=None):
        # Modelos considerados "grandes" que deben delegarse
        self.large_models = large_models or [
            "mistral-7b", "llama-13b", "llama-2-13b", "falcon-7b", "falcon-40b"
        ]

    def should_delegate(self, request: Dict[str, Any], is_coordinator: bool) -> bool:
        """
        Decide si la inferencia debe delegarse a un nodo superior.
        Args:
            request: Diccionario con los datos de la inferencia.
            is_coordinator: Si este nodo es el coordinador principal.
        Returns:
            True si debe delegarse, False si se procesa localmente.
        """
        model = request.get("model")
        gpu_index = request.get("gpu_index", 0)
        # Si no es coordinador y el modelo es grande o la GPU no es la principal, delega
        if not is_coordinator and (model in self.large_models or gpu_index != 0):
            return True
        return False
