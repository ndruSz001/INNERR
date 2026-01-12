# Diario de Desarrollo - TARS IA Personal

## Fecha: 7 de enero de 2026
- **Inicio del Proyecto**: Configuración inicial de seguridad con Streamlit. Perfiles preparados para familia.
- **Objetivos**: Desarrollar IA sólida para prototipos médicos, escalable a familia.
- **Próximos Pasos**: Integrar PA-LLaVA para visión por computadora.

## Fecha: 7 de enero de 2026 (Actualización)
- **Estructura Modular**: Creado `__init__.py` para paquete Python. Actualizado `requirements.txt` con dependencias para visión y datos.
- **Normas Agregadas**: Incorporadas secciones de ciberseguridad, computación y ética médica en README.
- **Reto Fase 2**: Preparado para etiquetado de componentes en imágenes con PA-LLaVA.
- **Próximos Pasos**: Instalar dependencias y empezar experimentos en notebooks.

## Fecha: 07-01-2026
Objetivo: Conexión de TARS con hardware local (RTX 3050) y preparación para cluster de 35 nodos.  
Tarea: Configurar core_ia.py para que el modelo PA-LLaVA pueda ejecutarse en modo "Inferencia" en mi laptop y modo "Entrenamiento" en el cluster de resonancia.  
Nota de Seguridad: Se ha implementado el aislamiento de carpetas por familiar para cumplir con la privacidad [cite: 2026-01-07].

## Fecha: 7 de enero de 2026 - Voz Avanzada y Futuras Expansiones
- **Script voz_tars.py**: Creado script de voz con wake word ("Hey TARS"), TTS automático, y procesamiento local.
- **Wake Word**: Evita escucha constante, activa solo con palabra clave.
- **Futuras Expansiones Preparadas**: Comentarios para TTS avanzado (Piper/Sherpa-ONNX), reconocimiento de voz familiar, integración clúster, y seguridad multiusuario.
- **Exclusivo para Ndrz**: Por ahora, enfocado en usuario principal; expansiones futuras comentadas.
- **Próximo**: Probar script de voz y refinar personalidad.