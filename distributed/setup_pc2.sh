#!/bin/bash

# SETUP PC2 (GTX 1660 Super) - Cliente/Worker
# Este script configura la PC2 como cliente conectado a PC1

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║  🖥️  SETUP PC2 (GTX 1660 Super) - CLIENTE/WORKER              ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"

# Validar argumento PC1
if [ -z "$1" ]; then
    echo -e "${RED}❌ ERROR: Necesitas pasar la IP o hostname de PC1${NC}"
    echo ""
    echo "Uso: bash setup_pc2.sh <IP_DE_PC1>"
    echo ""
    echo "Ejemplos:"
    echo "  bash setup_pc2.sh 192.168.1.100"
    echo "  bash setup_pc2.sh PC1.local"
    echo "  bash setup_pc2.sh 192.168.0.50"
    echo ""
    exit 1
fi

PC1_HOST=$1
PC1_PORT=8000
PC2_PORT=8001
PYTHON_CMD="python3"
REPO_PATH=$(pwd)

echo -e "\n${BLUE}ℹ️  Configuración:${NC}"
echo "  PC1 Host: $PC1_HOST"
echo "  PC1 Port: $PC1_PORT"
echo "  PC2 Port: $PC2_PORT"
echo ""

echo -e "${YELLOW}📋 PASO 1: Verificar Python y CUDA${NC}"
$PYTHON_CMD --version
$PYTHON_CMD -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.version.cuda}'); print(f'GPUs: {torch.cuda.device_count()}')"

echo -e "\n${YELLOW}📋 PASO 2: Instalar dependencias${NC}"
pip install --upgrade pip setuptools wheel
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install fastapi uvicorn aiohttp pydantic python-multipart

# Dependencias para modelos
pip install transformers sentence-transformers

echo -e "\n${YELLOW}📋 PASO 3: Detectar GPUs${NC}"
$PYTHON_CMD distributed/gpu_config.py PC2 localhost $PC2_PORT

echo -e "\n${YELLOW}📋 PASO 4: Crear directorio de configuración${NC}"
mkdir -p config/pc2
cp pc2_config.json config/pc2/

echo -e "\n${YELLOW}📋 PASO 5: Configurar variables de entorno${NC}"
cat > .env.pc2 << EOF
# PC2 Configuration (GTX 1660 Super)
TARS_PC_NAME=PC2
TARS_HOST=0.0.0.0
TARS_PORT=$PC2_PORT
TARS_IS_COORDINATOR=false
TARS_REMOTE_HOST=$PC1_HOST
TARS_REMOTE_PORT=$PC1_PORT

# GPU Configuration
CUDA_VISIBLE_DEVICES=0
TORCH_HOME=/home/user/.cache/torch

# Model Configuration
DEFAULT_MODEL=embedding
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
DEVICE=cuda

# Performance (optimizado para 1660 Super - 6GB)
NUM_WORKERS=2
BATCH_SIZE=4
INFERENCE_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
EOF

echo -e "\n${YELLOW}📋 PASO 6: Crear script de inicio${NC}"
cat > run_pc2.sh << EOF
#!/bin/bash

set -e

# Load environment
source .env.pc2

echo "🚀 Starting PC2 (GTX 1660 Super - Worker)..."
echo "  Host: \$TARS_HOST"
echo "  Port: \$TARS_PORT"
echo "  GPU: \$CUDA_VISIBLE_DEVICES"
echo "  Connected to: \$TARS_REMOTE_HOST:\$TARS_REMOTE_PORT"
echo ""

# Start backend server
python3 -m api.main --host \$TARS_HOST --port \$TARS_PORT --remote-host \$TARS_REMOTE_HOST --remote-port \$TARS_REMOTE_PORT

EOF

chmod +x run_pc2.sh

echo -e "\n${YELLOW}📋 PASO 7: Crear script de conexión a PC1${NC}"
cat > test_pc2_connection.py << 'EOF'
#!/usr/bin/env python3
"""Test PC2 connection to PC1"""

import sys
import asyncio
import os
from distributed.gpu_config import DistributedConfig, GPUDetector, ModelDistribution
from distributed.rpc_communicator import RPCClient

