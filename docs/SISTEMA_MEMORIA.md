# Sistema de Memoria de Conversaciones - TARS

## 📋 Organización de la Memoria

### Estructura de Base de Datos

```
tars_lifelong/conversations.db
├── conversaciones          # Metadatos de conversaciones
├── mensajes               # Todos los mensajes intercambiados
├── contexto_conversacion  # Contexto específico por conversación
└── resumenes             # Resúmenes automáticos generados
```

---

## 🔄 Flujo de Gestión de Conversaciones

### Al Inicio: Filtros y Decisiones

Cuando inicias TARS, el sistema te pregunta:

```
┌─────────────────────────────────────┐
│  ¿Cómo deseas empezar?              │
├─────────────────────────────────────┤
│  1. Nueva conversación ocasional    │
│  2. Continuar conversación anterior │
│  3. Buscar en conversaciones        │
└─────────────────────────────────────┘
```

#### Opción 1: Nueva Conversación Ocasional

**Filtros aplicados AL INICIO:**

1. **Tipo de conversación** (categoría)
   - Investigación (papers, análisis científico)
   - Desarrollo (diseño, prototipado)
   - Médica (biomecánica, análisis clínico)
   - Casual (general)
   - Análisis (datos, experimentos)

2. **Proyecto relacionado** (opcional)
   - Vincula la conversación a un proyecto específico
   - Ejemplo: "Exoesqueleto_Rodilla_v3"

3. **Importancia** (1-10)
   - 1-3: Baja (exploratoria, pruebas)
   - 4-7: Media (trabajo regular)
   - 8-10: Alta (crítica, decisiones importantes)

4. **Tags/Etiquetas**
   - Palabras clave para buscar después
   - Ejemplo: ["motor", "torque", "pruebas"]

**¿Qué se guarda AL INICIO?**

```python
# Se crea registro en BD inmediatamente
{
    "id": "a3f9b2c1",  # ID único
    "titulo": "Sin título (se genera con primer mensaje)",
    "categoria": "desarrollo",
    "proyecto_relacionado": "Exoesqueleto_v3",
    "importancia": 7,
    "tags": ["motor", "torque"],
    "fecha_inicio": "2026-01-23T14:30:00",
    "estado": "activa"
}
```

#### Opción 2: Continuar Conversación Anterior

**Proceso:**

1. **Lista las 10 conversaciones más recientes**
   ```
   1. Análisis de torque motor Maxon
      📁 desarrollo | 💬 23 mensajes | 🕐 Hace 2 días
      🔗 Proyecto: Exoesqueleto_v3
   
   2. Revisión paper biomecánica rodilla
      📁 investigacion | 💬 15 mensajes | 🕐 Ayer
   ```

2. **Al elegir una conversación, carga:**
   - ✅ Últimos 10 mensajes (contexto inmediato)
   - ✅ Contexto guardado (variables, temas, decisiones)
   - ✅ Metadatos (proyecto, importancia, tags)

3. **Muestra resumen:**
   ```
   📂 Conversación recuperada: Análisis de torque motor Maxon
      Mensajes previos: 23
      Última actividad: 2026-01-21
   
   📜 Últimos mensajes:
      👤 ¿El motor Maxon EC45 tiene suficiente torque?
      🤖 Con reductor 1:50 alcanza 48 Nm, suficiente...
      👤 Perfecto, entonces lo apruebo para v3
   ```

#### Opción 3: Buscar Conversaciones

**Búsqueda inteligente:**
- Busca en **títulos**, **descripciones** y **contenido de mensajes**
- Muestra coincidencias ordenadas por relevancia

```bash
🔎 Buscar: "motor sobrecalentamiento"

✅ 3 resultado(s):

1. Problema motor MG996R temperatura
   📁 desarrollo | 💬 18 mensajes
   📝 Servo se sobrecalienta después de 5 min...

2. Solución: Cambio a Dynamixel
   📁 desarrollo | 💬 12 mensajes
```

---

## 💾 Guardado de Conversaciones

### Durante la Conversación

**Guardado AUTOMÁTICO después de cada mensaje:**

```python
# Usuario escribe
mensaje_user = "¿Cómo calculo el torque necesario?"

# Se guarda INMEDIATAMENTE
manager.agregar_mensaje(
    conversacion_id="a3f9b2c1",
    tipo="user",
    contenido=mensaje_user,
    metadata={"timestamp": "2026-01-23T14:35:12"}
)

# TARS responde
respuesta = tars.generar_respuesta(mensaje_user)

# Se guarda INMEDIATAMENTE
manager.agregar_mensaje(
    conversacion_id="a3f9b2c1",
    tipo="tars",
    contenido=respuesta,
    metadata={"modelo": "llama", "tokens": 150}
)
```

**Auto-actualización:**
- ✅ Contador de mensajes incrementa
- ✅ Fecha de última actividad se actualiza
- ✅ Título se genera automáticamente con primer mensaje del usuario

### Al Final de la Conversación

**Guardado FINAL automático:**

```python
# Usuario cierra conversación (/salir o cierra terminal)

# 1. Guardar contexto final
manager.guardar_contexto(
    conversacion_id,
    "ultimo_tema",
    "cálculos de torque"
)

# 2. Generar resumen automático (si >5 mensajes)
if num_mensajes > 5:
    resumen = manager.generar_resumen_conversacion(conversacion_id)
    # Guarda: resumen_corto, palabras_clave, temas

# 3. Marcar como última posición conocida
manager.guardar_contexto(
    conversacion_id,
    "punto_pausa",
    "decisión final: aprobar motor Maxon"
)
```

