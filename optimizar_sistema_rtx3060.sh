# 🚀 Optimización del Sistema para RTX 3060 - TARS Dedicado
# Configuraciones preparadas para cuando tengas la Dell dedicada

# Variables de entorno críticas para RTX 3060
export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:2048
export TORCH_USE_CUDA_DSA=1
export CUDA_LAUNCH_BLOCKING=0
export TRANSFORMERS_CACHE=/home/tars/.cache/huggingface
export HF_HOME=/home/tars/.cache/huggingface

# Configuración de NVIDIA para rendimiento máximo
nvidia-settings -a "[gpu:0]/GpuPowerMizerMode=1"           # Modo máximo rendimiento
nvidia-settings -a "[gpu:0]/GPUGraphicsClockOffset[3]=100" # Overclock ligero
nvidia-settings -a "[gpu:0]/GPUMemoryTransferRateOffset[3]=200"

# Instalar PyTorch optimizado para RTX 30-series (CUDA 12.1)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Instalar transformers con optimizaciones
pip install transformers[torch] accelerate bitsandbytes
pip install auto-gptq optimum  # Para quantization avanzada

# Configurar swap para modelos grandes (si es necesario)
sudo fallocate -l 16G /swapfile_tars
sudo chmod 600 /swapfile_tars
sudo mkswap /swapfile_tars
sudo swapon /swapfile_tars
echo '/swapfile_tars none swap sw 0 0' | sudo tee -a /etc/fstab

# Configurar límites de memoria
echo 'vm.max_map_count=262144' | sudo tee -a /etc/sysctl.conf
echo 'vm.overcommit_memory=1' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

echo "✅ Sistema optimizado para RTX 3060. Listo para TARS dedicado."