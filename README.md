# TARS - IA Personal Inteligente ⚡

> **NUEVO**: Ahora con aceleración **llama.cpp** - respuestas 4x más rápidas 🚀

## 🎯 Descripción
TARS es una IA personal desarrollada para acompañarme (Ndrz) en mi carrera profesional, enfocada en prototipos médicos, exoesqueletos y otras investigaciones. Diseñada para ser escalable, segura y personalizable, con expansión futura a la familia.

## ⚡ Optimizaciones Recientes

### Aceleración con llama.cpp
- **Velocidad**: Respuestas 4x más rápidas (0.5-1s vs 2-3s)
- **Backend**: llama-cpp-python con modelos GGUF cuantizados
- **Modelo**: WizardLM-7B Q4_0 (3.6GB, ~5 tokens/segundo)
- **Sistema de prioridades**:
  1. 🚀 llama.cpp (ultrarrápido, C++)
  2. ⚡ Ollama (rápido, si disponible)
  3. 📦 Phi-2 Transformers (fallback)

Ver [INTEGRACION_LLAMA_CPP.md](INTEGRACION_LLAMA_CPP.md) para detalles técnicos.

### Lazy Loading
- LLaVA solo se carga cuando se necesita analizar imágenes
- Phi-2 como único modelo de texto en inicio
- Reducción de 50% en uso de memoria inicial
- Tiempo de inicio: 20-30s (vs 60-90s antes)

Ver documentación completa:
- [OPTIMIZACION_APLICADA.md](OPTIMIZACION_APLICADA.md) - Optimizaciones implementadas
- [RESUMEN_OPTIMIZACION.md](RESUMEN_OPTIMIZACION.md) - Resumen técnico
- [GUIA_RAPIDA.md](GUIA_RAPIDA.md) - Guía de uso rápido

---

## 🎮 Funcionalidades de depuración y utilidad

### Marcar respuestas como útiles o no útiles

Durante el chat en terminal (usando `tars_terminal_chat.py`), puedes escribir:

- `útil` o `util` para marcar la última respuesta de TARS como útil
- `no útil` o `no util` para marcar la última respuesta como no útil

Esto se registra en el archivo `utilidad_respuestas_tars.txt` para que puedas revisar después qué te sirvió y qué no.

### Guardado interactivo de temas

Si escribes frases como "guarda esto", "cambiar de tema", "nueva conversación", el sistema te preguntará dónde guardar el historial antes de limpiar o cambiar de tema.

---

## 🎯 Diferenciadores vs Copilot/ChatGPT

TARS **NO compite** en programación general. Su valor está en:

### 1. 🔒 **Privacidad Total** (Crítico para Medicina)
- ✅ **100% local** - Sin enviar datos a internet
- ✅ Ideal para imágenes médicas de pacientes (HIPAA compliance)
- ✅ Datos de investigación confidenciales
- ✅ Prototipos privados pre-publicación

### 2. 🧠 **Memoria a Largo Plazo**
- ✅ Recuerda **todos** tus proyectos y experimentos
- ✅ Busca soluciones en tu historial ("¿cómo solucioné esto en octubre?")
- ✅ Evolución de diseños documentada automáticamente
- ✅ Base de conocimiento acumulativa que crece contigo

### 3. 🔧 **Control de Hardware Real**
- ✅ Controla ESP32, Arduino, sensores, actuadores
- ✅ Ejecuta protocolos de prueba automatizados
- ✅ Monitoreo en tiempo real de experimentos
- ✅ Calibración automática de servos/motores

### 4. 🧪 **Cerebros Expertos Especializados**
- ✅ **Brain Medical**: Análisis de imágenes médicas con LLaVA
- ✅ **Brain Mechanical**: Cálculos de ingeniería (torque, materiales, etc)
- ✅ **Brain Conceptual**: Análisis ergonómico y de diseño
- ✅ Integrados con tu contexto específico

### 5. 📊 **Documentación Automática de Experimentos**
- ✅ Registra setup, resultados, observaciones
- ✅ Genera reportes de progreso de proyectos
- ✅ Compara versiones de diseño
- ✅ Historial completo de iteraciones

## Objetivos
- **Base Sólida**: IA con capacidades de NLP, visión por computadora y aprendizaje continuo.
- **Personalización**: Adaptación a necesidades individuales, con perfiles privados.
- **Escalabilidad**: Desde PC local a cluster familiar y mini IAs en ESP32.
- **Seguridad**: Privacidad total, con controles administrativos.
- **Durabilidad**: Proyecto mantenible y mejorable a lo largo de la vida.