async def test_connection(pc1_host, pc1_port=8000):
    print("\n" + "="*70)
    print("🧪 PC2 CONNECTION TEST")
    print("="*70)
    
    # 1. GPU Detection
    print("\n1️⃣  GPU DETECTION")
    gpus = GPUDetector.detect_gpus()
    if not gpus:
        print("❌ No GPUs detected!")
        return False
    
    print(f"✅ Found {len(gpus)} GPU(s)")
    for gpu in gpus:
        print(f"  - {gpu.name} ({gpu.vram_total_gb:.1f}GB)")
    
    # 2. Configuration
    print("\n2️⃣  LOCAL CONFIGURATION")
    config = DistributedConfig("PC2", "localhost", 8001)
    full_config = config.generate_config(
        coordinator_host=pc1_host,
        coordinator_port=pc1_port
    )
    print(f"✅ Configuration generated")
    print(f"  PC Name: {full_config.pc_name}")
    print(f"  Total VRAM: {full_config.total_vram_gb:.1f}GB")
    print(f"  Remote: {full_config.coordinator_host}:{full_config.coordinator_port}")
    
    # 3. Model Distribution
    print("\n3️⃣  MODEL ASSIGNMENT")
    distribution = ModelDistribution.recommend_distribution(gpus)
    print(f"✅ Models for this PC:")
    for gpu_key, models in distribution.items():
        print(f"  {gpu_key}:")
        for model in models:
            print(f"    - {model}")
    
    # 4. Test RPC Connection
    print(f"\n4️⃣  RPC CONNECTION TEST")
    print(f"  Connecting to PC1: {pc1_host}:{pc1_port}...")
    
    client = RPCClient(pc1_host, pc1_port, timeout=5)
    await client.initialize()
    
    try:
        response = await client.health_check()
        if response.error:
            print(f"❌ PC1 Health Check Failed: {response.error}")
            print(f"\n   Verifica que:")
            print(f"   1. PC1 está corriendo en {pc1_host}:{pc1_port}")
            print(f"   2. El firewall permite conexiones al puerto {pc1_port}")
            print(f"   3. La red está correctamente configurada")
            return False
        else:
            print(f"✅ PC1 is ONLINE and responding!")
            result = response.to_dict()
            print(f"  Response: {result}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    finally:
        await client.close()
    
    print("\n" + "="*70)
    print("✅ PC2 SETUP VERIFIED SUCCESSFULLY")
    print("="*70)
    print("\n✨ PC1 y PC2 están listos para trabajar juntos!")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 test_pc2_connection.py <PC1_HOST>")
        sys.exit(1)
    
    pc1_host = sys.argv[1]
    success = asyncio.run(test_connection(pc1_host))
    sys.exit(0 if success else 1)
EOF

chmod +x test_pc2_connection.py

echo -e "\n${GREEN}✅ PC2 SETUP COMPLETO${NC}"
echo ""
echo "📝 PRÓXIMOS PASOS:"
echo ""
echo "1. En PC2, prueba la conexión a PC1:"
echo "   ${YELLOW}python3 test_pc2_connection.py $PC1_HOST${NC}"
echo ""
echo "2. Una vez conectado, inicia PC2:"
echo "   ${YELLOW}./run_pc2.sh${NC}"
echo ""
echo "3. Esto iniciará el worker en:"
echo "   ${YELLOW}http://localhost:$PC2_PORT${NC}"
echo ""
echo "4. PC2 se comunicará con PC1 en:"
echo "   ${YELLOW}http://$PC1_HOST:$PC1_PORT${NC}"
echo ""

echo -e "\n${YELLOW}📊 INFORMACIÓN IMPORTANTE:${NC}"
echo "  - PC2 es un WORKER (cliente secundario)"
echo "  - Se conecta a PC1 por RPC/HTTP"
echo "  - GPU de PC2 (1660 Super): embeddings y procesamiento"
echo "  - Los modelos grandes se ejecutan en PC1"
echo "  - La comunicación es asincrónica y no requiere servidor central"
echo ""

echo -e "${BLUE}💡 TROUBLESHOOTING:${NC}"
echo ""
echo "Si la conexión falla:"
echo "  1. Verifica IP de PC1: ${YELLOW}ifconfig | grep inet${NC}"
echo "  2. Prueba conectividad: ${YELLOW}ping $PC1_HOST${NC}"
echo "  3. Verifica puerto abierto: ${YELLOW}nc -zv $PC1_HOST $PC1_PORT${NC}"
echo ""
