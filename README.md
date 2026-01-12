<<<<<<< HEAD
# Funcionalidades de depuración y utilidad

## Marcar respuestas como útiles o no útiles

Durante el chat en terminal (usando `tars_terminal_chat.py`), puedes escribir:

- `útil` o `util` para marcar la última respuesta de TARS como útil
- `no útil` o `no util` para marcar la última respuesta como no útil

Esto se registra en el archivo `utilidad_respuestas_tars.txt` para que puedas revisar después qué te sirvió y qué no.

## Guardado interactivo de temas

Si escribes frases como "guarda esto", "cambiar de tema", "nueva conversación", el sistema te preguntará dónde guardar el historial antes de limpiar o cambiar de tema.

---
# TARS - IA Personal Inteligente

## Descripción
TARS es una IA personal desarrollada para acompañarme (Ndrz) en mi carrera profesional, enfocada en prototipos médicos, exoesqueletos y otras investigaciones. Diseñada para ser escalable, segura y personalizable, con expansión futura a la familia.

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
- **Privacidad por Diseño**: Todos los datos de usuarios están aislados y encriptados. No se comparten datos entre perfiles sin consentimiento explícito.
- **Autenticación Segura**: Uso de hashes SHA-256 para contraseñas. Modo exclusivo para prevenir accesos no autorizados.
- **Protección de Datos**: Cumplir con principios similares a GDPR: minimización de datos, derecho al olvido (borrar datos de usuario), y auditorías regulares.
- **Seguridad en Red**: En despliegues futuros (cluster, ESP32), usar VPN y encriptación TLS para comunicaciones.
- **Actualizaciones**: Monitorear vulnerabilidades y actualizar dependencias regularmente.

### Computación
- **Buenas Prácticas de Código**: Código modular, comentado y versionado con Git. Usar PEP 8 para estilo Python.
- **Eficiencia**: Optimizar para hardware limitado (RTX 3050 inicialmente, luego ESP32). Evitar over-engineering.
- **Versionado**: Commits descriptivos, branches para experimentos (ej. `feature/vision-module`).
- **Testing**: Implementar pruebas unitarias con pytest para validar módulos.

### Área Médica
- **Ética en Prototipos**: Todos los desarrollos médicos deben priorizar la seguridad del paciente. Documentar riesgos y obtener consentimientos informados si aplica.
- **Normativas**: Cumplir con estándares como ISO 13485 para dispositivos médicos. TARS ayudará a generar documentación regulatoria.
- **Privacidad Médica**: Datos sensibles (imágenes de resonancias) se tratan con HIPAA-like principios: acceso restringido, encriptación y no compartición.
- **Transparencia**: TARS documentará automáticamente procesos para auditorías.

## Reto para Fase 2: Módulo de Visión Robótica
Cuando integres PA-LLaVA, haz que TARS no solo analice imágenes, sino que etiquete componentes específicos:
- **Objetivo**: Detectar 'articulaciones', 'servomotores', 'estructuras' en renders de exoesqueletos.
- **Implementación**: Crea una función que use el modelo para clasificar y etiquetar objetos en la imagen subida.
- **Ejemplo**: Sube un render → TARS responde: "Detectado: 3 articulaciones, 2 servomotores. ¿Quieres simular movimiento?"
=======
# keys_1
Personali_a
>>>>>>> 80307d3bd450fd3b7e1b75094d8c34d72d565950
