# Mejoras implementadas y pendientes (Sprint actual)

1. Mejorar endpoints y documentación RPC (completado)
2. Implementar reintentos y manejo de errores en RPC (completado)
3. Agregar logs detallados de comunicación (completado)
4. Optimizar uso de recursos entre PC1 y PC2 (completado)
5. Automatizar reconexión y monitoreo de nodos (completado)
6. Documentar flujo distribuido en README (completado)
7. Agregar pruebas de carga y stress (completado)

# Mejoras Futuras para Arquitectura Distribuida

1. Balanceo dinámico de carga entre nodos (PC1/PC2 y futuros workers).
	 - Descripción: Permitir que las tareas se distribuyan automáticamente entre los nodos disponibles según su carga y capacidad.
	 - Pasos sugeridos:
		 1. Analizar el flujo actual de asignación de tareas y puntos de decisión.
		 2. Implementar un monitor de recursos (CPU, RAM, uso de GPU) en cada nodo.
		 3. Crear un módulo centralizado o distribuido que reciba métricas y decida el nodo óptimo para cada tarea.
		 4. Definir políticas de balanceo (round-robin, least-loaded, prioridad por tipo de tarea, etc.).
		 5. Probar el sistema con diferentes cargas y documentar resultados.
	 - Recomendación: Priorizar la flexibilidad para agregar nuevos nodos en el futuro.
2. Priorización de tareas según recursos disponibles y tipo de modelo.
	 - Descripción: Permitir que el sistema asigne prioridad a las tareas en función de la disponibilidad de recursos, la urgencia y el tipo de modelo o proceso requerido.
	 - Recomendaciones:
		 1. Definir criterios de prioridad: urgencia, recursos requeridos, tipo de tarea/modelo, usuario solicitante, etc.
		 2. Implementar una cola de tareas con niveles de prioridad (por ejemplo, alta, media, baja).
		 3. Ajustar dinámicamente la prioridad según el estado del sistema y la carga de trabajo.
		 4. Permitir la re-priorización manual o automática de tareas en ejecución.
		 5. Documentar el algoritmo de priorización y sus parámetros configurables.
	 - Sugerencia: Comenzar con un esquema simple y evolucionar hacia reglas más complejas según las necesidades reales.
3. Implementar caché de resultados frecuentes en ambos nodos.
4. Soporte para escalado horizontal (más de dos nodos).
5. Métricas y dashboard de monitoreo en tiempo real.
	 - Descripción: Implementar un sistema que recoja métricas clave (uso de CPU, RAM, GPU, latencia, throughput, errores) y las visualice en un dashboard accesible en tiempo real.
	 - Pasos sugeridos:
		 1. Definir las métricas más relevantes para el monitoreo de los nodos y el sistema distribuido.
		 2. Seleccionar herramientas/librerías para la recolección de métricas (por ejemplo, Prometheus, Grafana, o soluciones ligeras personalizadas).
		 3. Instrumentar el código de los nodos para exponer métricas mediante endpoints o logs estructurados.
		 4. Configurar un dashboard centralizado que permita visualizar el estado y la evolución de los recursos y tareas.
		 5. Establecer alertas automáticas para condiciones críticas (caídas, sobrecarga, errores recurrentes).
	 - Recomendación: Priorizar la facilidad de integración y la visualización clara para el equipo de desarrollo.
6. Seguridad: autenticación y autorización en endpoints RPC.
7. Tolerancia a fallos avanzada: failover automático y persistencia de tareas.
	 - Descripción: Garantizar la continuidad del servicio ante fallos de nodos o caídas de red, minimizando la pérdida de tareas y permitiendo la recuperación automática.
	 - Pasos sugeridos:
		 1. Implementar un sistema de detección de fallos (heartbeat, health checks periódicos entre nodos).
		 2. Desarrollar mecanismos de failover automático: reasignación de tareas activas a nodos disponibles en caso de caída.
		 3. Persistir el estado de las tareas en una base de datos o almacenamiento compartido para evitar pérdidas.
		 4. Probar escenarios de fallo simulando caídas y recuperaciones de nodos.
		 5. Documentar el flujo de recuperación y las limitaciones conocidas.
	 - Recomendación: Priorizar la simplicidad y robustez en la primera versión, luego iterar hacia mayor sofisticación.
8. Integración con orquestadores externos (Kubernetes, Docker Swarm).
	 - Descripción: Facilitar la gestión, despliegue y escalado automático del sistema distribuido mediante orquestadores de contenedores.
	 - Sugerencias:
		 1. Adaptar los servicios y nodos para ejecutarse en contenedores (Docker).
		 2. Crear archivos de configuración para orquestadores (YAML para Kubernetes, Docker Compose, etc.).
		 3. Definir políticas de escalado automático y recuperación ante fallos usando las capacidades del orquestador.
		 4. Integrar el monitoreo y logging con herramientas compatibles del orquestador.
		 5. Documentar el proceso de despliegue y las dependencias necesarias.
	 - Recomendación: Comenzar con un entorno de pruebas y migrar gradualmente a producción.
9. Pruebas automáticas de resiliencia ante caídas de red y reinicios.
10. Documentación técnica y diagramas de arquitectura actualizados.

	 - Descripción: Mantener la documentación técnica y los diagramas de arquitectura alineados con la evolución del sistema distribuido.
	 - Recomendaciones:
		 1. Actualizar diagramas de arquitectura (componentes, flujo de datos, despliegue) tras cada cambio relevante.
		 2. Documentar nuevas funcionalidades, dependencias y configuraciones.
		 3. Incluir ejemplos de uso y casos de prueba en la documentación.
		 4. Utilizar herramientas colaborativas para mantener la documentación accesible y versionada.
		 5. Revisar y validar la documentación con el equipo periódicamente.
	 - Sugerencia: Priorizar la claridad y la actualización continua para facilitar el onboarding y el mantenimiento.
# Notas
- Mantener este archivo como referencia para el roadmap de mejoras distribuidas.
- Revisar y actualizar tras cada sprint o mejora significativa.
