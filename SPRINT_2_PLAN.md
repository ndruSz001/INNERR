# 🚀 SPRINT 2 - PROCESAMIENTO DISTRIBUIDO

**Fecha Inicio:** 12 de Febrero de 2026  
**Duración Estimada:** 12-16 horas  
**Objetivo:** Agregar procesamiento distribuido en PC2 (embeddings, indexación, síntesis)

---

## 📋 ESTADO ACTUAL

**Sprint 1: ✅ COMPLETADO**
- ✅ Inferencia (PC1)
- ✅ Memoria 3-capas (PC1)
- ✅ Orquestador (PC2)

**Sprint 2: ⏳ PRÓXIMO** (4 fases)

---

## 🎯 SPRINT 2 - FASES

### FASE 4: Procesamiento Distribuido (PC2)
**Duración:** 4-5 horas

```
processing/
├── ingestion/
│   ├── __init__.py
│   ├── document_ingester.py      ← Refactorizado de document_processor.py
│   └── text_cleaner.py            ← Limpieza de texto
│
├── embeddings/
│   ├── __init__.py
│   ├── embedding_engine.py        ← Genera embeddings (Sentence Transformers)
│   └── embedding_cache.py         ← Cache de embeddings
│
└── indexing/
    ├── __init__.py
    ├── vector_index.py            ← FAISS o ChromaDB
    └── index_manager.py           ← Manejo de índices
```

**Tareas:**
1. **4.1** `processing/ingestion/document_ingester.py` (45 min)
   - Extraer de `document_processor.py`
   - Limpiar y modularizar
   - Interfaz simple: ingest(text) → metadata

2. **4.2** `processing/embeddings/embedding_engine.py` (60 min)
   - Usar Sentence Transformers (all-MiniLM-L6-v2)
   - Generar vectores de dimensión 384
   - Interfaz: embed_text(text) → List[float]

3. **4.3** `processing/indexing/vector_index.py` (45 min)
   - FAISS para índice local
   - Operaciones: add, search, delete
   - Interfaz: search_similar(embedding, top_k) → List[{id, score}]

4. **4.4** `infrastructure/jobs/nightly_synthesis.py` (30 min)
   - Job que ejecuta cada noche
   - Resume conversaciones antiguas
   - Genera embeddings de resúmenes
   - Limpia conversaciones de RAM

---

### FASE 5: Infrastructure & Monitoring
**Duración:** 4-5 horas

```
infrastructure/
├── systemd/
│   ├── tars-pc1-cognitivo.service
│   ├── tars-pc2-procesamiento.service
│   └── README.md (instrucciones)
│
├── monitoring/
│   ├── __init__.py
│   ├── health_checker.py           ← Health checks periódicos
│   ├── metrics_collector.py        ← Recopila métricas
│   └── alerting.py                 ← Alertas (logs)
│
├── jobs/
│   ├── __init__.py
│   ├── nightly_synthesis.py        ← Síntesis noctorna
│   ├── cleanup_old_data.py         ← Limpieza automática
│   └── scheduler.py                ← APScheduler scheduler
│
└── logging/
    ├── __init__.py
    └── logger_config.py             ← Configuración centralizada
```

**Tareas:**
1. **5.1** Systemd Services (45 min)
   - Crear servicios para PC1 y PC2
   - Auto-restart en crash
   - Logging a archivos

2. **5.2** Health Checks (45 min)
   - Verificar que módulos están vivos
   - API health endpoint
   - Notificaciones de fallos

3. **5.3** Nightly Jobs (30 min)
   - Ejecutar síntesis de conversaciones
   - Generar embeddings
   - Optimizar índice

4. **5.4** Logging Centralizado (30 min)
   - Logs a archivos con rotation
   - Formato consistente
   - Níveis: INFO, WARNING, ERROR, DEBUG

---

### FASE 6: API REST + CLI
**Duración:** 3-5 horas

