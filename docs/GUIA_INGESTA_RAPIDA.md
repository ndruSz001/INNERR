# Guía de Ingesta Rápida de Información - TARS

## 🚀 Inicio Rápido

### 1. Procesar un PDF desde terminal
```bash
# Modo simple
python ingesta_rapida.py mi_paper.pdf

# Demo de funcionalidades avanzadas
python demo_pdf_avanzado.py mi_paper.pdf

# Modo interactivo
python ingesta_rapida.py
```

### 2. Uso desde código Python
```python
from core_ia import TarsVision

tars = TarsVision()

# Procesar paper científico
resultado = tars.procesar_pdf(
    "paper_biomechanics.pdf",
    categoria="paper",
    extraer_imagenes=True
)

print(f"✅ {resultado['estadisticas']['total_palabras']} palabras extraídas")
print(f"🖼️  {resultado['estadisticas']['total_imagenes']} imágenes")
```

---

## 🆕 FUNCIONALIDADES AVANZADAS

### 1. OCR para PDFs Escaneados
```python
# Para papers antiguos sin texto extraíble
resultado_ocr = tars.procesar_pdf_con_ocr(
    "paper_escaneado_1995.pdf",
    idioma="spa+eng"  # Español + Inglés
)

print(f"📝 {resultado_ocr['total_palabras']} palabras extraídas por OCR")
# Guardado automáticamente en: tars_lifelong/knowledge/ocr_results/
```

### 2. Extracción Automática de Metadatos
```python
# Extrae: Título, Autores, DOI, Año, Abstract, Keywords
metadatos = tars.extraer_metadatos_paper("paper.pdf")

print(f"📌 Título: {metadatos['titulo']}")
print(f"🔗 DOI: {metadatos['doi']}")
print(f"📅 Año: {metadatos['año']}")
print(f"🏷️  Keywords: {metadatos['keywords']}")
print(f"📄 Abstract: {metadatos['abstract']}")
```

### 3. Resumen Automático
```python
# Genera resumen extractivo inteligente
resumen = tars.generar_resumen_pdf(
    "paper_largo.pdf",
    num_oraciones=5  # Top 5 oraciones más importantes
)

print(resumen['resumen'])
```

### 4. Extracción de Referencias Bibliográficas
```python
# Extrae y estructura todas las referencias
referencias = tars.extraer_referencias_paper("paper.pdf")

print(f"📚 {referencias['total_referencias']} referencias encontradas")

for ref in referencias['referencias'][:5]:
    print(f"[{ref['numero']}] {ref['texto']}")
    if ref['doi']:
        print(f"   DOI: {ref['doi']}")
```

### 5. Comparación de Documentos
```python
# Compara dos versiones de un paper
comparacion = tars.comparar_pdfs(
    "paper_v1.pdf",
    "paper_v2.pdf"
)

print(f"Similitud: {comparacion['similitud_porcentaje']}%")
print(f"Líneas agregadas: {comparacion['lineas_agregadas']}")
print(f"Líneas eliminadas: {comparacion['lineas_eliminadas']}")
```

### 6. Análisis de Calidad de Paper
```python
# Verifica estructura científica
calidad = tars.analizar_calidad_paper("paper.pdf")

print(f"Completitud: {calidad['completitud']}%")
print(f"Secciones encontradas: {calidad['secciones_encontradas']}")
print(f"Referencias: {calidad['numero_referencias']}")
print(f"Figuras: {calidad['numero_figuras']}")

if calidad['recomendaciones']:
    print("Recomendaciones:")
    for rec in calidad['recomendaciones']:
        print(f"  {rec}")
```

---

## 📄 Tipos de Documentos Soportados

### Papers Científicos
```python
# Procesa y extrae: abstract, métodos, resultados, referencias
tars.procesar_pdf("paper.pdf", categoria="paper")

# Detecta automáticamente:
# - Secciones (Introduction, Methods, Results, etc.)
# - Referencias bibliográficas [1], [2], etc.
# - Figuras mencionadas (Figure 1, Fig. 2, etc.)
```

### Manuales Técnicos
```python
# Procesa manuales de equipos, protocolos, etc.
tars.procesar_pdf("manual_motor.pdf", categoria="manual")

# Detecta:
# - Pasos numerados (Step 1, Step 2, etc.)
# - Diagramas y esquemas
# - Tablas de especificaciones
```

### Reportes/Resultados
```python
# Resultados de experimentos, tesis, etc.
tars.procesar_pdf("resultados_experimento.pdf", categoria="reporte")
```

---

## 🔍 Búsqueda en Documentos

### Buscar información específica
```python
# Busca en TODOS los PDFs procesados
resultados = tars.buscar_en_documentos("torque calculation")

for res in resultados:
    print(f"📄 {res['documento']}")
    print(f"   {res['contexto']}")
```

### Filtrar por categoría
```python
# Solo en papers
resultados = tars.buscar_en_documentos("ACL injury", categoria="paper")

# Solo en manuales
resultados = tars.buscar_en_documentos("maintenance", categoria="manual")
```

---

## 🧠 Análisis con Cerebros Expertos

### Análisis completo de PDF
```python
# Procesa PDF + analiza imágenes con cerebros expertos
analisis = tars.analizar_documento_con_expertos(
    "diseno_exoesqueleto.pdf",
    tipo_analisis="completo"  # médico + mecánico + conceptual
)

# Análisis específico
analisis = tars.analizar_documento_con_expertos(
    "radiografia_estudio.pdf",
    tipo_analisis="medico"  # Solo brain médico
)
```

