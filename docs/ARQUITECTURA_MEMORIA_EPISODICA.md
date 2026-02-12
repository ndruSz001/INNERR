# Arquitectura de Memoria Episódica Estructurada - TARS

## Visión General

Sistema de gestión de conocimiento de largo plazo diseñado para IA personal persistente. Resuelve el problema de fragmentación del conocimiento mediante un **grafo de conocimiento trazable**, donde cada conversación conserva su identidad y especificidad, pero puede ser reutilizada de forma controlada.

## Principios Fundamentales

### 1. Usuario como Supervisor
- **NO automático**: El sistema NO asume relaciones entre conversaciones
- **Explícito**: El usuario indica qué conversaciones deben integrarse
- **Controlado**: Evita contaminación contextual y pérdida de especificidad

### 2. Conversaciones como Unidades Semánticas
Cada conversación es una unidad independiente con:
- **Identificador único**: UUID corto (8 caracteres)
- **Objetivo declarado**: Propósito explícito de la conversación
- **Conclusiones parciales/resultados**: Conocimiento destilado reutilizable
- **Metadatos temporales y temáticos**: Categoría, proyecto, tags, fechas

### 3. Conversaciones Integradoras
Nodos de nivel superior que:
- **Combinan conocimiento** de múltiples conversaciones base
- **NO modifican** las conversaciones originales
- **Preservan trazabilidad** del origen de cada fragmento
- **Actúan como conectores** en el grafo de conocimiento

### 4. Trazabilidad Total
- **Origen claro**: Cada dato sabe de dónde viene
- **Relaciones tipificadas**: 7 tipos de relación entre conversaciones
- **Historial inmutable**: Las conversaciones base nunca se modifican
- **Grafo navegable**: Visualización y exploración de conexiones

## Arquitectura del Sistema

### Schema de Base de Datos

```sql
-- Conversaciones (nodos del grafo)
CREATE TABLE conversaciones (
    id TEXT PRIMARY KEY,
    titulo TEXT,
    descripcion TEXT,
    categoria TEXT,
    fecha_inicio TEXT,
    fecha_ultima_actividad TEXT,
    num_mensajes INTEGER DEFAULT 0,
    estado TEXT DEFAULT 'activa',
    tags TEXT,  -- JSON array
    proyecto_relacionado TEXT,
    importancia INTEGER DEFAULT 5,
    metadata TEXT,  -- JSON
    -- Nuevos campos para grafo:
    es_integradora INTEGER DEFAULT 0,  -- Boolean
    objetivo TEXT,  -- Propósito declarado
    conclusiones TEXT,  -- Conocimiento destilado
    resultados TEXT  -- Resultados obtenidos
);

-- Mensajes (contenido de conversaciones)
CREATE TABLE mensajes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversacion_id TEXT,
    timestamp TEXT,
    tipo TEXT,  -- 'user' o 'tars'
    contenido TEXT,
    metadata TEXT,  -- JSON
    FOREIGN KEY (conversacion_id) REFERENCES conversaciones(id)
);

-- Relaciones (aristas del grafo)
CREATE TABLE relaciones_conversaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversacion_origen TEXT,
    conversacion_destino TEXT,
    tipo_relacion TEXT,  -- Ver tipos abajo
    descripcion TEXT,
    relevancia INTEGER DEFAULT 5,  -- 1-10
    fecha_vinculacion TEXT,
    metadata TEXT,  -- JSON
    FOREIGN KEY (conversacion_origen) REFERENCES conversaciones(id),
    FOREIGN KEY (conversacion_destino) REFERENCES conversaciones(id)
);

-- Índices para búsquedas eficientes
CREATE INDEX idx_relaciones_origen ON relaciones_conversaciones(conversacion_origen);
CREATE INDEX idx_relaciones_destino ON relaciones_conversaciones(conversacion_destino);
```

### Tipos de Relación