```
api/
├── __init__.py
├── main.py                         ← FastAPI app
├── routes/
│   ├── __init__.py
│   ├── chat.py                     ← POST /chat/query
│   ├── memory.py                   ← GET /memory/conversations
│   ├── projects.py                 ← GET /projects
│   └── health.py                   ← GET /health
│
└── schemas.py                       ← Pydantic models

cli/
├── __init__.py
└── main.py                          ← CLI interactiva con argparse
```

**Tareas:**
1. **6.1** FastAPI REST API (75 min)
   - Endpoint POST /chat/query
   - Endpoint GET /memory/*
   - WebSocket streaming (opcional)
   - Autenticación simple (API keys)

2. **6.2** CLI Interactiva (45 min)
   - Interactive REPL
   - Comandos: `/memory`, `/projects`, `/health`
   - Colores y formatting
   - Historial con arrow keys

3. **6.3** Documentación & Testing (30 min)
   - Swagger/OpenAPI docs
   - Tests de endpoints
   - README actualizado

---

## 📊 TIMELINE SPRINT 2

| Fase | Tareas | Tiempo | Total |
|------|--------|--------|-------|
| 4 | Procesamiento | 4 tareas | 3h | 3h |
| 5 | Infrastructure | 4 tareas | 2.5h | 5.5h |
| 6 | API + CLI | 3 tareas | 2.5h | 8h |
| Testing & Docs | | 1h | 9h |
| **TOTAL** | | | **~9-10 horas** |

**Realista: 12-16 horas** (con debugging, pausa, ajustes)

---

## 🏗️ ARQUITECTURA SPRINT 2

```
┌─────────────────────────────────────────────────────────────────┐
│                  TARS DISTRIBUIDO (SPRINT 2)                    │
├──────────────────────────────────┬──────────────────────────────┤
│                                  │                              │
│  PC1: NODO COGNITIVO             │  PC2: NODO PROCESAMIENTO     │
│  (Inferencia, Síntesis)          │  (Embeddings, Indexación)    │
│                                  │                              │
│  ┌────────────────────────────┐  │  ┌──────────────────────────┐│
│  │ core/inference/            │  │  │ processing/ingestion/    ││
│  │ core/memory/               │  │  │ processing/embeddings/   ││
│  │ core/apis/                 │  │  │ processing/indexing/     ││
│  │                            │  │  │                          ││
│  │ ┌──────────────────────┐   │  │  │ ┌──────────────────────┐││
│  │ │ CLI/API (FastAPI)    │   │  │  │ │ RPC Server           │││
│  │ │ PORT 8000            │   │  │  │ │ PORT 9999            │││
│  │ └──────────────────────┘   │  │  │ └──────────────────────┘││
│  │                            │  │  │                          ││
│  │ ┌──────────────────────┐   │  │  │ ┌──────────────────────┐││
│  │ │ orchestrator/        │   │  │  │ │ infrastructure/      │││
│  │ │ (Router, Planner)    │   │  │  │ │ (Jobs, Monitoring)   │││
│  │ └──────────────────────┘   │  │  │ └──────────────────────┘││
│  │                            │  │  │                          ││
│  └────────────────────────────┘  │  └──────────────────────────┘│
│                                  │                              │
│  Servicio: tars-pc1-cognitivo.service                           │
│  Autostart: systemd                                             │
│                                  │  Servicio: tars-pc2-proc...  │
│                                  │  Autostart: systemd         │
│                                  │                              │
└──────────────────────────────────┴──────────────────────────────┘

RED DISTRIBUIDA:
┌─ PC1 (8000: API, 9999: Client RPC)
│
└─ PC2 (9999: Server RPC, 5555: Embeddings Service)
   ├─ FAISS Index (128 GB de RAM)
   ├─ PostgreSQL (metadata)
   └─ Nightly Jobs (02:00 AM)
```

---

## 📌 DEPENDENCIAS SPRINT 2

```
sentence-transformers==2.2.2        # Embeddings
faiss-cpu==1.7.4                    # Vector index (o faiss-gpu)
fastapi==0.104.1                    # REST API
uvicorn==0.24.0                     # ASGI server
pydantic==2.5.0                     # Data validation
apscheduler==3.10.4                 # Job scheduler
psutil==5.9.0                       # System monitoring
aiohttp==3.9.1                      # Async HTTP client
```

**Instalar en ambas PCs:**
```bash
pip install -r requirements_sprint2.txt
```

---

## 🎯 CHECKPOINTS SPRINT 2

### Checkpoint 1: FASE 4 Completa
- [ ] Ingestion funciona
- [ ] Embedding engine genera vectores
- [ ] FAISS index guarda y busca
- [ ] Nightly job se ejecuta sin errores

### Checkpoint 2: FASE 5 Completa
- [ ] Systemd services creados
- [ ] Health checks pasan
- [ ] Logs se escriben correctamente
- [ ] Jobs ejecutan en horario

### Checkpoint 3: FASE 6 Completa
- [ ] FastAPI API responde en /health
- [ ] CLI interactiva funciona
- [ ] Documentación completa
- [ ] Tests de integración pasan

### FINAL: SPRINT 2 COMPLETO
- [ ] Ambas PCs corren 24/7 sin crashes
- [ ] RPC entre PC1 y PC2 sincronizado
- [ ] API lista para usuarios
- [ ] Arquitectura escalable (agregar PC3 = solo config)

---

## 💡 DECISIONES ARQUITECTÓNICAS SPRINT 2

### 1. Sentence Transformers vs Otros
**Elegido:** Sentence Transformers (all-MiniLM-L6-v2)
- ✅ Rápido (inferencia <100ms)
- ✅ Dimensión compacta (384)
- ✅ Funciona bien en español
- ✅ Memory efficient (no GPU requerida)

### 2. FAISS vs ChromaDB
**Elegido:** FAISS
- ✅ Más rápido para búsqueda
- ✅ Mejor para millones de vectores
- ✅ Menos overhead
- ❌ Requiere almacenamiento manual de metadata

### 3. FastAPI vs Flask
**Elegido:** FastAPI
- ✅ Async/await nativo
- ✅ Validación automática (Pydantic)
- ✅ Docs automáticas (Swagger)
- ✅ WebSocket soporte

### 4. JSON-RPC vs gRPC
**Elegido:** JSON-RPC (HTTP)
- ✅ Simple de implementar
- ✅ Fácil de debuggear
- ✅ Funciona en cualquier lenguaje
- ❌ Más lento que gRPC (aceptable para este caso)

---

## 🚀 SIGUIENTE DESPUÉS DE SPRINT 2

**SPRINT 3: Autonomía 24/7**
- Watchdog (reinicia servicios si caen)
- Backup automático de índices
- Replicación PC2 → PC3
- Clustering de inferencia

**SPRINT 4: UI Web**
- Frontend React/Vue
- Dashboard de memoria
- Editor de proyectos
- Chat en tiempo real

**SPRINT 5: Multilingüe + Voz**
- Soporte múltiples idiomas
- Speech-to-text
- Text-to-speech
- Interfaz por voz

---

## 📝 PRÓXIMAS ACCIONES

1. **Ahora:** Comienza FASE 4
   ```bash
   cd /home/ndrz02/keys_1
   
   # Crear estructura
   mkdir -p processing/ingestion processing/embeddings processing/indexing
   touch processing/__init__.py
   touch processing/ingestion/__init__.py
   touch processing/embeddings/__init__.py
   touch processing/indexing/__init__.py
   ```

2. **Después Fase 4:** Comienza Fase 5
3. **Después Fase 5:** Comienza Fase 6
4. **Después Fase 6:** Integración y testing final

---

## 📞 RECURSOS

- Sentence Transformers: https://www.sbert.net/
- FAISS: https://github.com/facebookresearch/faiss
- FastAPI: https://fastapi.tiangolo.com/
- APScheduler: https://apscheduler.readthedocs.io/

---

**Estado:** 🟢 LISTO PARA COMENZAR SPRINT 2
**Última Actualización:** 12 FEB 2026, 10:26
