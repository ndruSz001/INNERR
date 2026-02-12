"""
CORE Inference Engine - Motor de Inferencia PC1 (Nodo Cognitivo)

Responsabilidad: SOLO generación de texto/respuestas LLM
No maneja: documentos, indexación, embeddings

Backends soportados:
- llama.cpp: 4x más rápido (por defecto)
- Ollama: Inferencia alternativa
- Transformers: Fallback CPU
"""

try:
    from .inference_engine import InferenceEngine
    from .llm_backend import LlamaCppBackend
    from .ollama_backend import OllamaBackend
    from .transformers_backend import TransformersBackend
    
    __all__ = [
        "InferenceEngine",
        "LlamaCppBackend",
        "OllamaBackend",
        "TransformersBackend",
    ]
except ImportError as e:
    print(f"Warning: Could not import some backends: {e}")
    __all__ = []
