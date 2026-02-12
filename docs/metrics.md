# Métricas propuestas para evaluar TARS (rápido y accionable)

- **Latency (s):** Tiempo wall-clock para generar la respuesta (promedio por prompt).
- **Tokens/sec:** Tokens generados por segundo (si es posible medir).
- **Longitud respuesta (tokens):** Mediana y rango.
- **Relevancia (1-5):** Evaluación humana rápida si la respuesta responde la pregunta.
- **Utilidad/Ayuda (1-5):** ¿La respuesta ayuda a la tarea del usuario?
- **Exactitud factual (1-5):** Verificación rápida contra la verdad conocida (spot-check).
- **Hallucination rate (%):** Fracciones de respuestas con hechos inventados (estimado).
- **Consistencia contextual (1-5):** Mantiene coherencia entre prompts relacionados.
- **CPU/RAM peak (MB):** Memoria usada durante la inferencia (desde logs o `top`).
- **Observaciones cualitativas:** ejemplos de fallos y mejoras sugeridas.

Notas:
- Priorizar métricas que puedas medir automáticamente (latency, tokens/sec, longitud, recursos).
- Métricas humanas (relevancia, utilidad, exactitud) requieren etiquetado; generar 100 ejemplos etiquetados para evaluación rápida.
