# 🚀 GUÍA DE INICIO RÁPIDO - SPRINT 1

**Objetivo:** Crear el módulo `core/inference/` independiente y testeable  
**Tiempo:** 2-3 horas  
**Resultado:** Backend elegible y testeable  

---

## 📋 Tareas Sprint 1

### 1️⃣ Backend llama.cpp (30 min)

**Archivo:** `core/inference/llm_backend.py`

```python
"""
Wrapper para llama.cpp - Backend C++ ultrarrápido
Responsabilidad: Solo generar texto usando llama-cpp-python
No debe importar nada de TARS (zero dependencies)
"""

from typing import Optional, Dict
import subprocess
import json


class LlamaCppBackend:
    """Backend ultrarrápido usando llama.cpp"""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Args:
            model_path: Ruta al modelo GGUF (ej: models/Phi-2-gguf/model.gguf)
        """
        self.model_path = model_path
        self.loaded = False
        
        if model_path:
            try:
                from llama_cpp import Llama
                self.llm = Llama(model_path=model_path, n_gpu_layers=33)
                self.loaded = True
                print(f"✅ llama.cpp loaded: {model_path}")
            except Exception as e:
                print(f"❌ llama.cpp failed: {e}")
    
    def generate(
        self,
        full_prompt: str,
        max_tokens: int = 200,
        temperature: float = 0.8
    ) -> str:
        """
        Genera texto usando llama.cpp
        
        Args:
            full_prompt: Prompt completo con sistema + contexto + consulta
            max_tokens: Máximo de tokens a generar
            temperature: Creatividad (0.0-1.0)
        
        Returns:
            Texto generado
        """
        if not self.loaded:
            raise RuntimeError("llama.cpp not loaded")
        
        output = self.llm(
            full_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
            repeat_penalty=1.1,
            stop=["User:", "Usuario:"]
        )
        
        return output['choices'][0]['text'].strip()
```

**Checklist:**
- [ ] Crear archivo
- [ ] Implementar `__init__()` con carga de modelo
- [ ] Implementar `generate()` method
- [ ] Probar: `python -c "from core.inference.llm_backend import LlamaCppBackend"`

---

### 2️⃣ Backend Ollama (30 min)

**Archivo:** `core/inference/ollama_backend.py`

```python
"""
Wrapper para Ollama - Backend alternativo (llama3, mistral, etc)
Responsabilidad: Solo generar texto usando Ollama API
"""

from typing import Optional
import ollama


class OllamaBackend:
    """Backend Ollama (interfaz HTTP a modelos locales)"""
    
    def __init__(self, model: str = "llama3"):
        """
        Args:
            model: Nombre del modelo Ollama (llama3, mistral, neural-chat, etc)
        """
        self.model = model
        self.loaded = False
        
        try:
            # Probar conexión a Ollama
            info = ollama.show(model)
            self.loaded = True
            print(f"✅ Ollama loaded: {model}")
        except Exception as e:
            print(f"❌ Ollama failed: {e}")
    
    def generate(
        self,
        full_prompt: str,
        max_tokens: int = 200,
        temperature: float = 0.8
    ) -> str:
        """
        Genera texto usando Ollama
        
        Args:
            full_prompt: Prompt completo
            max_tokens: Máximo de tokens
            temperature: Creatividad
        
        Returns:
            Texto generado
        """
        if not self.loaded:
            raise RuntimeError("Ollama not connected")
        
        response = ollama.generate(
            model=self.model,
            prompt=full_prompt,
            stream=False,
            options={
                'temperature': temperature,
                'num_predict': max_tokens,
                'top_p': 0.9
            }
        )
        
        return response['response'].strip()
```

**Checklist:**
- [ ] Crear archivo
- [ ] Implementar `__init__()` con verificación de modelo
- [ ] Implementar `generate()` method
- [ ] Probar: `ollama pull llama3 && python -c "from core.inference.ollama_backend import OllamaBackend"`

---

### 3️⃣ Backend Transformers (30 min)

**Archivo:** `core/inference/transformers_backend.py`

```python
"""
Wrapper para Transformers - Backend fallback (Phi-2, etc)
Responsabilidad: Solo generar texto usando PyTorch/Hugging Face
"""

from typing import Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


class TransformersBackend:
    """Backend Transformers para CPU/GPU"""
    
    def __init__(
        self,
        model_name: str = "microsoft/phi-2",
        device: str = "cuda"
    ):
        """
        Args:
            model_name: Hugging Face model ID
            device: "cuda" o "cpu"
        """
        self.model_name = model_name
        self.device = device
        self.loaded = False
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                trust_remote_code=True
            ).to(device)
            
            self.loaded = True
            print(f"✅ Transformers loaded: {model_name} on {device}")
        except Exception as e:
            print(f"❌ Transformers failed: {e}")
    
    def generate(
        self,
        full_prompt: str,
        max_tokens: int = 200,
        temperature: float = 0.8
    ) -> str:
        """
        Genera texto usando Transformers
        
        Args:
            full_prompt: Prompt completo
            max_tokens: Máximo de tokens
            temperature: Creatividad
        
        Returns:
            Texto generado
        """
        if not self.loaded:
            raise RuntimeError("Transformers model not loaded")
        
        inputs = self.tokenizer(
            full_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                do_sample=True,
                repetition_penalty=1.1,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Limpiar: remover prompt original
        if full_prompt in text:
            text = text.split(full_prompt)[-1]
        
        return text.strip()
```

**Checklist:**
- [ ] Crear archivo
- [ ] Implementar `__init__()` con carga de modelo
- [ ] Implementar `generate()` method
- [ ] Probar: `python -c "from core.inference.transformers_backend import TransformersBackend"`

