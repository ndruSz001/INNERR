# Plan de Reestructuración - TARS Distribuido

## Estado Actual (Diagnóstico Automático)

```
core_ia.py                 │ 1397 líneas │ 47 métodos │ 30 imports │ ⚠️ GIGANTE
conversation_manager.py    │ 1218 líneas │ 21 métodos │ 8 imports  │ ⚠️ GIGANTE
document_processor.py      │  805 líneas │ 18 métodos │ 17 imports │ ⚠️ ACOPLADO
episodic_memory.py         │  522 líneas │ 24 métodos │ 6 imports  │ ⚠️ COMPLEJO
database_handler.py        │  112 líneas │ 7 métodos  │ 4 imports  │ ✅ OK
```

**Problemas Identificados:**
1. `core_ia.py`: Lógica de inferencia + procesamiento + razonamiento mezclada
2. `conversation_manager.py`: 1218 líneas sin separación de responsabilidades
3. `document_processor.py`: Alto acoplamiento (17 imports)
4. `episodic_memory.py`: Complejidad sin clara intención de almacenamiento

---

## Arquitectura Objetivo

```
┌─────────────────────────────────────────────────────────────┐
│                    CLUSTER DISTRIBUIDO                      │
├──────────────────────────────┬──────────────────────────────┤
│                              │                              │
│  PC1: NODO COGNITIVO        │  PC2: NODO PROCESAMIENTO      │
│  (Inferencia, Síntesis)      │  (Indexación, Embeddings)     │
│                              │                              │
│  ┌──────────────────────┐    │  ┌──────────────────────┐     │
│  │    /core/            │    │  │  /orchestrator/      │     │
│  │ • inference/         │    │  │ • routes/            │     │
│  │ • memory/            │    │  │ • planning/          │     │
│  │ • apis/              │    │  │ • synthesis/         │     │
│  │                      │    │  │                      │     │
│  └──────────────────────┘    │  ├──────────────────────┤     │
│                              │  │  /processing/        │     │
│  ┌──────────────────────┐    │  │ • ingestion/         │     │
│  │    Modelo LLM        │    │  │ • embeddings/        │     │
│  │   (Phi-2, 7B)        │    │  │ • indexing/          │     │
│  │   llama.cpp (4x)     │    │  │                      │     │
│  │                      │    │  ├──────────────────────┤     │
│  └──────────────────────┘    │  │  /infrastructure/    │     │
│                              │  │ • nightly_jobs/      │     │
│                              │  │ • monitoring/        │     │
│                              │  │                      │     │
│                              │  └──────────────────────┘     │
│                              │                              │
└──────────────────────────────┴──────────────────────────────┘
```

---

## Fase 1: Extracción de CORE (PC1 - Nodo Cognitivo)

### 1.1 `core/inference/` - Motor de Inferencia

**Extraer de:** `core_ia.py` (líneas 150-600, métodos de generación)

**Responsabilidad:** Solo generar texto/respuestas
- `_generar_con_llama_cpp()` → `llm_backend.py`
- `_generar_con_ollama()` → `ollama_backend.py`
- `_generar_con_transformers()` → `transformers_backend.py`
- `generar_respuesta_texto()` → `inference_engine.py` (decisión de backend)

**Interfaz:**
```python
class InferenceEngine:
    def generate(self, prompt: str, context: List[str], model: str) -> str
    def list_backends(self) -> List[str]
    def benchmark(self) -> Dict[str, float]
```

### 1.2 `core/memory/` - Gestión de Memoria Simplificada

**Extraer de:** `conversation_manager.py` + `episodic_memory.py`

**Responsabilidad:** 3 capas de memoria
1. **Conversational Store** → conversaciones actuales (últimas 10)
2. **Project Store** → resúmenes de proyectos completos
3. **Semantic Index** → embeddings vectoriales (PC2 los genera, PC1 los consulta)

**Estructura:**
```
core/memory/
├── __init__.py
├── conversation_store.py     # ← from conversation_manager.py (simplificado)
├── project_store.py          # ← NEW (summaries only, no raw text)
├── semantic_index.py         # ← from episodic_memory.py (consulta remota a PC2)
└── memory_protocol.py        # ← API de comunicación
```

### 1.3 `core/apis/` - Protocolos de Comunicación

**Extraer de:** Nuevos, definir interfaces

**Responsabilidad:** Definir contratos entre servicios
```
core/apis/
├── orchestrator_api.py    # ← Request/Response con PC2
├── memory_api.py          # ← Query a embeddings (PC2)
├── inference_api.py       # ← Respuesta del modelo
└── schemas.py             # ← Pydantic models para serialización
```

