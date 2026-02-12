# 🎯 PLAN DE ACCIÓN - SPRINT 1 → SPRINT 2

**Objetivo:** Completar Sprint 1 (4-6 horas) y preparar Sprint 2

---

## FASE 1: TESTING DE INFERENCIA (1 hora)

### ✅ Tarea 1.5: Crear `tests/test_inference.py`

```bash
# Crear el archivo de testing
touch tests/test_inference.py
```

**Contenido esperado:**
- Test de carga de cada backend
- Benchmark de velocidad
- Validación de formato de salida
- Test de fallback entre backends

**Checklist:**
- [ ] Archivo creado
- [ ] Tests pasan sin errores
- [ ] Coverage > 80%

---

## FASE 2: MEMORIA SIMPLIFICADA (2-3 horas)

### Tarea 2.1: `core/memory/conversation_store.py` (45 min)

**Responsabilidad:** Gestionar últimas 10 conversaciones activas

```python
# Estructura
class ConversationStore:
    def add_conversation(self, user_id: str, conversation_data: dict) -> None
    def get_conversation(self, conversation_id: str) -> Optional[dict]
    def list_conversations(self, user_id: str, limit: int = 10) -> List[dict]
    def delete_conversation(self, conversation_id: str) -> None
    def clear_old(self, hours: int = 24) -> int  # Elimina conversaciones antiguas
```

**Fuente:** Extraer de `conversation_manager.py` (simplificar)

**Checklist:**
- [ ] Archivo creado
- [ ] Métodos CRUD implementados
- [ ] Test básico funciona

---

### Tarea 2.2: `core/memory/project_store.py` (45 min)

**Responsabilidad:** Gestionar resúmenes de proyectos (NO raw text)

```python
class ProjectStore:
    def create_project_summary(self, project_id: str, summary: dict) -> None
    def get_project_summary(self, project_id: str) -> Optional[dict]
    def search_projects(self, keywords: List[str]) -> List[dict]
    def update_project_metadata(self, project_id: str, metadata: dict) -> None
    def list_all_projects(self) -> List[dict]
```

**Metadatos:** ID, fecha, tags, keywords, embeddings_pointer (apunta a PC2)

**Checklist:**
- [ ] Archivo creado
- [ ] Métodos implementados
- [ ] Test básico funciona

---

### Tarea 2.3: `core/memory/semantic_index.py` (45 min)

**Responsabilidad:** Interfaz para consultar embeddings vectoriales (en PC2)

```python
class SemanticIndex:
    def __init__(self, pc2_host: str = "localhost:9999"):
        # Conecta a PC2
    
    def search_similar(self, query_embedding: List[float], top_k: int = 5) -> List[dict]
    def add_embedding(self, text_id: str, embedding: List[float], metadata: dict) -> None
    def get_embedding_status(self) -> dict  # Stats desde PC2
```

**Nota:** Aún no hay implementación en PC2, pero definimos la interfaz

**Checklist:**
- [ ] Interfaz definida (sin implementación backend)
- [ ] Métodos stubbed
- [ ] Documentación clara

---

### Tarea 2.4: `core/apis/memory_api.py` (30 min)

**Responsabilidad:** Definir contrato de comunicación

```python
# Protocolos para RPC entre PC1 y PC2
class MemoryAPI:
    """Contrato para comunicación memoria entre nodos"""
    
    GET_CONVERSATION = "memory.get_conversation"
    GET_PROJECT_SUMMARY = "memory.get_project_summary"
    SEARCH_SIMILAR = "memory.search_similar"
    SYNC_EMBEDDINGS = "memory.sync_embeddings"
```

**Checklist:**
- [ ] APIs definidas
- [ ] Documentación clara
- [ ] Compatible con JSON-RPC

---

### Tarea 2.5: `tests/test_memory.py` (30 min)

**Contenido:**
- CRUD tests para stores
- Test de límites (máx 10 conversaciones)
- Test de limpieza automática

**Checklist:**
- [ ] Archivo creado
- [ ] Tests pasan
- [ ] Coverage > 70%

---

## FASE 3: ORQUESTADOR (1-2 horas)

### Tarea 3.1: `orchestrator/routes/router.py` (45 min)

**Responsabilidad:** Decidir qué tipo de procesamiento necesita la query

```python
class QueryRouter:
    def route(self, query: str, context: dict) -> RoutingDecision
    
    # Posibles rutas:
    # 1. inference_only: Solo generar respuesta (→ PC1)
    # 2. needs_context: Buscar contexto primero (→ PC2)
    # 3. synthesis: Múltiples fuentes (→ PC2)
```

**Lógica:**
```
¿Es pregunta simple? → inference_only
¿Menciona proyectos/archivos? → needs_context
¿Pide comparación/síntesis? → synthesis
```

**Checklist:**
- [ ] Archivo creado
- [ ] Lógica implementada
- [ ] Test routing funciona

---

### Tarea 3.2: `orchestrator/planning/query_planner.py` (30 min)