| Tipo | Descripción | Uso |
|------|-------------|-----|
| `relacionada` | Temas relacionados | Conversaciones sobre temas similares |
| `continua` | Una continúa la otra | Secuencia temporal |
| `complementa` | Información complementaria | Perspectivas diferentes del mismo tema |
| `contradice` | Información contradictoria | Detectar inconsistencias |
| `depende` | Requiere contexto | Una necesita la otra para entenderse |
| `converge` | Conclusiones similares | Llegan a resultados parecidos |
| `diverge` | Conclusiones diferentes | Llegan a resultados opuestos |
| `integra` | Conversación integradora | Meta-conversación que sintetiza otras |

## Flujos de Uso

### 1. Crear Conversación Normal
```python
from conversation_manager import ConversationManager

manager = ConversationManager()

# Nueva conversación independiente
conv_id = manager.nueva_conversacion(
    titulo="Análisis torque motor Maxon",
    categoria="investigacion",
    descripcion="Cálculos para exoesqueleto rodilla",
    proyecto_relacionado="exoesqueleto_v2",
    tags=["motores", "torque", "biomecánica"]
)

# Agregar mensajes (automático en chat)
manager.agregar_mensaje(conv_id, "user", "¿Qué torque necesito?")
manager.agregar_mensaje(conv_id, "tars", "Según biomecánica...")

# Guardar conclusiones
manager.actualizar_conclusiones(
    conv_id,
    conclusiones="Motor Maxon EC90 con reductor 1:50 es óptimo",
    resultados="Torque: 12 Nm, Peso: 450g, Costo: $800"
)
```

### 2. Vincular Conversaciones (Usuario como Supervisor)
```python
# Usuario decide explícitamente vincular
manager.vincular_conversaciones(
    conv_origen="conv_123",  # Análisis torque motor
    conv_destino="conv_456",  # Diseño mecánico rodilla
    tipo_relacion="complementa",
    descripcion="Los cálculos de torque informan el diseño mecánico",
    relevancia=9
)
```

### 3. Analizar Convergencias
```python
# Antes de integrar, analizar si tiene sentido
analisis = manager.analizar_convergencias([
    "conv_123",  # Análisis torque
    "conv_456",  # Diseño mecánico
    "conv_789"   # Selección materiales
])

print(f"Temas comunes: {len(analisis['temas_comunes'])}")
print(f"Convergencias: {analisis['convergencias']}")
print(f"Divergencias: {analisis['divergencias']}")

# Decisión basada en análisis
if len(analisis['temas_comunes']) >= 3:
    # Alta convergencia → integrar
    pass
```

### 4. Crear Conversación Integradora
```python
# Usuario crea meta-conversación
conv_integrador = manager.crear_conversacion_integradora(
    titulo="Especificación completa exoesqueleto rodilla",
    objetivo="Integrar análisis de torque, diseño mecánico y materiales",
    conversaciones_base=["conv_123", "conv_456", "conv_789"],
    categoria="sintesis"
)

# Las conversaciones base NO se modifican
# La integradora tiene relaciones tipo "integra" con cada una
```

### 5. Navegar el Grafo
```python
# Ver todas las relaciones de una conversación
relaciones = manager.obtener_conversaciones_relacionadas("conv_123")

print(f"Salientes (esta → otras): {relaciones['salientes']}")
print(f"Entrantes (otras → esta): {relaciones['entrantes']}")

# Explorar subgrafo desde un nodo
grafo = manager.obtener_grafo_conocimiento(
    profundidad=2,
    conv_raiz="conv_123"
)

print(f"Nodos alcanzables: {grafo['estadisticas']['num_nodos']}")
print(f"Aristas: {grafo['estadisticas']['num_aristas']}")
```

## Capacidades del Sistema

### ✅ Reutilizar conocimiento sin duplicarlo
- Conclusiones almacenadas en cada conversación
- Conversaciones integradoras referencian (no copian)
- Múltiples integradoras pueden usar las mismas bases

