"""
Ollama Backend - wrapper para Ollama
Backend alternativo usando Ollama (llama3, mistral, neural-chat, etc)

Responsabilidad ÚNICA: generar texto usando Ollama API
Sin dependencias cruzadas con otros módulos TARS.
"""

from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class OllamaBackend:
    """Backend Ollama - interfaz HTTP a modelos locales"""
    
    def __init__(
        self,
        model: str = "llama3",
        host: str = "http://localhost:11434"
    ):
        """
        Inicializa el backend Ollama.
        
        Args:
            model: Nombre del modelo Ollama 
                  (llama3, mistral, neural-chat, etc)
            host: URL del servidor Ollama
        
        Raises:
            ImportError: Si el paquete ollama no está instalado
            ConnectionError: Si no puede conectar con Ollama
        """
        self.model = model
        self.host = host
        self.ollama_client = None
        self.loaded = False
        
        self._initialize()
    
    def _initialize(self) -> None:
        """Verifica conexión e inicializa cliente"""
        try:
            import ollama
            self.ollama_client = ollama
            
            logger.info(f"🔄 Verificando modelo Ollama: {self.model}")
            
            # Probar conexión
            info = ollama.show(self.model)
            self.loaded = True
            logger.info(f"✅ Ollama backend inicializado: {self.model}")
            
        except ImportError as e:
            logger.error(f"❌ ollama package not installed: {e}")
            raise ImportError(
                "Install ollama: pip install ollama"
            )
        except Exception as e:
            logger.warning(
                f"⚠️  Ollama connection failed (will retry on generate): {e}"
            )
            # No fallar aquí, intentaremos en generate()
            self.ollama_client = None
    
    def generate(
        self,
        full_prompt: str,
        max_tokens: int = 200,
        temperature: float = 0.8
    ) -> str:
        """
        Genera texto usando Ollama.
        
        Args:
            full_prompt: Prompt completo con sistema + contexto + consulta
            max_tokens: Máximo de tokens a generar
            temperature: Creatividad (0.0-1.0)
        
        Returns:
            Texto generado
        
        Raises:
            RuntimeError: Si Ollama no está disponible
            ValueError: Si los parámetros son inválidos
        """
        if self.ollama_client is None:
            raise RuntimeError(
                "Ollama not available. Make sure Ollama is running: ollama serve"
            )
        
        if not isinstance(full_prompt, str) or not full_prompt.strip():
            raise ValueError("full_prompt must be a non-empty string")
        
        if not 1 <= max_tokens <= 32000:
            raise ValueError("max_tokens must be between 1 and 32000")
        
        if not 0.0 <= temperature <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")
        
        try:
            response = self.ollama_client.generate(
                model=self.model,
                prompt=full_prompt,
                stream=False,
                options={
                    'temperature': temperature,
                    'num_predict': max_tokens,
                    'top_p': 0.9,
                    'repeat_penalty': 1.1
                }
            )
            
            text = response.get('response', '').strip()
            
            if not text:
                logger.warning("⚠️  Ollama returned empty response")
                return ""
            
            return text
            
        except ConnectionError as e:
            logger.error(f"❌ Cannot connect to Ollama: {e}")
            raise RuntimeError(
                f"Ollama connection failed. Is Ollama running? Error: {e}"
            )
        except Exception as e:
            logger.error(f"❌ Error generating text with Ollama: {e}")
            raise RuntimeError(f"Generation failed: {e}")
    
    def get_info(self) -> Dict[str, any]:
        """Retorna información del modelo Ollama"""
        return {
            'status': 'loaded' if self.loaded else 'not_loaded',
            'model': self.model,
            'host': self.host,
            'backend': 'ollama',
            'description': 'API-based backend (llama3, mistral, etc)'
        }
    
    def list_models(self) -> list:
        """Lista todos los modelos disponibles en Ollama"""
        if self.ollama_client is None:
            logger.warning("Ollama client not available")
            return []
        
        try:
            models = self.ollama_client.list()
            return models.get('models', [])
        except Exception as e:
            logger.error(f"Cannot list models: {e}")
            return []
    
    def pull_model(self, model_name: str) -> None:
        """Descarga un modelo desde Ollama registry"""
        if self.ollama_client is None:
            raise RuntimeError("Ollama client not available")
        
        try:
            logger.info(f"📥 Descargando modelo: {model_name}")
            self.ollama_client.pull(model_name)
            logger.info(f"✅ Modelo descargado: {model_name}")
        except Exception as e:
            logger.error(f"Cannot pull model: {e}")
            raise