**Responsabilidad:** Planificar pasos de ejecución

```python
class QueryPlanner:
    def plan(self, query: str, route: RoutingDecision) -> ExecutionPlan
    
    # Plan = lista de pasos ordenados a ejecutar
    # Ej: [fetch_context, generate, validate]
```

**Checklist:**
- [ ] Archivo creado
- [ ] Plan básico implementado
- [ ] Test funciona

---

### Tarea 3.3: `orchestrator/synthesis/response_synthesizer.py` (30 min)

**Responsabilidad:** Combinar resultados de múltiples fuentes

```python
class ResponseSynthesizer:
    def synthesize(self, results: List[dict], query: str) -> str
    
    # Combina: [context de PC2] + [generación de PC1] → respuesta coherente
```

**Checklist:**
- [ ] Archivo creado
- [ ] Síntesis básica funciona
- [ ] Test pasa

---

### Tarea 3.4: `orchestrator/main.py` (15 min)

**Responsabilidad:** Punto de entrada del servicio

```python
# Estructura base para ejecutar orquestador
class Orchestrator:
    def __init__(self):
        self.router = QueryRouter()
        self.planner = QueryPlanner()
        self.synthesizer = ResponseSynthesizer()
    
    def process(self, query: str, user_id: str) -> str:
        route = self.router.route(query, {})
        plan = self.planner.plan(query, route)
        # ... ejecutar plan
        return respuesta

if __name__ == "__main__":
    orchestrator = Orchestrator()
    print(orchestrator.process("Hola, ¿cómo estás?", "user123"))
```

**Checklist:**
- [ ] Archivo creado
- [ ] Integración básica funciona

---

## TESTING FINAL SPRINT 1

### Crear `tests/test_sprint1_integration.py`

```python
# Test que valida toda la FASE 1-3
# 1. Carga inference engine
# 2. Carga memory stores
# 3. Carga orchestrator
# 4. Ejecuta query end-to-end
```

**Criterios de Éxito:**
- ✅ Todos los módulos se importan sin errores
- ✅ Inference engine genera texto
- ✅ Memory stores funcionan
- ✅ Router hace routing
- ✅ Response synthesizer combina resultados

---

## 📊 TIMELINE ESTIMADO

| Tarea | Tiempo | Total |
|-------|--------|-------|
| 1.5 Testing Inferencia | 1 hora | 1h |
| 2.1 Conversation Store | 45 min | 1h 45m |
| 2.2 Project Store | 45 min | 2h 30m |
| 2.3 Semantic Index | 45 min | 3h 15m |
| 2.4 Memory API | 30 min | 3h 45m |
| 2.5 Test Memory | 30 min | 4h 15m |
| 3.1 Router | 45 min | 5h |
| 3.2 Query Planner | 30 min | 5h 30m |
| 3.3 Response Synthesizer | 30 min | 6h |
| 3.4 Main | 15 min | 6h 15m |
| Integration Test | 30 min | 6h 45m |
| **TOTAL** | | **~7 horas** |

**Realista:** 4-6 horas (con pausa, café, etc.)

---

## 🚀 SPRINT 2: Vista Previa

Una vez completado Sprint 1:

### FASE 4: Procesamiento (PC2)
- `processing/ingestion/document_processor.py` refactorizado
- `processing/embeddings/embedding_engine.py` (genera vectores)
- `processing/indexing/vector_index.py` (FAISS/ChromaDB)

### FASE 5: Infrastructure
- `infrastructure/systemd/` - Servicios automáticos
- `infrastructure/monitoring/` - Health checks
- `infrastructure/jobs/` - Tareas nocturas (síntesis)

### FASE 6: API + CLI
- `FastAPI` endpoint REST
- `WebSocket` streaming
- CLI interactiva

---

## 💡 RECOMENDACIONES

1. **Implementa en orden** - Cada tarea depende de la anterior
2. **Crea tests después de cada tarea** - No al final
3. **Verifica imports** - Asegúrate que no hay dependencias cruzadas
4. **Documenta mientras haces** - Código + docstrings = claro

---

## ⚡ COMANDO PARA EMPEZAR

```bash
# Ir al directorio raíz
cd /home/ndrz02/keys_1

# Crear estructura de testing
touch tests/test_inference.py tests/test_memory.py tests/test_sprint1_integration.py

# Crear archivos de memoria
touch core/memory/__init__.py
touch core/memory/conversation_store.py
touch core/memory/project_store.py
touch core/memory/semantic_index.py

# Crear archivos de APIs
touch core/apis/__init__.py
touch core/apis/memory_api.py

# Crear archivos de orquestador
touch orchestrator/__init__.py
touch orchestrator/main.py
touch orchestrator/routes/__init__.py
touch orchestrator/routes/router.py
touch orchestrator/planning/__init__.py
touch orchestrator/planning/query_planner.py
touch orchestrator/synthesis/__init__.py
touch orchestrator/synthesis/response_synthesizer.py
```

¡Listo para empezar! 🎯
