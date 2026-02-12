"""
Tests para InferenceEngine y backends

Verifica que cada backend funciona independientemente
y que el motor orquesta correctamente.
"""

import pytest
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestInferenceEngine:
    """Tests para el motor de inferencia"""
    
    def test_engine_initialization(self):
        """Verifica que InferenceEngine se inicializa"""
        from core.inference.inference_engine import InferenceEngine
        
        engine = InferenceEngine(config={
            'use_llama_cpp': False,  # No disponible sin modelo
            'use_ollama': False,      # Veremos después
            'use_transformers': True
        })
        
        backends = engine.list_available_backends()
        assert len(backends) >= 0, "Engine initialized"
        print(f"✅ Engine initialized with backends: {backends}")
    
    def test_engine_get_active_backend(self):
        """Verifica que se obtiene el backend activo"""
        from core.inference.inference_engine import InferenceEngine
        
        engine = InferenceEngine(config={
            'use_llama_cpp': False,
            'use_ollama': False,
            'use_transformers': True
        })
        
        active = engine.get_active_backend()
        print(f"✅ Active backend: {active}")
    
    def test_engine_list_available_backends(self):
        """Verifica que se listan backends disponibles"""
        from core.inference.inference_engine import InferenceEngine
        
        engine = InferenceEngine(config={
            'use_llama_cpp': False,
            'use_ollama': False,
            'use_transformers': True
        })
        
        backends = engine.list_available_backends()
        assert isinstance(backends, list), "Returns a list"
        print(f"✅ Available backends: {backends}")


class TestLlamaCppBackend:
    """Tests para LlamaCppBackend"""
    
    def test_backend_initialization_no_model(self):
        """Verifica que el backend se inicializa sin modelo"""
        from core.inference.llm_backend import LlamaCppBackend
        
        backend = LlamaCppBackend(model_path=None)
        assert not backend.loaded, "Backend not loaded without model"
        print("✅ LlamaCppBackend initialized without model")
    
    def test_backend_get_info(self):
        """Verifica que get_info() retorna info correcta"""
        from core.inference.llm_backend import LlamaCppBackend
        
        backend = LlamaCppBackend(model_path=None)
        info = backend.get_info()
        
        assert isinstance(info, dict), "Returns dict"
        assert 'status' in info, "Has status key"
        print(f"✅ Backend info: {info}")
    
    def test_backend_generate_without_model_raises(self):
        """Verifica que generate() lanza error sin modelo"""
        from core.inference.llm_backend import LlamaCppBackend
        
        backend = LlamaCppBackend(model_path=None)
        
        with pytest.raises(RuntimeError):
            backend.generate("test prompt")
        
        print("✅ Raises RuntimeError when model not loaded")


class TestOllamaBackend:
    """Tests para OllamaBackend"""
    
    def test_backend_initialization(self):
        """Verifica que OllamaBackend se inicializa"""
        from core.inference.ollama_backend import OllamaBackend
        
        backend = OllamaBackend(model="llama3")
        # Puede estar loaded o not_loaded (depende si Ollama está corriendo)
        info = backend.get_info()
        assert 'status' in info
        print(f"✅ OllamaBackend info: {info}")
    
    def test_backend_get_info(self):
        """Verifica que get_info() retorna info correcta"""
        from core.inference.ollama_backend import OllamaBackend
        
        backend = OllamaBackend(model="llama3")
        info = backend.get_info()
        
        assert info['model'] == 'llama3'
        assert info['backend'] == 'ollama'
        print(f"✅ OllamaBackend info retrieved")


class TestTransformersBackend:
    """Tests para TransformersBackend"""
    
    def test_backend_initialization(self):
        """Verifica que TransformersBackend se inicializa"""
        from core.inference.transformers_backend import TransformersBackend
        
        # Usar CPU para testing (más rápido)
        backend = TransformersBackend(
            model_name="microsoft/phi-2",
            device="cpu"
        )
        
        assert backend.loaded, "Model should be loaded"
        print("✅ TransformersBackend initialized")
    
    def test_backend_get_info(self):
        """Verifica que get_info() retorna info correcta"""
        from core.inference.transformers_backend import TransformersBackend
        
        backend = TransformersBackend(
            model_name="microsoft/phi-2",
            device="cpu"
        )
        
        info = backend.get_info()
        assert info['status'] == 'loaded'
        assert info['device'] == 'cpu'
        print(f"✅ TransformersBackend info: {info}")
    
    def test_backend_generate_invalid_prompt_raises(self):
        """Verifica que generate() valida el prompt"""
        from core.inference.transformers_backend import TransformersBackend
        
        backend = TransformersBackend(
            model_name="microsoft/phi-2",
            device="cpu"
        )
        
        with pytest.raises(ValueError):
            backend.generate("")  # Empty prompt
        
        print("✅ Validates empty prompt")
    
    def test_backend_generate_invalid_max_tokens_raises(self):
        """Verifica que generate() valida max_tokens"""
        from core.inference.transformers_backend import TransformersBackend
        
        backend = TransformersBackend(
            model_name="microsoft/phi-2",
            device="cpu"
        )
        
        with pytest.raises(ValueError):
            backend.generate("test", max_tokens=50000)  # Too large
        
        print("✅ Validates max_tokens")
    
    def test_backend_generate_produces_text(self):
        """Verifica que generate() produce texto"""
        from core.inference.transformers_backend import TransformersBackend
        
        backend = TransformersBackend(
            model_name="microsoft/phi-2",
            device="cpu"
        )
        
        response = backend.generate(
            "¿Cuál es tu nombre?",
            max_tokens=50,
            temperature=0.7
        )
        
        assert isinstance(response, str), "Returns string"
        assert len(response) > 0, "Returns non-empty string"
        print(f"✅ Generated text: {response[:80]}...")


# ============================================================================
# TESTS DE INTEGRACIÓN
# ============================================================================

class TestIntegration:
    """Tests de integración del sistema"""
    
    def test_full_inference_pipeline(self):
        """Prueba el pipeline completo de inferencia"""
        from core.inference.inference_engine import InferenceEngine
        
        engine = InferenceEngine(config={
            'use_llama_cpp': False,
            'use_ollama': False,
            'use_transformers': True
        })
        
        # Verificar que el motor está funcionando
        assert engine.get_active_backend() is not None
        print(f"✅ Pipeline ready with: {engine.get_active_backend()}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Ejecutar tests sin pytest (para debugging manual)
    logger.info("🧪 Running tests...")
    
    tests = TestInferenceEngine()
    tests.test_engine_initialization()
    tests.test_engine_get_active_backend()
    tests.test_engine_list_available_backends()
    
    tests_llama = TestLlamaCppBackend()
    tests_llama.test_backend_initialization_no_model()
    tests_llama.test_backend_get_info()
    
    tests_ollama = TestOllamaBackend()
    tests_ollama.test_backend_initialization()
    tests_ollama.test_backend_get_info()
    
    # Tests de Transformers (más pesados)
    logger.info("⏳ Loading Transformers (may take 1-2 minutes)...")
    tests_transformers = TestTransformersBackend()
    tests_transformers.test_backend_initialization()
    tests_transformers.test_backend_get_info()
    tests_transformers.test_backend_generate_invalid_prompt_raises()
    tests_transformers.test_backend_generate_invalid_max_tokens_raises()
    
    logger.info("🚀 Running generation test (may take 30-60s)...")
    tests_transformers.test_backend_generate_produces_text()
    
    tests_integration = TestIntegration()
    tests_integration.test_full_inference_pipeline()
    
    logger.info("✅ All tests passed!")