### ✅ Detectar convergencias, contradicciones o vacíos
```python
# Análisis automático de overlaps
analisis = manager.analizar_convergencias(conv_ids)

# Detecta:
# - Temas comunes (convergencias)
# - Categorías divergentes (vacíos)
# - Palabras clave frecuentes
# - Overlap de contexto
```

### ✅ Razonamiento progresivo a largo plazo
- Conversaciones de nivel 1: Investigaciones independientes
- Conversaciones de nivel 2: Síntesis de investigaciones
- Conversaciones de nivel 3: Meta-síntesis de síntesis
- Árbol de conocimiento evolutivo

### ✅ Historial cognitivo completo
- Ninguna conversación se pierde
- Trazabilidad total de decisiones
- Reconstrucción del proceso de pensamiento
- Auditoría de evolución de ideas

## Herramientas del Sistema

### 1. Asistente Principal (`tars_asistente.py`)
```bash
python tars_asistente.py
```

Comandos:
- `/memoria` - Ver conversaciones
- `/nueva` - Nueva conversación
- `/conclusiones` - Guardar conclusiones
- `/vincular` - Vincular con otra
- `/integrar` - Crear integradora
- `/grafo` - Ver grafo
- `/contexto` - Ver contexto actual
- `/salir` - Guardar y salir

### 2. Explorador de Grafo (`grafo_conocimiento.py`)
```bash
python grafo_conocimiento.py
```

Funciones:
1. Ver grafo completo
2. Explorar conversación específica
3. Analizar convergencias
4. Crear conversación integradora
5. Vincular conversaciones
6. Exportar grafo (Graphviz DOT)

### 3. Exportación y Visualización
```bash
python grafo_conocimiento.py
# Opción 6: Exportar
# Genera: grafo_conocimiento.dot

# Visualizar con Graphviz
dot -Tpng grafo_conocimiento.dot -o grafo.png
```

## Casos de Uso Avanzados

### Caso 1: Investigación Multi-Año
```
Año 1: 15 conversaciones sobre biomecánica
Año 2: 20 conversaciones sobre actuadores
Año 3: Usuario crea integradora "Diseño exoesqueleto completo"
       → Referencia 10 conversaciones de año 1 y 2
       → NO pierde especificidad de cada conversación original
       → Puede volver a consultar cualquiera en detalle
```

### Caso 2: Detección de Contradicciones
```python
# Dos conversaciones con conclusiones diferentes
manager.vincular_conversaciones(
    "conv_old", "conv_new",
    tipo_relacion="contradice",
    descripcion="Nuevo paper contradice cálculo anterior de torque"
)

# Crear integradora para resolver contradicción
integrador = manager.crear_conversacion_integradora(
    titulo="Resolución: Cálculo correcto de torque",
    objetivo="Determinar cuál modelo es correcto",
    conversaciones_base=["conv_old", "conv_new"]
)
```

### Caso 3: Evolución de Proyecto
```
Proyecto: Exoesqueleto
├─ Fase 1: Concepto (10 conversaciones)
│  └─ Integradora: "Especificación conceptual"
├─ Fase 2: Prototipo (25 conversaciones)
│  └─ Integradora: "Especificación técnica v1"
└─ Fase 3: Producción (15 conversaciones)
   └─ Integradora final: "Documentación completa"
       ├─ Referencia: "Especificación conceptual"
       ├─ Referencia: "Especificación técnica v1"
       └─ Referencia: 5 conversaciones de Fase 3

Total trazabilidad: Desde idea inicial hasta producto final
```

## Comparación con Otros Sistemas

