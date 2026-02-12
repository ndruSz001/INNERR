"""
LLM Backend - llama.cpp wrapper
Backend ultrarrápido usando llama.cpp

Responsabilidad ÚNICA: generar texto usando llama.cpp
Sin dependencias cruzadas con otros módulos TARS.
"""

from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class LlamaCppBackend:
    """Backend ultrarrápido usando llama.cpp (C++ bindings)"""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Inicializa el backend llama.cpp.
        
        Args:
            model_path: Ruta al modelo GGUF 
                       (ej: models/Phi-2-gguf/model.gguf)
        
        Raises:
            ImportError: Si llama-cpp-python no está instalado
            RuntimeError: Si el modelo no se puede cargar
        """
        self.model_path = model_path
        self.llm = None
        self.loaded = False
        
        if model_path:
            self._load_model(model_path)
        else:
            logger.info("⚠️  LlamaCppBackend inicializado sin modelo")
    
    def _load_model(self, model_path: str) -> None:
        """
        Carga el modelo GGUF usando llama.cpp.
        
        Args:
            model_path: Ruta al archivo GGUF
        """
        try:
            from llama_cpp import Llama
            
            logger.info(f"📥 Cargando modelo llama.cpp: {model_path}")
            
            self.llm = Llama(
                model_path=model_path,
                n_gpu_layers=33,  # Máximo de capas en GPU
                n_threads=8,      # Threads CPU
                verbose=False
            )
            
            self.loaded = True
            logger.info(f"✅ llama.cpp loaded successfully: {model_path}")
            
        except ImportError as e:
            logger.error(f"❌ llama-cpp-python not installed: {e}")
            raise ImportError(
                "Install llama-cpp-python: pip install llama-cpp-python"
            )
        except RuntimeError as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise RuntimeError(f"Cannot load model {model_path}: {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error loading model: {e}")
            raise
    
    def generate(
        self,
        full_prompt: str,
        max_tokens: int = 200,
        temperature: float = 0.8
    ) -> str:
        """
        Genera texto usando llama.cpp.
        
        Args:
            full_prompt: Prompt completo con sistema + contexto + consulta
            max_tokens: Máximo de tokens a generar
            temperature: Creatividad (0.0-1.0, más alto = más creativo)
        
        Returns:
            Texto generado
        
        Raises:
            RuntimeError: Si el modelo no está cargado
            ValueError: Si los parámetros son inválidos
        """
        if not self.loaded or self.llm is None:
            raise RuntimeError("llama.cpp model not loaded")
        
        if not isinstance(full_prompt, str) or not full_prompt.strip():
            raise ValueError("full_prompt must be a non-empty string")
        
        if not 1 <= max_tokens <= 32000:
            raise ValueError("max_tokens must be between 1 and 32000")
        
        if not 0.0 <= temperature <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")
        
        try:
            output = self.llm(
                full_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                repeat_penalty=1.1,
                stop=["User:", "Usuario:", "\n\nUsuario:"],
                echo=False  # No repetir el prompt
            )
            
            text = output['choices'][0]['text'].strip()
            return text
            
        except Exception as e:
            logger.error(f"❌ Error generating text with llama.cpp: {e}")
            raise RuntimeError(f"Generation failed: {e}")
    
    def get_info(self) -> Dict[str, any]:
        """Retorna información del modelo cargado"""
        if not self.loaded:
            return {
                'status': 'not_loaded',
                'model_path': self.model_path
            }
        
        return {
            'status': 'loaded',
            'model_path': self.model_path,
            'backend': 'llama.cpp',
            'description': 'Ultra-rápido C++ backend'
        }
    
    def unload(self) -> None:
        """Descarga el modelo y libera recursos"""
        if self.llm is not None:
            self.llm = None
            self.loaded = False
            logger.info("✅ llama.cpp backend unloaded")
