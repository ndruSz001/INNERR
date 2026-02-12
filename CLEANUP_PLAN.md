# Plan de Limpieza de Archivos

## Objetivo Actual
**TARS para investigación: documentación, mejora de diseños, análisis de proyectos**

---

## 🗑️ ARCHIVOS OBSOLETOS - Pueden eliminarse

### Scripts de instalación/setup ya ejecutados:
- `instalar_llama.sh` - Ya se instaló llama.cpp
- `setup_rtx3060.sh` - Setup inicial ya completado
- `actualizar_entrenamiento_rtx3060.sh` - No relacionado con objetivo actual
- `optimizar_sistema_rtx3060.sh` - No necesario para investigación
- `entrenamiento_personalidad_demo.sh` - Demo ya no necesario
- `mejoras_avanzadas_personalidad.sh` - No prioritario

### Archivos de testing/experimentación:
- `test_optimizacion.py` - Tests de optimización completados
- `test_integracion.py` - Tests de integración completados
- `test_simplificado.py` - Tests simplificados completados
- `terminal_ia.py` - Versión antigua, reemplazada por tars_terminal_chat.py
- `tars_terminal_chat_backup.py` - Backup innecesario

### Archivos de experimentos con modelos:
- `infer_4bit.py` - Experimento con cuantización 4-bit (no usado)
- `infer_gptq.py` - Experimento con GPTQ (no usado)
- `infer_gptq_optimum.py` - Experimento con Optimum (no usado)
- `download_model.py` - Script de descarga, ya no necesario
- `run_gguf.py` - Experimento individual, integrado en core_ia.py

### Módulos no relevantes para investigación:
- `core_ia_rtx3060.py` - Versión específica RTX3060, duplicado
- `modelos_rtx3060.py` - Configuración específica RTX3060
- `integracion_llama.py` - Ya integrado en core_ia.py
- `optimizacion_llama.py` - Ya integrado

### Archivos de personalidad/voz (no core para investigación):
- `personality_config.py` - No prioritario para documentación
- `personality_trainer.py` - No prioritario
- `rvc_voice_cloner.py` - Funcionalidad de voz no necesaria ahora
- `voz_tars.py` - Síntesis de voz no necesaria ahora
- `response_postprocessor.py` - No crítico

### Otros archivos obsoletos:
- `tars_seguro.py` - ¿Versión antigua de tars_terminal_chat?
- `ejemplo_audio_simulado.txt` - Ejemplo no usado
- `ejemplo_datos_cluster.json` - Ejemplo no usado
- `last_gguf_output.txt` - Log temporal
- `test_user` - Archivo de test

---

## 📁 ARCHIVAR - Mover a carpeta "deprecated/"

### Documentación obsoleta/redundante:
- `checklist_rtx3060.md` - Específico de hardware
- `checklist_personalidad.md` - No prioritario
- `comparacion_gpus.md` - Ya tomada decisión
- `README_RTX3060.md` - README específico, usar README.md principal
- `OPTIMIZACION_README.md` - Optimización ya aplicada
- `OPTIMIZACION_APLICADA.md` - Duplicado
- `RESUMEN_OPTIMIZACION.md` - Duplicado
- `INTEGRACION_LLAMA_CPP.md` - Ya integrado
- `ESTRATEGIA_SIGUIENTE.md` - Estrategia ya definida
- `GUIA_RAPIDA.md` - Puede quedar pero revisar si duplica README

### Módulos que pueden quedarse inactivos:
- `episodic_memory.py` - Memoria episódica (puede ser útil luego)
- `strategic_reasoning.py` - Razonamiento estratégico (puede ser útil)
- `encrypted_db.py` - Base de datos encriptada (útil para médico)
- `database_handler.py` - Handler de BD (puede ser útil)

---

## ✅ ARCHIVOS CORE - Mantener activos

### Módulos principales:
- `core_ia.py` - ✅ Core principal
- `brain_medical.py` - ✅ Análisis médico
- `brain_mechanical.py` - ✅ Análisis mecánico
- `brain_conceptual.py` - ✅ Análisis conceptual
- `project_knowledge.py` - ✅ Base de conocimiento
- `tars_hardware.py` - ✅ Control de hardware
- `tars_terminal_chat.py` - ✅ Interfaz principal

### Documentación relevante:
- `README.md` - ✅ README principal
- `requirements.txt` - ✅ Dependencias

### Ejemplos:
- `ejemplos_tars_unico.py` - ✅ Ejemplos de uso

### Carpetas importantes:
- `models/` - ✅ Modelos GGUF
- `llama.cpp/` - ✅ Backend C++
- `data/` - ✅ Datos de entrenamiento
- `bench/` - ⚠️ Benchmarks (puede archivarse)
- `scripts/` - ⚠️ Scripts auxiliares (revisar)
- `docs/` - ✅ Documentación
- `tars_lifelong/` - ⚠️ Revisar contenido

---

## 🎯 ACCIÓN RECOMENDADA

1. **Crear carpeta de archivo:**
   ```bash
   mkdir -p deprecated/{scripts,tests,docs,experiments}
   ```

2. **Mover archivos obsoletos:**
   - Scripts → `deprecated/scripts/`
   - Tests → `deprecated/tests/`
   - Docs → `deprecated/docs/`
   - Experimentos → `deprecated/experiments/`

3. **Eliminar archivos temporales:**
   - `last_gguf_output.txt`
   - `test_user`
   - `__pycache__/` (regenerable)

4. **Workspace limpio final:**
   ```
   keys_1/
   ├── core_ia.py                    # Core principal
   ├── brain_*.py                    # 3 cerebros expertos
   ├── project_knowledge.py          # Base de conocimiento
   ├── tars_hardware.py              # Control hardware
   ├── tars_terminal_chat.py         # Interfaz
   ├── ejemplos_tars_unico.py        # Ejemplos
   ├── README.md                     # Documentación
   ├── requirements.txt              # Dependencias
   ├── models/                       # Modelos GGUF
   ├── llama.cpp/                    # Backend
   ├── data/                         # Datos
   ├── docs/                         # Documentación extra
   └── deprecated/                   # Archivos antiguos
   ```

---

## 📊 Resumen de Limpieza

**Total de archivos a mover/eliminar:** ~35 archivos
**Espacio a liberar:** ~varios MB + claridad mental 🧠
**Beneficio:** Workspace enfocado en investigación y documentación