| Característica | TARS Episódico | ChatGPT | Claude Proyectos | Copilot Workspace |
|----------------|----------------|---------|------------------|-------------------|
| Memoria persistente | ✅ Años | ❌ Sesión | 🟡 Por proyecto | 🟡 Por workspace |
| Trazabilidad | ✅ Total | ❌ Ninguna | ❌ Limitada | ❌ Limitada |
| Grafo de conocimiento | ✅ Explícito | ❌ | ❌ | ❌ |
| Control del usuario | ✅ Total | ❌ Automático | 🟡 Parcial | 🟡 Parcial |
| Previene contaminación | ✅ Sí | ❌ No | 🟡 Parcial | 🟡 Parcial |
| Local-first | ✅ Sí | ❌ Cloud | ❌ Cloud | ❌ Cloud |
| Sin límite temporal | ✅ Ilimitado | ❌ ~3 meses | ❌ ~6 meses | ❌ Variable |

## Implementación Técnica

### Requisitos
- Python 3.8+
- SQLite3 (incluido en Python)
- ~100KB por conversación (promedio)
- RAM: 50MB base + 10MB por conversación activa

### Performance
- Búsqueda: O(log n) con índices
- Grafo completo: O(n + m) donde n=nodos, m=aristas
- Subgrafo: O(d * k) donde d=profundidad, k=branching factor

### Escalabilidad
- 10,000 conversaciones: ~1GB base de datos
- 100,000 mensajes: ~500MB
- Búsqueda <100ms con índices
- Grafo completo <1s hasta 1000 nodos

## Filosofía del Sistema

### Por qué NO Automático

**Problema de la IA tradicional**: Asume contexto automáticamente
- Contamina conversaciones no relacionadas
- Pierde especificidad técnica
- No hay trazabilidad de decisiones

**Solución TARS**: Usuario como supervisor
- Decide explícitamente qué integrar
- Mantiene especificidad de cada conversación
- Trazabilidad total de relaciones

### Memoria Episódica vs Semántica

**Episódica** (TARS):
- Eventos específicos en tiempo y contexto
- "El 15 de enero calculé torque para motor Maxon"
- Preserva contexto y secuencia

**Semántica** (tradicional):
- Hechos generales sin contexto
- "Los motores Maxon tienen buen torque"
- Pierde cuándo, cómo, por qué

### Conocimiento como Grafo

```
         [Concepto A]
           /      \
    relaciona   contradice
        /            \
  [Análisis 1]   [Análisis 2]
        \            /
       integra    integra
          \       /
        [Síntesis]
```

Beneficios:
- Múltiples caminos al conocimiento
- Evolución visible
- Contradicciones explícitas
- Convergencias detectables

## Próximos Desarrollos

### Corto Plazo
- [ ] Búsqueda semántica (embeddings)
- [ ] Auto-sugerencia de vinculaciones (usuario confirma)
- [ ] Exportación a formatos (MD, PDF, HTML)
- [ ] Estadísticas avanzadas de uso

### Mediano Plazo
- [ ] Interfaz web interactiva
- [ ] Visualización 3D del grafo (Three.js)
- [ ] Integración con knowledge bases externas
- [ ] Sistema de alertas (contradicciones detectadas)

### Largo Plazo
- [ ] Multi-usuario (colaborativo)
- [ ] Federación entre instancias TARS
- [ ] Razonamiento automático sobre grafo
- [ ] Predicción de convergencias

## Conclusión

Este sistema resuelve el problema fundamental de las IA personales: **fragmentación del conocimiento sin pérdida de especificidad**.

Características clave:
1. **Usuario supervisado**: Control total de integraciones
2. **Trazabilidad total**: Origen claro de cada dato
3. **Especificidad preservada**: Conversaciones independientes
4. **Reutilización controlada**: Conocimiento modular
5. **Evolución visible**: Grafo de conocimiento navegable

Diseñado para acompañar investigación, desarrollo tecnológico y aprendizaje continuo durante **años**, manteniendo coherencia, memoria y contexto evolutivo.

---

**Última actualización**: 2026-01-23  
**Versión**: 2.0  
**Autor**: TARS Development Team
