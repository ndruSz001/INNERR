#!/bin/bash

# SETUP PC1 (RTX 3060) - Coordinador Principal
# Este script configura la PC1 como servidor principal

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║  🖥️  SETUP PC1 (RTX 3060) - COORDINADOR PRINCIPAL             ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuración
PC1_HOST="0.0.0.0"
PC1_PORT=8000
PYTHON_CMD="python3"
REPO_PATH=$(pwd)

echo -e "\n${YELLOW}📋 PASO 1: Verificar Python y CUDA${NC}"
$PYTHON_CMD --version
$PYTHON_CMD -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.version.cuda}'); print(f'GPUs: {torch.cuda.device_count()}')"

echo -e "\n${YELLOW}📋 PASO 2: Instalar dependencias${NC}"
pip install --upgrade pip setuptools wheel
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install fastapi uvicorn aiohttp pydantic python-multipart

# Dependencias para modelos
pip install transformers sentence-transformers ollama openai

echo -e "\n${YELLOW}📋 PASO 3: Detectar GPUs${NC}"
$PYTHON_CMD distributed/gpu_config.py PC1 localhost $PC1_PORT

echo -e "\n${YELLOW}📋 PASO 4: Crear directorio de configuración${NC}"
mkdir -p config/pc1
cp pc1_config.json config/pc1/

echo -e "\n${YELLOW}📋 PASO 5: Configurar variables de entorno${NC}"
cat > .env.pc1 << 'EOF'
# PC1 Configuration (RTX 3060)
TARS_PC_NAME=PC1
TARS_HOST=0.0.0.0
TARS_PORT=8000
TARS_IS_COORDINATOR=true
TARS_REMOTE_HOST=None
TARS_REMOTE_PORT=None

# GPU Configuration
CUDA_VISIBLE_DEVICES=0
TORCH_HOME=/home/user/.cache/torch

# Model Configuration
DEFAULT_MODEL=mistral-7b
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
DEVICE=cuda

# Performance
NUM_WORKERS=4
BATCH_SIZE=8
INFERENCE_TIMEOUT=60

# Logging
LOG_LEVEL=INFO
EOF

echo -e "\n${YELLOW}📋 PASO 6: Crear script de inicio${NC}"
cat > run_pc1.sh << 'EOF'
#!/bin/bash

set -e

# Load environment
source .env.pc1

echo "🚀 Starting PC1 (RTX 3060 - Coordinator)..."
echo "  Host: $TARS_HOST"
echo "  Port: $TARS_PORT"
echo "  GPU: $CUDA_VISIBLE_DEVICES"
echo ""

# Start backend server
python3 -m api.main --host $TARS_HOST --port $TARS_PORT

EOF

chmod +x run_pc1.sh

echo -e "\n${YELLOW}📋 PASO 7: Crear script de prueba rápida${NC}"
cat > test_pc1_setup.py << 'EOF'
#!/usr/bin/env python3
"""Quick test of PC1 setup"""

import sys
import torch
from distributed.gpu_config import DistributedConfig, GPUDetector, ModelDistribution

def main():
    print("\n" + "="*70)
    print("🧪 PC1 SETUP TEST")
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
    print("\n2️⃣  CONFIGURATION")
    config = DistributedConfig("PC1", "localhost", 8000)
    full_config = config.generate_config()
    print(f"✅ Configuration generated")
    print(f"  PC Name: {full_config.pc_name}")
    print(f"  Total VRAM: {full_config.total_vram_gb:.1f}GB")
    print(f"  Is Coordinator: {full_config.is_coordinator}")
    
    # 3. Model Distribution
    print("\n3️⃣  MODEL DISTRIBUTION")
    distribution = ModelDistribution.recommend_distribution(gpus)
    print(f"✅ Recommended distribution:")
    for gpu_key, models in distribution.items():
        print(f"  {gpu_key}:")
        for model in models:
            print(f"    - {model}")
    
    # 4. CUDA Check
    print("\n4️⃣  CUDA CHECK")
    print(f"✅ CUDA Available: {torch.cuda.is_available()}")
    print(f"✅ CUDA Device Count: {torch.cuda.device_count()}")
    print(f"✅ PyTorch Version: {torch.__version__}")
    
    # 5. Quick Memory Test
    print("\n5️⃣  MEMORY TEST")
    try:
        x = torch.randn(1000, 1000).cuda()
        del x
        torch.cuda.empty_cache()
        print("✅ GPU memory allocation test passed")
    except Exception as e:
        print(f"❌ GPU memory test failed: {e}")
        return False
    
    print("\n" + "="*70)
    print("✅ PC1 SETUP VERIFIED SUCCESSFULLY")
    print("="*70)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
EOF

chmod +x test_pc1_setup.py

echo -e "\n${GREEN}✅ PC1 SETUP COMPLETO${NC}"
echo ""
echo "📝 PRÓXIMOS PASOS:"
echo ""
echo "1. En PC1, prueba la configuración:"
echo "   ${YELLOW}python3 test_pc1_setup.py${NC}"
echo ""
echo "2. Una vez verificado, inicia PC1:"
echo "   ${YELLOW}./run_pc1.sh${NC}"
echo ""
echo "3. Esto iniciará el servidor en:"
echo "   ${YELLOW}http://localhost:8000${NC}"
echo ""
echo "4. Luego configura PC2 (GTX 1660 Super) con:"
echo "   ${YELLOW}bash setup_pc2.sh <IP_DE_PC1>${NC}"
echo ""

echo -e "\n${YELLOW}📊 INFORMACIÓN IMPORTANTE:${NC}"
echo "  - PC1 es el COORDINADOR (servidor principal)"
echo "  - PC2 se conectará a PC1 por RPC"
echo "  - GPU de PC1 (RTX 3060): modelos grandes (7-13B)"
echo "  - GPU de PC2 (1660 Super): embeddings y modelos pequeños"
echo ""