---

## 🎯 Modos de Uso

### Modo Ocasional (Nueva cada vez)

**Cuándo usar:**
- ✅ Pregunta rápida sin contexto
- ✅ Exploración de nuevo tema
- ✅ No necesitas recordar la conversación

**Comportamiento:**
```python
# Cada inicio = nueva conversación
Conv 1: "Cómo funciona OCR"        [cerrada]
Conv 2: "Análisis de PDF médico"   [cerrada]
Conv 3: "Buscar en documentos"     [cerrada]
```

### Modo Continuo (Retomar siempre la misma)

**Cuándo usar:**
- ✅ Trabajo en proyecto específico por días/semanas
- ✅ Necesitas mantener contexto acumulativo
- ✅ Decisiones que se construyen sobre anteriores

**Comportamiento:**
```python
# Día 1
Conv "Diseño Exoesqueleto v3": [23 mensajes]

# Día 2 - Continuar
Conv "Diseño Exoesqueleto v3": [23 + 15 = 38 mensajes]
# TARS recuerda: decisión de motor Maxon, cálculos previos, etc.

# Día 5 - Continuar
Conv "Diseño Exoesqueleto v3": [38 + 8 = 46 mensajes]
```

---

## 🔍 Ejemplo de Flujo Completo

### Escenario: Desarrollo de Exoesqueleto (1 semana)

**Día 1 - Lunes:**
```bash
$ python tars_chat_con_memoria.py

¿Cómo deseas empezar?
> 1. Nueva conversación

Tipo de conversación:
> 2. Desarrollo

Proyecto relacionado:
> Exoesqueleto_Rodilla_v3

Importancia (1-10):
> 8

Tags:
> motor, torque, diseño

✅ Conversación creada: [a3f9b2c1]

👤 Necesito calcular el torque para flexión de rodilla
🤖 Para calcular torque: τ = F × d × sin(θ)...

[15 mensajes más...]

/salir
💾 Conversación guardada: 16 mensajes
```

**Día 3 - Miércoles:**
```bash
$ python tars_chat_con_memoria.py

¿Cómo deseas empezar?
> 2. Continuar conversación

Conversaciones recientes:

1. Necesito calcular el torque para flexión...
   📁 desarrollo | 💬 16 mensajes | 🕐 Hace 2 días
   🔗 Proyecto: Exoesqueleto_Rodilla_v3

Elegir: 1

📂 Conversación recuperada
   Mensajes previos: 16
   
📜 Últimos mensajes:
   👤 Necesito calcular el torque...
   🤖 Para calcular torque: τ = F × d...
   👤 Perfecto, entonces uso motor Maxon

👤 Ahora necesito validar el material del soporte
🤖 [TARS recuerda decisión del motor y continúa...]

[12 mensajes nuevos...]

/salir
💾 Conversación guardada: 28 mensajes total
```

**Día 7 - Domingo (revisión):**
```bash
$ python tars_chat_con_memoria.py

¿Cómo deseas empezar?
> 3. Buscar conversaciones

🔎 Buscar: exoesqueleto motor

✅ 1 resultado:

1. Necesito calcular el torque para flexión...
   📁 desarrollo | 💬 28 mensajes
   🔗 Proyecto: Exoesqueleto_Rodilla_v3

Elegir: 1

👤 /resumen

📝 Resumen:
   Diseño y validación de motor Maxon EC45 con reductor
   para exoesqueleto de rodilla. Material aluminio 6061.

🏷️  Palabras clave: motor, torque, aluminio, validación, maxon
```

---

## ⚙️ Configuración Avanzada

### Archivado Automático

```python
# Archivar conversaciones sin actividad >30 días
manager.archivar_conversaciones_inactivas(dias=30)
```

### Exportar Conversaciones

```python
# Exportar conversación específica a JSON
manager.exportar_conversacion("a3f9b2c1", "backup.json")
```

### Generación de Resúmenes

```python
# Generar resúmenes de todas las conversaciones activas
for conv in manager.listar_conversaciones(estado="activa"):
    manager.generar_resumen_conversacion(conv['id'])
```

---

## 🎯 Diferenciador vs Copilot/ChatGPT

| Funcionalidad | TARS | Copilot/ChatGPT |
|--------------|------|-----------------|
| **Memoria entre sesiones** | ✅ Ilimitada | ❌ Olvida todo |
| **Múltiples conversaciones** | ✅ Gestión completa | ❌ Una a la vez |
| **Búsqueda en historial** | ✅ Texto completo | ❌ No disponible |
| **Contexto acumulativo** | ✅ Días/semanas | ❌ Solo sesión actual |
| **Vinculación a proyectos** | ✅ Automática | ❌ Manual |
| **Resúmenes automáticos** | ✅ Generados | ⚠️ Solo bajo demanda |
| **Privacidad total** | ✅ 100% local | ❌ Servidor remoto |

---

## 🚀 Uso Rápido

```bash
# Interfaz completa con memoria
python tars_chat_con_memoria.py

# O integrar en chat existente
python tars_terminal_chat.py  # (actualizado con memoria)
```

**Comandos durante chat:**
- `/salir` - Guardar y salir
- `/archivar` - Archivar conversación
- `/contexto` - Ver contexto guardado
- `/resumen` - Generar resumen
