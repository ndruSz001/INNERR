# REESTRUCTURACIÓN: 2 PCs + Cluster Distribuido

## Estado Actual Analizado

Tu proyecto tiene:
- ✅ Core IA (core_ia.py)
- ✅ ConversationManager 
- ✅ Procesamiento documental
- ✅ Memoria persistente
- ✅ 2 PCs disponibles (conectadas)

## Problema a Resolver

Lógica experimental + estable mezcladas → complejidad acumulativa

## Solución: Arquitectura por Capas

```
PC 1 (NODO COGNITIVO PRINCIPAL)
├─ /core
│  ├─ Inferencia LLM
│  ├─ Conversación
│  ├─ Síntesis
│  └─ Razonamiento
└─ APIs internas estables

PC 2 (NODO PROCESAMIENTO)
├─ /orchestrator (recibe → delega → sintetiza)
├─ Embeddings
├─ Indexado vectorial
├─ Chunking documentos
└─ /lab (experimentos sin romper CORE)

COMPARTIDO
├─ /memory (BD optimizada)
├─ /models (modelos GGUF)
└─ /infrastructure (systemd, logging)
```

## Cambios Inmediatos Necesarios

1. **Separar CORE de LAB** (evitar experimentación que rompa estabilidad)
2. **Crear Orquestador** (divide responsabilidades entre PCs)
3. **Simplificar Memoria** (conversacional + proyecto + semántica)
4. **Optimizar Modelos** (pequeño→mediano→grande según tarea)
5. **Servicios systemd** (watchdog + reinicio automático)
6. **Monitoreo básico** (GPU, CPU, RAM, latencia)
7. **Jobs nocturnos en PC2** (re-síntesis, compactación)

## Próximos Pasos

→ Ejecutar diagnóstico de código actual (detectar problemas)
→ Crear estructura de directorios
→ Implementar Orquestador
→ Separar CORE de LAB
→ Añadir watchdog systemd
