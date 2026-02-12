# Optimización de TARS

## Situación Actual
- GPU: RTX 3060 (12GB VRAM) ✅
- Modelo: Llama 3.2 3B
- Ollama usando ~2.8GB VRAM
- Primera respuesta: ~5-10 segundos
- Respuestas siguientes: ~2-5 segundos

## Opciones para Acelerar

### 1. Usar modelo más pequeño (MÁS RÁPIDO)
```bash
# Modelo tiny (1.1B) - Respuestas en ~1-2 segundos
ollama pull phi3:mini

# Modelo compacto (1B) - Muy rápido
ollama pull tinyllama
```

Luego cambiar en `core_ia_simple.py` línea 164:
```python
model='phi3:mini',  # en vez de 'llama3.2:3b'
```

### 2. Reducir contexto (MENOS CALIDAD pero más rápido)
En `core_ia_simple.py` línea 145, cambiar:
```python
for ctx in self.contexto[-8:]:  # cambiar a [-4:] o [-2:]
```

### 3. Ajustar parámetros de generación (BALANCE)
En `core_ia_simple.py` añadir a `options`:
```python
options={
    "temperature": 0.7,
    "top_p": 0.9,
    "num_predict": 150,  # Limitar tokens (respuestas más cortas)
    "repeat_penalty": 1.1
}
```

### 4. Precargar modelo (ÓPTIMO)
```bash
# Mantener Ollama siempre con el modelo cargado
ollama run llama3.2:3b ""  # Carga el modelo sin preguntar
```

Agregar esto al inicio de tu sistema o crear un script.

### 5. Usar modelo quantizado Q4 (MÁS EFICIENTE)
El que tienes ya está quantizado (2GB), pero puedes probar versiones más agresivas:
```bash
ollama pull llama3.2:3b-q3_K_M  # Más comprimido, mismo tamaño param
```

## Recomendación Principal

**Para uso interactivo diario:**
```bash
ollama pull phi3:mini
```

Luego actualizar `core_ia_simple.py`:
```python
model='phi3:mini',  # Línea 164
```

Phi3:mini es:
- 3.8B parámetros (casi igual de inteligente)
- Optimizado para velocidad
- ~1-2 segundos por respuesta
- Excelente para chat interactivo

**Para investigación profunda:**
- Mantener llama3.2:3b actual
- Es más preciso y completo
- Vale la pena esperar 3-5 segundos

## Script de inicio rápido
Crear `~/tars.sh`:
```bash
#!/bin/bash
cd /home/ndrz02/keys_1
source .venv/bin/activate
ollama run llama3.2:3b "" &  # Precargar modelo
sleep 2
python3 tars_asistente.py
```

Hacer ejecutable:
```bash
chmod +x ~/tars.sh
```

Usar: `~/tars.sh`

## Métricas esperadas

| Modelo | VRAM | Primera | Siguientes | Calidad |
|--------|------|---------|------------|---------|
| llama3.2:3b | 2.8GB | 8s | 3-5s | ⭐⭐⭐⭐⭐ |
| phi3:mini | 2.3GB | 3s | 1-2s | ⭐⭐⭐⭐ |
| tinyllama | 0.6GB | 1s | <1s | ⭐⭐⭐ |