---

## 📊 Ejemplos de Uso Real

### Ejemplo 1: Revisar Paper de Biomecánica
```python
from core_ia import TarsVision

tars = TarsVision()

# 1. Procesar paper
resultado = tars.procesar_pdf("biomechanics_knee.pdf", categoria="paper")

# 2. Ver secciones detectadas
info = tars.docs.extraer_informacion_clave(
    resultado["texto_completo"],
    tipo="paper"
)

print("Secciones:", info["secciones_detectadas"])
print("Figuras:", info["figuras_mencionadas"])

# 3. Buscar información específica
refs_torque = tars.buscar_en_documentos("torque knee flexion")

# 4. Analizar figuras del paper con brain médico
if resultado["imagenes_extraidas"]:
    analisis = tars.brain_medical.analyze(
        resultado["imagenes_extraidas"][0],
        user_context="Imagen de paper sobre biomecánica de rodilla"
    )
```

### Ejemplo 2: Manual de Motor + Cálculos
```python
# Procesar manual del motor
manual = tars.procesar_pdf("manual_maxon_ec45.pdf", categoria="manual")

# Extraer especificaciones (tablas)
if manual["tablas"]:
    print(f"📊 Tablas de especificaciones: {len(manual['tablas'])}")
    for tabla_info in manual["tablas"]:
        print(f"   Página {tabla_info['pagina']}")

# Buscar torque nominal
torque_info = tars.buscar_en_documentos("rated torque", categoria="manual")

# Usar brain mecánico para validar
validacion = tars.brain_mechanical.seleccionar_motor(torque_requerido=45)
```

### Ejemplo 3: Flujo Completo de Investigación
```python
# 1. Procesar múltiples papers
papers = [
    "paper_exo_knee_2024.pdf",
    "paper_rehabilitation_acl.pdf",
    "paper_motor_selection.pdf"
]

for paper in papers:
    tars.procesar_pdf(paper, categoria="paper")

# 2. Buscar información consolidada
resultados = tars.buscar_en_documentos("rehabilitation protocol")

print(f"✅ Encontrado en {len(resultados)} documentos")

# 3. Listar toda la base de conocimiento
resumen = tars.docs.generar_resumen_coleccion()
print(f"📚 {resumen['total_documentos']} documentos")
print(f"📄 {resumen['total_paginas']} páginas totales")
print(f"📝 {resumen['total_palabras']:,} palabras")

# 4. Guardar en proyecto
proyecto = tars.projects.crear_proyecto(
    "Exoesqueleto_Rodilla_v4",
    "Diseño basado en literatura revisada"
)

# Vincular documentos al proyecto
tars.projects.registrar_experimento(proyecto, {
    "titulo": "Revisión de literatura",
    "documentos_revisados": papers,
    "hallazgos": resultados
})
```

---

## 🎯 Ventajas vs Copilot/ChatGPT

| Funcionalidad | TARS | Copilot/ChatGPT |
|--------------|------|-----------------|
| Procesar PDFs largos (>100 páginas) | ✅ Sin límite | ❌ Límite de tokens |
| Búsqueda en múltiples documentos | ✅ Instantánea | ❌ Debe reenviar cada vez |
| Memoria persistente de papers | ✅ Acumulativa | ❌ Olvida entre sesiones |
| Análisis de imágenes de PDFs | ✅ Con cerebros expertos | ⚠️ Limitado |
| 100% privado (papers confidenciales) | ✅ Local | ❌ Envía a internet |
| Extracción de tablas | ✅ Automática | ❌ Manual |

---

## 📁 Estructura de Almacenamiento

```
tars_lifelong/knowledge/
├── documents/                    # PDFs procesados (JSON)
│   ├── paper1_procesado.json
│   ├── paper1.txt              # Texto plano para búsqueda
│   └── manual_motor.txt
├── extracted_images/            # Imágenes extraídas
│   ├── paper1_pagina_1.png
│   ├── paper1_pagina_2.png
│   └── manual_motor_pagina_5.png
└── documents_index.json        # Índice de búsqueda
```

---

## ⚡ Tips para Ingesta Rápida

### 1. Batch Processing
```bash
# Procesar múltiples PDFs
for pdf in papers/*.pdf; do
    python ingesta_rapida.py "$pdf"
done
```

### 2. Búsqueda Eficiente
```python
# Buscar antes de procesar nuevo PDF
resultados = tars.buscar_en_documentos("tu tema")

# Si ya tienes la info, no reproceses
if not resultados:
    tars.procesar_pdf("nuevo_paper.pdf")
```

### 3. Categorización
```python
# Usa categorías para organizar
tars.procesar_pdf("paper.pdf", categoria="biomechanics")
tars.procesar_pdf("spec.pdf", categoria="datasheet")
tars.procesar_pdf("result.pdf", categoria="experimento")

# Busca por categoría
tars.buscar_en_documentos("query", categoria="biomechanics")
```

---

## 🚀 Próximos Pasos

1. **Procesa tu primer PDF:**
   ```bash
   python ingesta_rapida.py tu_paper.pdf
   ```

2. **Busca información:**
   ```python
   python ingesta_rapida.py
   # Opción 4: Buscar
   ```

3. **Integra con tus proyectos:**
   - Vincula PDFs procesados a proyectos específicos
   - Usa búsqueda para encontrar soluciones rápidamente
   - Analiza imágenes técnicas con cerebros expertos