## Arquitectura General
- **Frontend**: Streamlit para interfaz web segura.
- **Backend**: Python con integración de modelos (PA-LLaVA para visión, otros para NLP).
- **Almacenamiento**: Directorios privados por usuario, base de datos para memoria.
- **Seguridad**: Autenticación hasheada, modo exclusivo.
- **Escalabilidad**: Modular para despliegue en diferentes dispositivos.

## Fases de Desarrollo

### Fase 1: Base y Seguridad (Completada)
- Sistema de login con perfiles: Ndrz, Papá_Abogado, Mamá_Abogada, Betty, Diana, Abuela.
- Contraseñas hasheadas, modo exclusivo para admin.
- Almacenamiento privado de archivos.

### Fase 2: Núcleo de IA (En Desarrollo)
- Integración con PA-LLaVA para análisis de imágenes médicas.
- Capacidades básicas de chat y comandos.
- Procesamiento de texto y voz (opcional).

### Fase 3: Personalización y Aprendizaje ✅ **NUEVO**
- Perfiles de usuario con preferencias y memoria.
- **Aprendizaje de Personalidad**: TARS aprende de audios/voz del usuario para replicar su estilo de comunicación.
- Recomendaciones personalizadas basadas en personalidad aprendida.

#### 🎭 **Sistema de Personalidad Aprendida**
TARS puede aprender tu forma de hablar, expresiones favoritas, tono y estilo de comunicación:

**Cómo entrenar:**
- `entrenar_audio mi_voz.wav` - Aprende de archivos de audio
- `entrenar_texto "tu mensaje"` - Aprende de textos escritos
- **Automático**: Aprende de cada conversación (voz/texto)

**Comandos disponibles:**
- `estadisticas_personalidad` - Ver análisis de personalidad aprendida
- `sugerencias_personalidad` - Recomendaciones para mejorar
- `resetear_personalidad` - Volver a personalidad base

**Archivos relacionados:**
- `personality_trainer.py` - Motor de aprendizaje de personalidad
- `personalidad_aprendida.json` - Base de datos de personalidad
- `entrenamiento_personalidad_demo.sh` - Guía de uso

### Fase 4: Funcionalidades Avanzadas
- Asistente para diseño de prototipos (renderizado, simulación).
- Integración con herramientas médicas y legales.
- Interfaz de voz y comandos naturales.

### Fase 5: Escalabilidad Familiar
- Despliegue en cluster (mini PC en casa de papás).
- Mini IAs en ESP32 para cada familiar.
- Sincronización de datos segura.

## Tecnologías
- **Lenguaje**: Python
- **Framework IA**: Transformers, PyTorch (para PA-LLaVA)
- **Interfaz**: Streamlit
- **Seguridad**: Hashlib, OS para aislamiento
- **Almacenamiento**: SQLite o archivos locales inicialmente
- **Versionado**: Git

## Instalación y Uso
1. Clona el repo: `git clone [url]`
2. Instala dependencias: `pip install -r requirements.txt`
3. Ejecuta: `streamlit run tars_seguro.py`

## Documentación Adicional
- **Diario de Desarrollo**: Mantén logs en `docs/diario.md`
- **Experimentos**: Usa notebooks en `notebooks/`
- **Commits**: Usa mensajes descriptivos, ej. "Fase 2: Integración PA-LLaVA"

## Roadmap Futuro
Ver comentarios en `tars_seguro.py`.

## Normas y Ética
Para asegurar que TARS sea un proyecto responsable y escalable, seguimos estas normas:

### Ciberseguridad

### Computación

### Área Médica

## Reto para Fase 2: Módulo de Visión Robótica
Cuando integres PA-LLaVA, haz que TARS no solo analice imágenes, sino que etiquete componentes específicos:

---

## 🖥️ Setup en nuevas PCs y optimización para IA

Para instalar y optimizar el proyecto en una nueva PC, sigue estos pasos:

1. Clona el repositorio desde GitHub:
  ```bash
  git clone <URL_DEL_REPO>
  ```
2. Instala las dependencias principales:
  ```bash
  pip install -r requirements.txt
  pip install -r requirements_sprint2.txt
  ```
3. Si tu PC tiene una GPU NVIDIA, consulta el archivo [SETUP_1660_SUPER.md](SETUP_1660_SUPER.md) para instrucciones específicas de optimización (drivers, CUDA, PyTorch, faiss-gpu).
4. Para otros hardware, adapta el setup y documenta los cambios en un archivo similar.

**Nota:** Cada PC puede requerir ajustes según su hardware y demanda de trabajo. El setup está pensado para que cada equipo contribuya al 100% a la IA.

---
=======
# keys_1
Personali_a
>>>>>>> 80307d3bd450fd3b7e1b75094d8c34d72d565950
