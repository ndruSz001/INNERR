# 🚀 Configuración Optimizada para TARS en RTX 3060
# Script de setup para laptop Dell dedicada
# NO EJECUTAR HASTA TENER RTX 3060 CONFIGURADA

# 1. Instalar CUDA y PyTorch optimizado para RTX 30-series
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install transformers accelerate bitsandbytes scipy

# 2. Dependencias completas de TARS
pip install streamlit gtts pygame speechrecognition pyaudio
pip install pillow sqlalchemy auto-gptq

# 3. Variables de entorno para máximo rendimiento RTX 3060
export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:2048
export TORCH_USE_CUDA_DSA=1
export CUDA_LAUNCH_BLOCKING=0
export TRANSFORMERS_CACHE=/home/tars/.cache/huggingface

# 4. Configuración de NVIDIA para rendimiento máximo
nvidia-settings -a "[gpu:0]/GpuPowerMizerMode=1"  # Prefer maximum performance
nvidia-settings -a "[gpu:0]/GPUGraphicsClockOffset[3]=100"
nvidia-settings -a "[gpu:0]/GPUMemoryTransferRateOffset[3]=200"

# 5. Configurar auto-inicio de TARS
mkdir -p /home/tars/.config/autostart
echo "[Desktop Entry]
Type=Application
Name=TARS AI
Exec=streamlit run /home/tars/TARS/tars_seguro.py --server.port 8501 --server.address 0.0.0.0
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true" > /home/tars/.config/autostart/tars.desktop

echo "✅ Setup RTX 3060 completado. Reinicia para aplicar cambios."