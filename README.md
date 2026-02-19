# 🕸️ Arquitectura Distribuida y Mejoras Recientes

El sistema ahora soporta ejecución distribuida entre múltiples nodos (PC1, PC2, etc), con las siguientes características:

- **Inferencia real modular**: cada nodo puede ejecutar modelos o delegar tareas según reglas configurables.
- **Balanceo de carga inteligente**: las tareas se asignan dinámicamente según el tipo de modelo y recursos.
- **Caché distribuido y persistente**: resultados de inferencia se almacenan y recuperan incluso tras reinicios.
- **Tolerancia a fallos**: manejo de errores y persistencia del caché para robustez ante caídas.
- **Seguridad básica**: endpoints protegidos por API key configurable.
- **Escalabilidad**: arquitectura preparada para agregar más nodos fácilmente.
- **Métricas y monitoreo**: endpoint /metrics compatible con Prometheus para observabilidad y dashboards.

Consulta `distributed/MEJORAS_FUTURAS.md` para roadmap y detalles técnicos.
# TARS - IA Personal Inteligente ⚡

> **NUEVO**: Ahora con aceleración **llama.cpp** - respuestas 4x más rápidas 🚀

## 🎯 Descripción
TARS es una IA personal desarrollada para acompañarme (Ndrz) en mi carrera profesional, enfocada en prototipos médicos, exoesqueletos y otras investigaciones. Diseñada para ser escalable, segura y personalizable, con expansión futura a la familia.

## ⚡ Optimizaciones Recientes

### Aceleración con llama.cpp
  1. 🚀 llama.cpp (ultrarrápido, C++)
  2. ⚡ Ollama (rápido, si disponible)
  3. 📦 Phi-2 Transformers (fallback)

Ver [INTEGRACION_LLAMA_CPP.md](INTEGRACION_LLAMA_CPP.md) para detalles técnicos.

### Lazy Loading

Ver documentación completa:


## 🎮 Funcionalidades de depuración y utilidad

### Marcar respuestas como útiles o no útiles

Durante el chat en terminal (usando `tars_terminal_chat.py`), puedes escribir:


Esto se registra en el archivo `utilidad_respuestas_tars.txt` para que puedas revisar después qué te sirvió y qué no.

### Guardado interactivo de temas

Si escribes frases como "guarda esto", "cambiar de tema", "nueva conversación", el sistema te preguntará dónde guardar el historial antes de limpiar o cambiar de tema.


## 🎯 Diferenciadores vs Copilot/ChatGPT

TARS **NO compite** en programación general. Su valor está en:

### 1. 🔒 **Privacidad Total** (Crítico para Medicina)

### 2. 🧠 **Memoria a Largo Plazo**

### 3. 🔧 **Control de Hardware Real**

### 4. 🧪 **Cerebros Expertos Especializados**

### 5. 📊 **Documentación Automática de Experimentos**

## Objetivos

## Arquitectura General

## Fases de Desarrollo

### Fase 1: Base y Seguridad (Completada)

### Fase 2: Núcleo de IA (En Desarrollo)

### Fase 3: Personalización y Aprendizaje ✅ **NUEVO**

#### 🎭 **Sistema de Personalidad Aprendida**
TARS puede aprender tu forma de hablar, expresiones favoritas, tono y estilo de comunicación:

**Cómo entrenar:**

**Comandos disponibles:**

**Archivos relacionados:**

### Fase 4: Funcionalidades Avanzadas

### Fase 5: Escalabilidad Familiar

## Tecnologías

## Instalación y Uso
1. Clona el repo: `git clone [url]`
2. Instala dependencias: `pip install -r requirements.txt`
3. Ejecuta: `streamlit run tars_seguro.py`

## Documentación Adicional

## Roadmap Futuro
Ver comentarios en `tars_seguro.py`.

## Normas y Ética
Para asegurar que TARS sea un proyecto responsable y escalable, seguimos estas normas:

### Ciberseguridad

### Computación

### Área Médica

## Reto para Fase 2: Módulo de Visión Robótica
Cuando integres PA-LLaVA, haz que TARS no solo analice imágenes, sino que etiquete componentes específicos:


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

## 🚀 Instalación automática de dependencias

Para instalar todas las dependencias necesarias, ejecuta:

```bash
bash install_deps.sh
```

Esto instalará los paquetes listados en `requirements.txt`, `requirements_sprint2.txt` y otros requeridos para el funcionamiento del sistema.

## 📝 Licencia y autoría

Este proyecto es de código abierto bajo licencia MIT.

- Autor: ndrz02 (2026)
- Consulta AUTORÍA_Y_LICENCIA.md para detalles y ejemplos de cabecera.
- Consulta LICENSE para el texto completo de la licencia.

---
