#!/bin/bash
# Script de instalación automática de dependencias para TARS
# Ejecutar con: bash install_deps.sh

set -e

# Instalar requirements principales
if [ -f requirements.txt ]; then
    echo "Instalando dependencias principales..."
    pip install -r requirements.txt
fi

# Instalar requirements de sprint2 si existen
if [ -f requirements_sprint2.txt ]; then
    echo "Instalando dependencias Sprint 2..."
    pip install -r requirements_sprint2.txt
fi

# Instalar dependencias adicionales detectadas
pip install pdfplumber

# Confirmación
pip list | grep -E 'streamlit|torch|transformers|pillow|pandas|faiss|apscheduler|fastapi|uvicorn|pydantic|requests|pdfplumber'

echo "\n✅ Instalación de dependencias completada."
