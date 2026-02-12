"""
Inference Engine - Motor de Inferencia PC1

Responsabilidad ÚNICA: Generar texto/respuestas LLM

No maneja:
- Documentos/PDFs
- Indexación/embeddings
- Búsquedas semánticas
- Memoria a largo plazo

Solo orquesta backends y procesa respuestas.
"""

from typing import Optional, Dict, List
import json
from enum import Enum


class Backend(Enum):
    LLAMA_CPP = "llama_cpp"
    OLLAMA = "ollama"
    TRANSFORMERS = "transformers"


class InferenceEngine:
    """
    Motor de inferencia que decide qué backend usar.
    Prioridad: llama.cpp > Ollama > Transformers
    """
    
    def __init__(self, config: Dict = None):
        """
        Inicializa el motor.
        
        Args:
            config: {
                'use_llama_cpp': bool,
                'use_ollama': bool,
                'use_transformers': bool,
                'llama_cpp_path': str,
                'ollama_model': str,
                'transformers_model': str,
                'device': str,  # 'cuda' o 'cpu'
            }
        """
        self.config = config or {}
        self.backends: Dict[Backend, any] = {}
        self.active_backend: Optional[Backend] = None
        
        self._initialize_backends()
    
    def _initialize_backends(self) -> None:
        """Inicializa los backends disponibles."""
        # Intentar cargar en orden de preferencia
        if self.config.get('use_llama_cpp', True):
            try:
                from .llm_backend import LlamaCppBackend
                self.backends[Backend.LLAMA_CPP] = LlamaCppBackend(
                    self.config.get('llama_cpp_path')
                )
                self.active_backend = Backend.LLAMA_CPP
                print("✅ llama.cpp backend initialized")
            except Exception as e:
                print(f"⚠️  llama.cpp backend failed: {e}")
        
        if self.config.get('use_ollama', True) and self.active_backend is None:
            try:
                from .ollama_backend import OllamaBackend
                self.backends[Backend.OLLAMA] = OllamaBackend(
                    self.config.get('ollama_model', 'llama3')
                )
                self.active_backend = Backend.OLLAMA
                print("✅ Ollama backend initialized")
            except Exception as e:
                print(f"⚠️  Ollama backend failed: {e}")
        
        if self.config.get('use_transformers', True) and self.active_backend is None:
            try:
                from .transformers_backend import TransformersBackend
                self.backends[Backend.TRANSFORMERS] = TransformersBackend(
                    self.config.get('transformers_model', 'microsoft/phi-2'),
                    device=self.config.get('device', 'cuda')
                )
                self.active_backend = Backend.TRANSFORMERS
                print("✅ Transformers backend initialized")
            except Exception as e:
                print(f"⚠️  Transformers backend failed: {e}")
    
    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        context: List[str] = None,
        max_tokens: int = 200,
        temperature: float = 0.8,
        user_id: str = "default"
    ) -> str:
        """
        Genera respuesta usando el backend disponible.
        
        Args:
            prompt: Pregunta del usuario
            system_prompt: Instrucciones del sistema (personalidad, contexto)
            context: Lista de fragmentos de contexto
            max_tokens: Máximo de tokens a generar
            temperature: Creatividad (0.0-1.0)
            user_id: Identificador del usuario (para tracking)
        
        Returns:
            Respuesta generada
        """
        if not self.active_backend:
            return "❌ No backends available. Install llama.cpp, Ollama, or Transformers."
        
        try:
            backend = self.backends[self.active_backend]
            
            # Construir prompt completo
            full_prompt = self._build_prompt(prompt, system_prompt, context)
            
            # Generar respuesta
            response = backend.generate(
                full_prompt=full_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.strip()
        
        except Exception as e:
            print(f"❌ Generation error with {self.active_backend.value}: {e}")
            return self._fallback_generate(prompt, system_prompt, context, max_tokens)
    
    def _build_prompt(
        self,
        prompt: str,
        system_prompt: str,
        context: List[str] = None
    ) -> str:
        """
        Construye el prompt completo con contexto.
        
        Formato:
        ```
        [System prompt]
        
        [Context fragments]
        
        User: [prompt]
        TARS:
        ```
        """
        parts = []
        
        if system_prompt:
            parts.append(system_prompt)
        
        if context:
            context_text = "\n".join(context)
            parts.append(f"Context:\n{context_text}")
        
        parts.append(f"User: {prompt}")
        parts.append("TARS:")
        
        return "\n\n".join(parts)
    
    def _fallback_generate(
        self,
        prompt: str,
        system_prompt: str,
        context: List[str],
        max_tokens: int
    ) -> str:
        """
        Fallback si el backend activo falla.
        Intenta el siguiente en la cadena de prioridad.
        """
        # Intentar con otro backend
        for backend_type in [Backend.OLLAMA, Backend.TRANSFORMERS]:
            if backend_type in self.backends and backend_type != self.active_backend:
                try:
                    self.active_backend = backend_type
                    backend = self.backends[backend_type]
                    
                    full_prompt = self._build_prompt(prompt, system_prompt, context)
                    response = backend.generate(
                        full_prompt=full_prompt,
                        max_tokens=max_tokens,
                        temperature=0.8
                    )
                    
                    return response.strip()
                except Exception as e:
                    print(f"⚠️  Fallback {backend_type.value} also failed: {e}")
                    continue
        
        # Respuesta por defecto si todo falla
        return "Lo siento, tengo problemas procesando eso en este momento."
    
    def get_active_backend(self) -> str:
        """Retorna el nombre del backend activo."""
        return self.active_backend.value if self.active_backend else "none"
    
    def list_available_backends(self) -> List[str]:
        """Retorna lista de backends disponibles."""
        return [b.value for b in self.backends.keys()]
    
    def benchmark(self) -> Dict[str, float]:
        """
        Compara velocidad de backends.
        
        Returns:
            {'backend_name': latency_seconds, ...}
        """
        test_prompt = "¿Cuál es tu nombre? Responde en 2 palabras."
        results = {}
        
        import time
        
        for backend_type, backend in self.backends.items():
            try:
                start = time.time()
                backend.generate(test_prompt, max_tokens=50)
                latency = time.time() - start
                results[backend_type.value] = latency
            except Exception as e:
                results[backend_type.value] = None
        
        return results
