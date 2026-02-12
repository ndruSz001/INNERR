# 🔊 Sistema de Voz TARS - Documentación

## ✅ Estado: COMPLETAMENTE FUNCIONAL

---

## 🎯 Características

### Síntesis de Voz Implementada
- ✅ Pregunta al inicio si quieres activar voz
- ✅ Respuestas habladas automáticamente
- ✅ Control mediante comando `/voz`
- ✅ Dos métodos disponibles: pyttsx3 (offline) y gTTS (online)

### Métodos Disponibles

#### 1. **pyttsx3** (Predeterminado - OFFLINE) ⚡
- **Ventajas:**
  - No requiere internet
  - Respuesta instantánea
  - Bajo consumo de recursos
- **Desventajas:**
  - Voz más robótica
  - Calidad media

#### 2. **gTTS** (Opcional - ONLINE) 🌐
- **Ventajas:**
  - Voz más natural (Google TTS)
  - Mejor calidad de audio
  - Múltiples idiomas
- **Desventajas:**
  - Requiere internet
  - Pequeño delay (descarga audio)

---

## 📝 Uso

### Al Iniciar TARS
```
╔====================================================================╗
║                            TARS v2.0                               ║
║               IA Personal con Memoria de Largo Plazo              ║
╚====================================================================╝

🔊 ¿Quieres que TARS responda con voz? (s/n): s
✅ Voz activada - TARS hablará sus respuestas
```

### Durante la Conversación
```
> Hola TARS
TARS: [Texto escrito]
[🔊 TARS habla la respuesta]
```

### Controles

#### Activar/Desactivar Voz
```
> /voz
🔊 Voz activada
```

```
> /voz
🔇 Voz desactivada
```

---

## 🔧 Archivos Nuevos

### `tars_voice.py`
```python
Módulo de síntesis de voz
├── TarsVoice class
│   ├── __init__()           - Inicialización automática
│   ├── hablar(texto)        - Sintetiza y reproduce
│   ├── activar()            - Activa voz
│   ├── desactivar()         - Desactiva voz
│   ├── alternar()           - Toggle on/off
│   └── obtener_info()       - Estado del sistema
```

### Modificaciones en `tars_asistente.py`
```python
# Línea 33-38: Import de tars_voice
# Línea 51-54: Inicialización de self.voz
# Línea 68-82: Pregunta inicial de voz
# Línea 254-260: Comando /voz
# Línea 807-809: Síntesis automática de respuestas
```

---

## 🧪 Tests

### Test Manual
```bash
cd /home/ndrz02/keys_1
source .venv/bin/activate
python3 -c "
from tars_voice import TarsVoice
voz = TarsVoice()
print(voz.obtener_info())
voz.hablar('Hola, soy TARS')
"
```

**Resultado esperado:**
```
✅ Voz TARS activada (pyttsx3 - offline)
{'disponible': True, 'metodo': 'pyttsx3', 'activo': True, ...}
[🔊 Audio: "Hola, soy TARS"]
```

---

## ⚙️ Configuración

### Ajustar Velocidad (pyttsx3)
En `tars_voice.py` línea 78:
```python
self.engine.setProperty('rate', 150)  # 100-200 palabras/min
```

### Ajustar Volumen
En `tars_voice.py` línea 79:
```python
self.engine.setProperty('volume', 0.9)  # 0.0 a 1.0
```

### Cambiar a gTTS (mejor calidad)
En `tars_voice.py` línea 24, cambiar:
```python
def __init__(self, metodo: str = "gtts"):  # En vez de "auto"
```

---

## 🐛 Solución de Problemas

### "Sistema de voz no disponible"
**Causa:** Faltan dependencias
**Solución:**
```bash
source .venv/bin/activate
pip install pyttsx3 gtts pygame
```

### No se escucha audio
**Causa:** Audio del sistema silenciado
**Solución:**
1. Verificar volumen del sistema
2. Probar con `speaker-test -t wav`

### Error con pyttsx3 en español
**Causa:** No hay voces en español instaladas
**Solución:**
```bash
# Ubuntu/Debian
sudo apt install espeak espeak-ng

# O usar gTTS que siempre funciona en español
```

### gTTS requiere internet
**Causa:** gTTS descarga audio de Google
**Solución:** Usar pyttsx3 (offline) o asegurar conexión a internet

---

## 📊 Comparativa de Métodos

| Característica | pyttsx3 | gTTS |
|----------------|---------|------|
| Internet | ❌ No | ✅ Sí |
| Velocidad | ⚡ Instantáneo | 🐢 1-2 seg delay |
| Calidad | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Recursos | Bajo | Medio |
| Idiomas | Limitado | Muchos |
| Recomendado | Uso diario | Demos/presentaciones |

---

## 🚀 Comandos Rápidos

### Iniciar TARS con voz
```bash
cd /home/ndrz02/keys_1
source .venv/bin/activate
python3 tars_asistente.py
# Responder 's' cuando pregunte por voz
```

### Probar voz sin TARS completo
```bash
cd /home/ndrz02/keys_1
source .venv/bin/activate
python3 << 'EOF'
from tars_voice import TarsVoice
voz = TarsVoice()
voz.hablar("Este es un test de voz")
EOF
```

---

## 💡 Tips de Uso

1. **Primera vez:** Responde 's' al prompt inicial para probar
2. **Si molesta:** Usa `/voz` para desactivar temporalmente
3. **En público:** Desactiva voz con `/voz` 
4. **Mejores resultados:** gTTS tiene mejor pronunciación en español
5. **Sin internet:** pyttsx3 funciona offline perfectamente

---

## ✅ Verificación Final

### Checklist
- ✅ `tars_voice.py` creado
- ✅ Dependencias instaladas (pyttsx3, gtts, pygame)
- ✅ Integración en `tars_asistente.py`
- ✅ Comando `/voz` funcional
- ✅ Pregunta inicial implementada
- ✅ Test de audio exitoso

### Estado Actual
```
Módulo: tars_voice.py
Método activo: pyttsx3 (offline)
Estado: Funcional ✅
Velocidad: 150 palabras/min
Volumen: 90%
```

---

## 📚 Referencias

- **pyttsx3:** https://github.com/nateshmbhat/pyttsx3
- **gTTS:** https://gtts.readthedocs.io/
- **pygame:** https://www.pygame.org/docs/

---

**🎉 TARS ahora puede hablar!**