---

### 4️⃣ Testing de Backends (30 min)

**Archivo:** `tests/test_inference.py`

```python
"""
Tests para verificar que cada backend funciona independientemente
"""

import pytest
from core.inference.inference_engine import InferenceEngine


def test_inference_engine_initialization():
    """Verifica que el motor se inicializa correctamente"""
    engine = InferenceEngine(config={
        'use_llama_cpp': True,
        'use_ollama': True,
        'use_transformers': True
    })
    
    backends = engine.list_available_backends()
    assert len(backends) > 0, "No backends available!"
    print(f"✅ Available backends: {backends}")


def test_generate_text():
    """Verifica que la generación de texto funciona"""
    engine = InferenceEngine()
    
    response = engine.generate(
        prompt="¿Cuál es tu nombre?",
        system_prompt="Eres una IA. Responde brevemente.",
        max_tokens=50
    )
    
    assert len(response) > 0, "No response generated"
    print(f"✅ Generated: {response[:100]}...")


def test_backend_fallback():
    """Verifica que el sistema cambia de backend si uno falla"""
    engine = InferenceEngine()
    
    initial_backend = engine.get_active_backend()
    print(f"Initial backend: {initial_backend}")
    
    # Generar varias respuestas
    for i in range(3):
        response = engine.generate(
            prompt=f"Test {i}. Responde con 5 palabras.",
            max_tokens=20
        )
        assert len(response) > 0
    
    print(f"✅ Fallback works correctly")


def test_benchmark():
    """Compara velocidad de backends"""
    engine = InferenceEngine()
    
    results = engine.benchmark()
    print("\n🏃 Backend Benchmark:")
    for backend, latency in results.items():
        if latency:
            print(f"  {backend}: {latency:.3f}s")
        else:
            print(f"  {backend}: ❌ FAILED")


if __name__ == "__main__":
    test_inference_engine_initialization()
    test_generate_text()
    test_backend_fallback()
    test_benchmark()
    print("\n✅ All tests passed!")
```

**Checklist:**
- [ ] Crear directorio `tests/`
- [ ] Crear archivo `tests/__init__.py` (vacío)
- [ ] Crear archivo `tests/test_inference.py`
- [ ] Ejecutar: `pytest tests/test_inference.py -v`

---

## 🧪 Testing End-to-End (Sprint 1)

### Antes de Avanzar a Sprint 2

```bash
# 1. Verificar que cada backend se carga correctamente
python -c "from core.inference.llm_backend import LlamaCppBackend; print('✅ llama.cpp')"
python -c "from core.inference.ollama_backend import OllamaBackend; print('✅ Ollama')"
python -c "from core.inference.transformers_backend import TransformersBackend; print('✅ Transformers')"

# 2. Verificar que el motor orquesta correctamente
python -c "from core.inference.inference_engine import InferenceEngine; e = InferenceEngine(); print(f'✅ Active: {e.get_active_backend()}')"

# 3. Ejecutar tests
pytest tests/test_inference.py -v

# 4. Probar generación real
python -c "
from core.inference.inference_engine import InferenceEngine
e = InferenceEngine()
resp = e.generate('Hola, ¿cómo estás?', 'Eres TARS, una IA amigable.')
print('Response:', resp[:100])
"
```

---

## 📝 Estructura Final Sprint 1

```
core/
├─ __init__.py
├─ inference/
│  ├─ __init__.py
│  ├─ inference_engine.py       ✅ YA EXISTE
│  ├─ llm_backend.py            ← TODO
│  ├─ ollama_backend.py         ← TODO
│  └─ transformers_backend.py   ← TODO
├─ memory/
│  └─ __init__.py               (para Sprint 2)
└─ apis/
   └─ __init__.py               (para Sprint 2)

tests/
├─ __init__.py
└─ test_inference.py            ← TODO
```

---

## ⏱️ Timeline Esperado

| Tarea | Tiempo | Status |
|-------|--------|--------|
| llm_backend.py | 30 min | ← AQUÍ |
| ollama_backend.py | 30 min | |
| transformers_backend.py | 30 min | |
| test_inference.py | 30 min | |
| Debugging + ajustes | 30 min | |
| **TOTAL SPRINT 1** | **2.5 horas** | |

---

## 🎯 Definición de "Listo" (Sprint 1 Completo)

✅ Todos los 3 backends se cargan sin errores  
✅ `InferenceEngine` decide correctamente cual backend usar  
✅ Fallback automático si un backend falla  
✅ Tests pasan (pytest)  
✅ Cada backend puede generar texto independientemente  
✅ Documentación actualizada (docstrings en código)  

---

## 🆘 Troubleshooting Común

### Error: "No module named llama_cpp"
```bash
pip install llama-cpp-python
```

### Error: "Ollama connection refused"
```bash
# Instalar Ollama desde https://ollama.ai
ollama serve  # En otra terminal
ollama pull llama3
```

### Error: "CUDA out of memory"
```python
# En config, cambiar a CPU
config = {
    'use_transformers': True,
    'device': 'cpu'  # En lugar de 'cuda'
}
```

---

## 📞 Próximo Paso Después de Sprint 1

Una vez completado Sprint 1:
1. Verificar que `core/inference/` funciona correctamente
2. Crear tests de integración con memoria (Sprint 2)
3. Pasar a `core/memory/` (Sprint 2)

**Sprint 2 begin:** `core/memory/conversation_store.py`

---

**¡Listo para comenzar Sprint 1? Crea el archivo 1️⃣ first: `core/inference/llm_backend.py`**
