# SETUP_1660_SUPER.md

## Guía de configuración para PC con GPU NVIDIA GTX 1660 Super

### 1. Instalar drivers NVIDIA
- Descarga los drivers más recientes desde https://www.nvidia.com/Download/index.aspx
- Instala usando el método recomendado para tu distribución Linux (por ejemplo, `sudo apt install nvidia-driver-XXX`)

### 2. Instalar CUDA Toolkit
- Recomendado: CUDA 11.x o superior
- Descarga desde https://developer.nvidia.com/cuda-downloads
- Sigue las instrucciones para tu sistema operativo
- Verifica instalación con:
  ```bash
  nvcc --version
  nvidia-smi
  ```

### 3. Instalar PyTorch con soporte CUDA
- Ve a https://pytorch.org/get-started/locally/
- Elige CUDA 11.x y ejecuta:
  ```bash
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu11x
  ```

### 4. Instalar faiss-gpu
- Ejecuta:
  ```bash
  pip install faiss-gpu
  ```

### 5. Recomendaciones generales
- Instala dependencias del proyecto:
  ```bash
  pip install -r requirements.txt
  pip install -r requirements_sprint2.txt
  ```
- Si usas otras GPUs, consulta la documentación de PyTorch y CUDA para elegir la versión adecuada.

### 6. Verificación
- Ejecuta un test simple en Python:
  ```python
  import torch
  print(torch.cuda.is_available())
  print(torch.cuda.get_device_name(0))
  ```
- Debe mostrar `True` y el nombre de la GPU (1660 Super)

### 7. Notas
- Cada PC puede requerir ajustes según su hardware.
- Documenta cualquier cambio especial en este archivo.

---

Este archivo es específico para la GTX 1660 Super. Para otros equipos, crea archivos similares adaptados al hardware.
