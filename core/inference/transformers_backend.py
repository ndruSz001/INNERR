"""
Transformers Backend - wrapper para Hugging Face Transformers
Backend fallback usando PyTorch (Phi-2, LLaMA, etc)

Responsabilidad ÚNICA: generar texto usando Transformers
Sin dependencias cruzadas con otros módulos TARS.
"""

from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class TransformersBackend:
    """Backend Transformers para CPU/GPU usando PyTorch"""
    
    def __init__(
        self,
        model_name: str = "microsoft/phi-2",
        device: str = "cuda"
    ):
        """
        Inicializa el backend Transformers.
        
        Args:
            model_name: Hugging Face model ID 
                       (ej: microsoft/phi-2, meta-llama/Llama-2-7b-hf)
            device: "cuda" para GPU, "cpu" para CPU
        
        Raises:
            ImportError: Si torch o transformers no está instalado
            RuntimeError: Si el modelo no se puede cargar
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        self.tokenizer = None
        self.loaded = False
        
        self._load_model()
    
    def _load_model(self) -> None:
        """Carga el modelo y tokenizer desde Hugging Face"""
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            logger.info(f"📥 Cargando modelo Transformers: {self.model_name}")
            logger.info(f"   Dispositivo: {self.device}")
            
            # Determinar dtype según dispositivo
            dtype = torch.float16 if self.device == "cuda" else torch.float32
            logger.info(f"   Dtype: {dtype}")
            
            # Cargar tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                padding_side='left'
            )
            
            # Cargar modelo
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=dtype,
                device_map=self.device if self.device == "cuda" else None,
                trust_remote_code=True
            )
            
            # Mover a CPU si es necesario
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            self.model.eval()  # Modo evaluación
            self.loaded = True
            logger.info(f"✅ Transformers backend loaded: {self.model_name}")
            
        except ImportError as e:
            logger.error(f"❌ torch or transformers not installed: {e}")
            raise ImportError(
                "Install torch and transformers: pip install torch transformers"
            )
        except RuntimeError as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise RuntimeError(f"Cannot load model {self.model_name}: {e}")
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
        Genera texto usando Transformers.
        
        Args:
            full_prompt: Prompt completo con sistema + contexto + consulta
            max_tokens: Máximo de tokens a generar
            temperature: Creatividad (0.0-1.0)
        
        Returns:
            Texto generado
        
        Raises:
            RuntimeError: Si el modelo no está cargado
            ValueError: Si los parámetros son inválidos
        """
        if not self.loaded or self.model is None or self.tokenizer is None:
            raise RuntimeError("Transformers model not loaded")
        
        if not isinstance(full_prompt, str) or not full_prompt.strip():
            raise ValueError("full_prompt must be a non-empty string")
        
        if not 1 <= max_tokens <= 32000:
            raise ValueError("max_tokens must be between 1 and 32000")
        
        if not 0.0 <= temperature <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")
        
        try:
            import torch
            
            # Tokenizar
            inputs = self.tokenizer(
                full_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048,
                padding=False
            ).to(self.device)
            
            # Generar
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    top_p=0.9,
                    do_sample=temperature > 0,  # Solo samplear si temperature > 0
                    repetition_penalty=1.1,
                    eos_token_id=self.tokenizer.eos_token_id,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decodificar
            text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Limpiar: remover prompt original si está presente
            if full_prompt in text:
                text = text.split(full_prompt)[-1].strip()
            
            return text
            
        except torch.cuda.OutOfMemoryError as e:
            logger.error(f"❌ CUDA out of memory: {e}")
            raise RuntimeError(
                f"Out of GPU memory. Try reducing max_tokens or use CPU. Error: {e}"
            )
        except Exception as e:
            logger.error(f"❌ Error generating text: {e}")
            raise RuntimeError(f"Generation failed: {e}")
    
    def get_info(self) -> Dict[str, any]:
        """Retorna información del modelo cargado"""
        return {
            'status': 'loaded' if self.loaded else 'not_loaded',
            'model_name': self.model_name,
            'device': self.device,
            'backend': 'transformers',
            'description': 'PyTorch backend (Phi-2, LLaMA, etc)'
        }
    
    def unload(self) -> None:
        """Descarga el modelo y libera recursos"""
        try:
            import torch
            
            if self.model is not None:
                # Mover a CPU para liberar VRAM
                if self.device == "cuda":
                    self.model = self.model.to("cpu")
                    torch.cuda.empty_cache()
                
                self.model = None
                self.tokenizer = None
                self.loaded = False
                logger.info("✅ Transformers backend unloaded")
        except Exception as e:
            logger.error(f"Error unloading model: {e}")
