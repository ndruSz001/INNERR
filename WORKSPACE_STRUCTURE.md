# Estructura del Workspace TARS - Enfoque en Investigación

## 📁 Archivos Core (Activos)

### Módulos Principales
```
core_ia.py                   # 🧠 Cerebro principal de TARS
├── brain_medical.py         # 🏥 Análisis médico privado (HIPAA)
├── brain_mechanical.py      # ⚙️ Cálculos mecánicos/estructurales
├── brain_conceptual.py      # 🎨 Análisis ergonómico/diseño
├── project_knowledge.py     # 📚 Base de conocimiento acumulativa
└── tars_hardware.py         # 🤖 Control de hardware (ESP32/Arduino)
```

### Interfaz y Utilidades
```
tars_terminal_chat.py        # 💬 Interfaz de chat principal
ejemplos_tars_unico.py       # 📖 Ejemplos de uso
```

### Memoria y Persistencia
```
episodic_memory.py          # 🧠 Memoria episódica
encrypted_db.py             # 🔒 Base de datos encriptada
database_handler.py         # 📊 Manejador de BD
strategic_reasoning.py      # 🎯 Razonamiento estratégico
```

### Documentación
```
README.md                   # 📘 Documentación principal
CLEANUP_PLAN.md            # 🗑️ Plan de limpieza ejecutado
```

---

## 📦 Archivos Archivados (deprecated/)

### deprecated/tests/
- `test_optimizacion.py` - Tests de optimización
- `test_integracion.py` - Tests de integración
- `test_simplificado.py` - Tests simplificados

### deprecated/experiments/
- `infer_4bit.py` - Experimento cuantización 4-bit
- `infer_gptq.py` - Experimento GPTQ
- `infer_gptq_optimum.py` - Experimento Optimum
- `download_model.py` - Script de descarga
- `run_gguf.py` - Experimento individual GGUF

### deprecated/scripts/
- `instalar_llama.sh` - Setup inicial llama.cpp
- `setup_rtx3060.sh` - Setup RTX3060
- `actualizar_entrenamiento_rtx3060.sh` - Entrenamiento
- `optimizar_sistema_rtx3060.sh` - Optimización sistema
- `entrenamiento_personalidad_demo.sh` - Demo personalidad
- `mejoras_avanzadas_personalidad.sh` - Mejoras personalidad

### deprecated/docs/
- `README_RTX3060.md` - README específico RTX3060
- `OPTIMIZACION_README.md` - Docs de optimización
- `OPTIMIZACION_APLICADA.md` - Optimización aplicada
- `RESUMEN_OPTIMIZACION.md` - Resumen optimización
- `INTEGRACION_LLAMA_CPP.md` - Integración llama.cpp
- `ESTRATEGIA_SIGUIENTE.md` - Estrategia antigua
- `GUIA_RAPIDA.md` - Guía rápida
- `checklist_rtx3060.md` - Checklist RTX3060
- `checklist_personalidad.md` - Checklist personalidad
- `comparacion_gpus.md` - Comparación GPUs

### deprecated/personality/
- `personality_config.py` - Configuración personalidad
- `personality_trainer.py` - Entrenador personalidad
- `rvc_voice_cloner.py` - Clonación de voz
- `voz_tars.py` - Síntesis de voz
- `response_postprocessor.py` - Post-procesador

### deprecated/old_versions/
- `terminal_ia.py` - Versión antigua terminal
- `tars_terminal_chat_backup.py` - Backup chat
- `tars_seguro.py` - Versión antigua
- `core_ia_rtx3060.py` - Core específico RTX3060
- `modelos_rtx3060.py` - Modelos RTX3060
- `integracion_llama.py` - Integración antigua
- `optimizacion_llama.py` - Optimización antigua

---

## 🎯 Uso Recomendado

### Para investigación y documentación:
```bash
# Interfaz principal
python tars_terminal_chat.py

# Ver ejemplos de uso
python ejemplos_tars_unico.py
```

### Módulos activos según necesidad:
- **Análisis médico local**: `brain_medical.py`
- **Cálculos mecánicos**: `brain_mechanical.py`
- **Diseño/ergonomía**: `brain_conceptual.py`
- **Control de hardware**: `tars_hardware.py`
- **Base de conocimiento**: `project_knowledge.py`

---

## 📊 Estadísticas de Limpieza

- **Archivos movidos**: 35
- **Archivos eliminados**: 4 temporales
- **Espacio organizado**: deprecated/ con 6 subcategorías
- **Archivos core activos**: 15

**Resultado**: Workspace enfocado en investigación 🎯
