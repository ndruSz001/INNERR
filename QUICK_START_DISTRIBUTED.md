# 🚀 GUÍA RÁPIDA: Conectar PC1 (3060) + PC2 (1660 Super) HOY

## 📊 Arquitectura

```
                    ┌──────────────────┐
                    │   PC1 (3060)     │
                    │  RTX 3060 - 12GB │
                    │  COORDINADOR     │
                    │  puerto 8000     │
                    └────────┬─────────┘
                             │
                      (RPC/HTTP)
                             │
                    ┌────────▼─────────┐
                    │   PC2 (1660S)    │
                    │  GTX 1660 - 6GB  │
                    │  WORKER          │
                    │  puerto 8001     │
                    └──────────────────┘
```

## ⚡ INICIO RÁPIDO (Hoy)

### PASO 1: PC1 - Detectar Hardware

En la PC con RTX 3060:

```bash
# 1. Navega al repo
cd /path/to/keys_1

# 2. Detecta la GPU
python3 distributed/gpu_config.py PC1 localhost 8000

# Deberías ver:
# ✅ GPU 0: NVIDIA RTX 3060 (12.0GB)
```

### PASO 2: PC1 - Setup Inicial

```bash
# Ejecuta el script de setup
bash distributed/setup_pc1.sh

# Esto:
# ✅ Instala dependencias CUDA
# ✅ Detecta GPU
# ✅ Crea archivo de configuración
# ✅ Genera scripts de inicio
```

### PASO 3: PC1 - Prueba Rápida

```bash
# Verifica que todo funciona
python3 distributed/test_pc1_setup.py

# Deberías ver:
# 1️⃣  GPU DETECTION - ✅ Found 1 GPU(s)
# 2️⃣  CONFIGURATION - ✅ Configuration generated
# 3️⃣  MODEL DISTRIBUTION - ✅ Recommended distribution
# 4️⃣  CUDA CHECK - ✅ CUDA Available: True
# 5️⃣  MEMORY TEST - ✅ GPU memory allocation test passed
```

### PASO 4: PC1 - Inicia el Servidor

```bash
# En PC1, inicia el servidor
./run_pc1.sh

# Verás:
# 🚀 Starting PC1 (RTX 3060 - Coordinator)...
#   Host: 0.0.0.0
#   Port: 8000
#   GPU: 0
#
# [INFO] Application startup complete
```

**✅ PC1 está ONLINE en `http://localhost:8000`**

---

### PASO 5: PC2 - Obtener IP de PC1

En la PC con GTX 1660 Super:

```bash
# En PC1, obtén su IP:
ifconfig | grep "inet "

# Ejemplo:
# inet 192.168.1.100 netmask 0xffffff00
# inet 127.0.0.1 netmask 0xff000000

# Si estás en red local, usa la que empieza con 192.168 o 10.x
# Para este ejemplo: 192.168.1.100
```

### PASO 6: PC2 - Setup con IP de PC1

En la PC con GTX 1660 Super:

```bash
# 1. Navega al repo (que descargaste de GitHub)
cd /path/to/keys_1

# 2. Ejecuta setup con IP de PC1
bash distributed/setup_pc2.sh 192.168.1.100

# Reemplaza 192.168.1.100 con la IP real de PC1
# Esto:
# ✅ Instala dependencias
# ✅ Detecta GPU
# ✅ Configura conexión a PC1
# ✅ Genera scripts de inicio
```

### PASO 7: PC2 - Prueba la Conexión

```bash
# Verifica que PC2 se conecta a PC1
python3 distributed/test_pc2_connection.py 192.168.1.100

# Deberías ver:
# 1️⃣  GPU DETECTION - ✅ Found 1 GPU(s)
# 2️⃣  LOCAL CONFIGURATION - ✅ Configuration generated
# 3️⃣  MODEL ASSIGNMENT - ✅ Models for this PC
# 4️⃣  RPC CONNECTION TEST
#   Connecting to PC1: 192.168.1.100:8000...
# ✅ PC1 is ONLINE and responding!
```

### PASO 8: PC2 - Inicia el Worker

```bash
# En PC2, inicia el worker
./run_pc2.sh

# Verás:
# 🚀 Starting PC2 (GTX 1660 Super - Worker)...
#   Host: 0.0.0.0
#   Port: 8001
#   GPU: 0
#   Connected to: 192.168.1.100:8000
#
# [INFO] Application startup complete
```

**✅ PC2 está ONLINE en `http://localhost:8001`**

---

## 🧪 Pruebas de Comunicación

### Verificar que funciona (desde cualquier PC)

```bash
# 1. Health check PC1
curl http://192.168.1.100:8000/health

# Respuesta esperada:
# {"status":"ok","timestamp":"2024-02-12T...","pc_name":"PC1",...}

# 2. Health check PC2
curl http://192.168.1.100:8001/health

# Respuesta esperada:
# {"status":"ok","timestamp":"2024-02-12T...","pc_name":"PC2",...}

# 3. Ver modelos asignados a PC1
curl http://192.168.1.100:8000/models

# 4. Ver modelos asignados a PC2
curl http://192.168.1.100:8001/models

# 5. Ver configuración completa
curl http://192.168.1.100:8000/config
```