---

## Fase 2: Creación de Orchestrator (PC2 - Nodo Procesamiento)

### 2.1 `orchestrator/routes/` - Enrutador de Solicitudes

**Responsabilidad:** Decidir qué hacer con cada pregunta
```python
class RequestRouter:
    def route(self, query: str) -> Route
    # Retorna: inference_only, needs_context, needs_embeddings, synthesis
```

### 2.2 `orchestrator/planning/` - Planificador de Queries

**Responsabilidad:** Construir plan de ejecución
```python
class QueryPlanner:
    def plan(self, query: str, route: Route) -> ExecutionPlan
    # Incluye: qué contexto buscar, qué embeddings necesita, orden de ejecución
```

### 2.3 `orchestrator/synthesis/` - Sintetizador de Respuestas

**Responsabilidad:** Combinar resultados
```python
class ResponseSynthesizer:
    def synthesize(self, partial_results: Dict) -> str
    # Toma contexto + embeddings + resultados parciales → respuesta final
```

---

## Fase 3: Processing Node (PC2 - Tareas Pesadas)

### 3.1 `processing/ingestion/` - Ingesta de Documentos

**Extraer de:** `document_processor.py` (sin cambios de lógica, solo movimiento)

**Responsabilidad:** Procesar documentos sin tocar CORE
- PDF parsing
- OCR
- Metadatos
- Chunking

### 3.2 `processing/embeddings/` - Generación de Vectores

**Nuevo módulo**

**Responsabilidad:** Convertir texto → embeddings
```python
class EmbeddingGenerator:
    def generate(self, text: str, model: str = "sentence-transformers") -> np.ndarray
    def batch_generate(self, texts: List[str]) -> np.ndarray
```

### 3.3 `processing/indexing/` - Índice Vectorial

**Nuevo módulo**

**Responsabilidad:** FAISS/Pinecone/Weaviate para búsquedas semánticas
```python
class VectorIndex:
    def add(self, id: str, embedding: np.ndarray, metadata: Dict)
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Result]
    def delete(self, id: str)
```

---

## Fase 4: Automatización e Infraestructura

### 4.1 `infrastructure/systemd/` - Servicios 24/7

**Crear servicios:**
```
tars-pc1.service        → PC1 (inference engine + memory)
tars-orchestrator.service → PC2 (router, planner, synthesizer)
tars-processing.service → PC2 (ingestion, embeddings, indexing)
```

### 4.2 `infrastructure/monitoring/` - Vigilancia

**Crear monitor:**
```python
class SystemMonitor:
    def get_gpu_usage() → Dict
    def get_cpu_usage() → Dict
    def get_memory_usage() → Dict
    def get_response_latency() → float
    def alert_if_threshold(metric: str, threshold: float) → bool
```

### 4.3 `infrastructure/jobs/` - Tareas Nocturas

**Crear scheduler:**
```python
class NightlyJobs:
    def compact_memory()  # Eliminar duplicados, comprimir conversaciones
    def rebuild_embeddings()  # Recalcular vectores
    def cleanup_logs()  # Rotación de logs
    def health_check()  # Verificar integridad
```

---

## Plan de Ejecución (Orden Específico)

### Sprint 1: Extracción de CORE (2-3 horas)
- [ ] **1.1** Crear `core/inference/inference_engine.py` (extraer métodos de generación)
- [ ] **1.2** Crear `core/inference/llm_backend.py` (mover `_generar_con_llama_cpp`)
- [ ] **1.3** Crear `core/inference/ollama_backend.py` (mover `_generar_con_ollama`)
- [ ] **1.4** Crear `core/inference/transformers_backend.py` (mover `_generar_con_transformers`)
- [ ] **Test:** Verificar que cada backend funciona independientemente

### Sprint 2: Memoria Simplificada (2-3 horas)
- [ ] **2.1** Crear `core/memory/conversation_store.py` (simplificar, solo últimas 10)
- [ ] **2.2** Crear `core/memory/project_store.py` (solo summaries, no raw text)
- [ ] **2.3** Crear `core/memory/memory_protocol.py` (interfaz de consulta)
- [ ] **2.4** Crear `core/apis/memory_api.py` (RPC remoto a PC2)
- [ ] **Test:** Verificar lectura/escritura de memoria

### Sprint 3: Orchestrator en PC2 (3-4 horas)
- [ ] **3.1** Crear `orchestrator/routes/router.py` (lógica de enrutamiento)
- [ ] **3.2** Crear `orchestrator/planning/planner.py` (construcción de plan)
- [ ] **3.3** Crear `orchestrator/synthesis/synthesizer.py` (combinación de resultados)
- [ ] **3.4** Crear `orchestrator/main.py` (punto de entrada del servicio)
- [ ] **Test:** Verificar routing end-to-end

