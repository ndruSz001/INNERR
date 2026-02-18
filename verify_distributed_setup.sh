
#!/bin/bash
# ------------------------------------------------------------------------------
# verify_distributed_setup.sh
# ------------------------------------------------------------------------------
# Script de verificación rápida para el entorno distribuido de TARS.
# Comprueba Python, PyTorch, CUDA, módulos requeridos, archivos clave,
# documentación, red, almacenamiento y módulos RPC/GPU.
#
# Uso:
#   bash verify_distributed_setup.sh
#
# Salida:
#   Muestra el estado de cada verificación y un resumen final.
#
# Autoría: Proyecto TARS (ver AUTORÍA_Y_LICENCIA.md)
# ------------------------------------------------------------------------------

# Quick Verification Script for Distributed System Setup
# Verifica rápidamente si el sistema está listo

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║  🔍 VERIFICACIÓN RÁPIDA - Sistema Distribuido                ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
PASSED=0
FAILED=0

# Helper functions
check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED++))
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILED++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

check_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# ========================================================================
# 1. Python Verification
# ========================================================================
echo -e "\n${BLUE}1️⃣  PYTHON SETUP${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    check_pass "Python found: $PYTHON_VERSION"
else
    check_fail "Python 3 not found"
    exit 1
fi

# ========================================================================
# 2. PyTorch & CUDA
# ========================================================================
echo -e "\n${BLUE}2️⃣  PYTORCH & CUDA${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

PYTORCH_CHECK=$(python3 -c "import torch; print(f'PyTorch {torch.__version__}')" 2>&1)
if [[ $? -eq 0 ]]; then
    check_pass "$PYTORCH_CHECK"
else
    check_fail "PyTorch import failed"
fi

CUDA_AVAILABLE=$(python3 -c "import torch; print(torch.cuda.is_available())" 2>&1)
if [[ "$CUDA_AVAILABLE" == "True" ]]; then
    check_pass "CUDA is available"
    
    GPU_COUNT=$(python3 -c "import torch; print(torch.cuda.device_count())" 2>&1)
    check_pass "GPU Count: $GPU_COUNT"
    
    # Get GPU names
    python3 -c "
import torch
for i in range(torch.cuda.device_count()):
    name = torch.cuda.get_device_name(i)
    vram = torch.cuda.get_device_properties(i).total_memory / (1024**3)
    print(f'  GPU {i}: {name} ({vram:.1f}GB)')
" | while read line; do
        check_info "$line"
    done
else
    check_fail "CUDA is not available"
fi

# ========================================================================
# 3. Required Packages
# ========================================================================
echo -e "\n${BLUE}3️⃣  REQUIRED PACKAGES${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

PACKAGES=("fastapi" "uvicorn" "aiohttp" "pydantic" "transformers")

for package in "${PACKAGES[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        check_pass "$package installed"
    else
        check_warn "$package not installed (will be installed by setup scripts)"
    fi
done

# ========================================================================
# 4. Distributed Module Files
# ========================================================================
echo -e "\n${BLUE}4️⃣  MODULE FILES${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

REQUIRED_FILES=(
    "distributed/__init__.py"
    "distributed/gpu_config.py"
    "distributed/rpc_communicator.py"
    "distributed/api_distributed.py"
    "distributed/gpu_optimization.py"
    "distributed/setup_pc1.sh"
    "distributed/setup_pc2.sh"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        check_pass "$file exists"
    else
        check_fail "$file NOT FOUND"
    fi
done

# ========================================================================
# 5. Documentation Files
# ========================================================================
echo -e "\n${BLUE}5️⃣  DOCUMENTATION${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

DOC_FILES=(
    "QUICK_START_DISTRIBUTED.md"
    "DISTRIBUTED_SETUP_SUMMARY.md"
    "examples_distributed.py"
)

for file in "${DOC_FILES[@]}"; do
    if [ -f "$file" ]; then
        check_pass "$file exists"
    else
        check_fail "$file NOT FOUND"
    fi
done

# ========================================================================
# 6. GPU Detection Test
# ========================================================================
echo -e "\n${BLUE}6️⃣  GPU DETECTION TEST${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if python3 -c "from distributed.gpu_config import GPUDetector; GPUDetector.detect_gpus()" 2>&1 | grep -q "Detected"; then
    check_pass "GPU detection module working"
else
    check_fail "GPU detection failed"
fi

# ========================================================================
# 7. RPC Module Test
# ========================================================================
echo -e "\n${BLUE}7️⃣  RPC COMMUNICATION TEST${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if python3 -c "from distributed.rpc_communicator import RPCClient, RPCServer; print('RPC modules loaded')" 2>&1 | grep -q "loaded"; then
    check_pass "RPC communication modules loaded"
else
    check_fail "RPC modules failed to load"
fi

# ========================================================================
# 8. Network Check
# ========================================================================
echo -e "\n${BLUE}8️⃣  NETWORK CHECK${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')
if [ -n "$LOCAL_IP" ]; then
    check_pass "Local IP: $LOCAL_IP"
else
    check_warn "Could not determine local IP"
fi

# Check if can create sockets
if python3 -c "import socket; s = socket.socket(); s.bind(('0.0.0.0', 0)); s.close()" 2>&1; then
    check_pass "Socket creation working"
else
    check_fail "Socket creation failed"
fi

# ========================================================================
# 9. Storage Space
# ========================================================================
echo -e "\n${BLUE}9️⃣  STORAGE CHECK${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

AVAILABLE_GB=$(df . | tail -1 | awk '{print $4}' | xargs echo "scale=2; " | bc)
if (( $(echo "$AVAILABLE_GB > 10000000" | bc -l) )); then
    check_pass "Sufficient storage available (~10GB+)"
else
    check_warn "Low storage available (models need ~30-50GB)"
fi

# ========================================================================
# SUMMARY
# ========================================================================
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                        RESUMEN                                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"

echo -e "\n${GREEN}✅ PASSOU: $PASSED${NC}"
echo -e "${RED}❌ FALHOU: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✨ SISTEMA PRONTO PARA CONFIGURAÇÃO!${NC}"
    echo ""
    echo "Próximos passos:"
    echo "  1. Em PC1: bash distributed/setup_pc1.sh"
    echo "  2. Em PC2: bash distributed/setup_pc2.sh <IP_DE_PC1>"
    echo ""
    echo "Leia para mais detalhes:"
    echo "  → QUICK_START_DISTRIBUTED.md"
    echo "  → DISTRIBUTED_SETUP_SUMMARY.md"
    exit 0
else
    echo -e "\n${RED}⚠️  ERROS DETECTADOS - Leia a saída acima${NC}"
    exit 1
fi
