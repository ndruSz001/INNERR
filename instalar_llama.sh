#!/bin/bash
# Script de instalación y configuración de Llama.cpp para TARS
# Optimizado para RTX 3050/3060

set -e

echo "🚀 INSTALACIÓN DE LLAMA.CPP PARA TARS"
echo "====================================="
echo "Este script configurará Llama.cpp como backend optimizado"
echo "para tu RTX 3050/3060 con cuantización Q4_K_M"
echo ""

# Verificar sistema
echo "🔍 Verificando sistema..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "✅ Linux detectado"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "✅ macOS detectado"
else
    echo "❌ Sistema operativo no soportado"
    exit 1
fi

# Verificar GPU
echo "🔍 Verificando GPU..."
if command -v nvidia-smi &> /dev/null; then
    GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits)
    echo "✅ NVIDIA GPU detectada: $GPU_INFO"
else
    echo "⚠️ No se detectó GPU NVIDIA. El rendimiento será limitado."
fi

# Instalar dependencias
echo "📦 Instalando dependencias..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt update
    sudo apt install -y build-essential cmake git
elif [[ "$OSTYPE" == "darwin"* ]]; then
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew no encontrado. Instálalo desde https://brew.sh/"
        exit 1
    fi
    brew install cmake git
fi

# Clonar y compilar llama.cpp
echo "🔧 Clonando y compilando Llama.cpp..."
if [ ! -d "llama.cpp" ]; then
    git clone https://github.com/ggerganov/llama.cpp
fi

cd llama.cpp

# Compilar con optimizaciones para RTX 30xx
echo "⚡ Compilando con optimizaciones CUDA..."
if command -v nvcc &> /dev/null; then
    # Con CUDA
    make LLAMA_CUDA=1 LLAMA_CUDA_FORCE_MMQ=1 LLAMA_CUDA_FORCE_CUBLAS=1
else
    # Sin CUDA (CPU only)
    make
fi

echo "✅ Llama.cpp compilado exitosamente"

# Crear directorio para modelos
cd ..
mkdir -p modelos

echo ""
echo "📋 PRÓXIMOS PASOS:"
echo "=================="
echo ""
echo "1. Descarga el modelo Phi-2:"
echo "   huggingface-cli download microsoft/phi-2 --local-dir modelos/phi-2"
echo ""
echo "2. Convierte el modelo a GGUF:"
echo "   cd llama.cpp"
echo "   python convert-hf-to-gguf.py ../modelos/phi-2/"
echo ""
echo "3. Cuantiza a Q4_K_M (óptimo para RTX 30xx):"
echo "   ./quantize ../modelos/phi-2.gguf ../modelos/phi-2-q4_k_m.gguf Q4_K_M"
echo ""
echo "4. Prueba el rendimiento:"
echo "   ./main -m ../modelos/phi-2-q4_k_m.gguf --prompt \"Hola TARS\" -n 50 --gpu-layers 35"
echo ""
echo "5. Integra con TARS:"
echo "   python optimizacion_llama.py test"
echo ""

echo "🎯 CONFIGURACIÓN RECOMENDADA PARA RTX 3050/3060:"
echo "- gpu-layers: 35 (aprox. 4GB VRAM)"
echo "- threads: 8-12 (núcleos de CPU)"
echo "- ctx-size: 2048 (contexto de conversación)"
echo "- temp: 0.7-0.8 (creatividad balanceada)"
echo ""

echo "📊 RENDIMIENTO ESPERADO:"
echo "- Primera respuesta: ~2-3 segundos"
echo "- Respuestas siguientes: ~0.5-1 segundo"
echo "- Uso de CPU: 40-50%"
echo "- Temperatura CPU: 60-65°C"
echo ""

echo "✅ Instalación completada. ¡TARS ahora volará! 🚀"