### Test de Inference Distribuido

```python
# test_distributed.py
import asyncio
import aiohttp

async def test():
    async with aiohttp.ClientSession() as session:
        # 1. Query a PC1 (Coordinator)
        async with session.post(
            'http://192.168.1.100:8000/inference',
            json={"prompt": "Hola, ¿cómo estás?"}
        ) as resp:
            print("PC1 Response:", await resp.json())
        
        # 2. Query a PC2 (Worker)
        async with session.post(
            'http://192.168.1.100:8001/embed',
            json={"text": "Texto a embeddings"}
        ) as resp:
            print("PC2 Response:", await resp.json())

asyncio.run(test())
```

---

## 📊 Asignación Automática de Modelos

### RTX 3060 (PC1) - Modelos Grandes

- `llama2-7b` (~7GB)
- `mistral-7b` (~7GB)
- `neural-chat-7b` (~7GB)

**Cuantización:** 4-bit

### GTX 1660 Super (PC2) - Modelos Ligeros

- `embedding-base` (~0.5GB)
- `embedding-large` (~1.5GB)
- `llama2-7b` (8-bit cuantizado)

**Cuantización:** 8-bit

---

## 🔧 Troubleshooting

### "Connection refused" en PC2

```bash
# 1. Verifica que PC1 está corriendo
curl http://192.168.1.100:8000/health

# 2. Verifica conectividad
ping 192.168.1.100

# 3. Verifica puerto abierto
nc -zv 192.168.1.100 8000

# 4. Verifica IP correcta
# En PC1: ifconfig | grep inet
```

### GPU no detectada

```bash
# 1. Verifica CUDA
python3 -c "import torch; print(torch.cuda.is_available())"

# 2. Verifica CUDA toolkit
nvcc --version

# 3. Reinstala PyTorch
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### VRAM insuficiente en PC2

```bash
# Cambiar a cuantización más agresiva en setup_pc2.sh
INFERENCE_TIMEOUT=30
NUM_WORKERS=1  # Reducir workers
BATCH_SIZE=2   # Reducir batch size
```

---

## 📈 Monitorear Rendimiento

### En tiempo real

```bash
# PC1
watch -n 1 'curl -s http://localhost:8000/status | python3 -m json.tool'

# PC2
watch -n 1 'curl -s http://localhost:8001/status | python3 -m json.tool'
```

### Ver GPU usage

```bash
# En ambas PCs
watch -n 1 nvidia-smi

# O con Top GPU
gpustat --watch
```

---

## 🎯 Arquitectura Final

Después de completar todos los pasos:

```
┌─────────────────────────────────────────────────────────────┐
│                  RED LOCAL 192.168.1.x                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  PC1 (Coordinador)          PC2 (Worker)                    │
│  ├─ FastAPI: 8000           ├─ FastAPI: 8001               │
│  ├─ RTX 3060 - 12GB         ├─ GTX 1660S - 6GB             │
│  ├─ Models: 7-13B           ├─ Models: embeddings + small  │
│  └─ RPC Server              └─ RPC Client                  │
│       ↓ RPC/HTTP ↑                                          │
│  ┌──────────────────────────────────────────┐              │
│  │  Distributed Inference & Embeddings      │              │
│  │  - Query PC1 para modelos grandes        │              │
│  │  - Query PC2 para embeddings             │              │
│  │  - Auto-routing automático               │              │
│  └──────────────────────────────────────────┘              │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Checklist Final

- [ ] PC1 GPU detectada (RTX 3060)
- [ ] PC2 GPU detectada (GTX 1660S)
- [ ] PC1 setup completado
- [ ] PC2 setup completado
- [ ] PC1 servidor iniciado (puerto 8000)
- [ ] PC2 servidor iniciado (puerto 8001)
- [ ] Health check PC1 respondiendo
- [ ] Health check PC2 respondiendo
- [ ] PC2 conectado a PC1 (RPC)
- [ ] Test de inference funcionando

---

## 🚀 Próximos Pasos Después de HOY

1. **Integrar modelos reales** (Ollama, LLaMA.cpp, Transformers)
2. **Setup de persistencia** (PostgreSQL compartida)
3. **Load balancing** entre las dos GPUs
4. **Monitoreo y métricas** (Prometheus, Grafana)
5. **Auto-scaling** y recuperación de fallos

---

## 📞 Soporte Rápido

Si hay errores, verifica:

1. **Python 3.8+**: `python3 --version`
2. **PyTorch con CUDA**: `python3 -c "import torch; print(torch.cuda.is_available())"`
3. **IP correcta**: `ping 192.168.1.100` (reemplaza con IP real)
4. **Puerto abierto**: `nc -zv 192.168.1.100 8000`
5. **Logs**: `./run_pc1.sh` y `./run_pc2.sh` muestran los errores en tiempo real

---

**¡Listo! Después de estos pasos tendrás PC1 y PC2 trabajando juntas hoy mismo! 🎉**