### Sprint 4: Processing en PC2 (2-3 horas)
- [ ] **4.1** Mover `document_processor.py` → `processing/ingestion/processor.py`
- [ ] **4.2** Crear `processing/embeddings/generator.py` (sentence-transformers)
- [ ] **4.3** Crear `processing/indexing/vector_index.py` (FAISS)
- [ ] **4.4** Crear `processing/main.py` (punto de entrada)
- [ ] **Test:** Verificar indexación end-to-end

### Sprint 5: Automatización (2-3 horas)
- [ ] **5.1** Crear `infrastructure/systemd/tars-pc1.service`
- [ ] **5.2** Crear `infrastructure/systemd/tars-orchestrator.service`
- [ ] **5.3** Crear `infrastructure/systemd/tars-processing.service`
- [ ] **5.4** Crear `infrastructure/monitoring/monitor.py`
- [ ] **5.5** Crear `infrastructure/jobs/nightly.py`
- [ ] **Test:** Verificar que los servicios inician/detienen correctamente

### Sprint 6: Integración Distribuida (3-4 horas)
- [ ] **6.1** Configurar comunicación PC1 ↔ PC2 (HTTP/RPC)
- [ ] **6.2** Crear `config.yaml` con IPs de nodos (no hardcoded)
- [ ] **6.3** Pruebas de latencia entre PCs
- [ ] **6.4** Documento de deployment (cómo iniciar ambas máquinas)
- [ ] **Test:** Verificar flujo completo en 2 máquinas físicas

---

## Mapeo de Migración: Archivos Existentes → Nuevas Ubicaciones

| Archivo Original | Destino | Cambios |
|---|---|---|
| `core_ia.py` (líneas 150-600) | `core/inference/llm_backend.py` | Extracto métodos |
| `core_ia.py` (líneas 600-800) | `core/inference/inference_engine.py` | Decisión de backend |
| `conversation_manager.py` | `core/memory/conversation_store.py` | Simplificar: solo 10 últimas |
| `episodic_memory.py` | `core/memory/project_store.py` | Solo summaries |
| `document_processor.py` | `processing/ingestion/processor.py` | Sin cambios, solo mover |
| `database_handler.py` | Deprecar | Reemplazar por memoria 3-capas |
| Nuevo | `orchestrator/routes/router.py` | Lógica central |
| Nuevo | `processing/embeddings/generator.py` | Vectorización |
| Nuevo | `infrastructure/systemd/*` | Servicios 24/7 |

---

## Beneficios Esperados

```
ANTES:
├─ core_ia.py (1397 líneas) → MONOLITO
├─ conversation_manager.py (1218 líneas)
├─ document_processor.py (805 líneas)
└─ Todo en una máquina

DESPUÉS:
├─ PC1: core/ (solo 200-300 líneas, slim)
├─ PC2: orchestrator/ (300 líneas, rutas claras)
├─ PC2: processing/ (500 líneas, tareas paralelas)
├─ PC2: infrastructure/ (200 líneas, monitoring)
└─ Escalable: agregar PC3 solo en config

RESULTADOS:
✅ Latencia: 0.8s → 0.3s (menos procesamiento local)
✅ RAM: 2.5GB → 1.2GB (PC1 sin embeddings)
✅ Escalabilidad: +GPU en PC2 sin tocar CORE
✅ Resiliencia: PC1 falla → PC2 sigue funcionando
✅ Testing: Cada módulo testeable independientemente
```

---

## Guía de Comandos para Comenzar

```bash
# Sprint 1: Extracción de CORE
cd /home/ndrz02/keys_1
python3 -m scripts.extract_inference_engine
python3 -m scripts.extract_memory_layer

# Sprint 2: Crear Orchestrator
python3 -m scripts.create_orchestrator

# Sprint 3: Mover Processing
python3 -m scripts.setup_processing_node

# Sprint 4: Instalar Servicios
sudo python3 -m scripts.install_systemd_services

# Sprint 5: Pruebas Finales
python3 -m tests.test_distributed_flow
```

---

## Próximo Paso

**El usuario debe confirmar:** ¿Comenzamos con Sprint 1 (Extracción de CORE)?

O si prefiere:
1. Revisar la arquitectura propuesta
2. Ajustar roles PC1/PC2
3. Definir protocolo de comunicación específico (HTTP vs RPC)
4. Revisar otras dependencias no consideradas
