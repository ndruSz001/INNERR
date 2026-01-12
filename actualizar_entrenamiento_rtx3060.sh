#!/bin/bash
# 🚀 Script de Actualización Automática para RTX 3060
# Ejecutar diariamente para integrar nuevos entrenamientos del cluster

echo "🔄 TARS RTX 3060 - Actualización Automática de Entrenamiento"
echo "Fecha: $(date)"
echo "=================================================="

# Verificar que estamos en RTX 3060
if ! nvidia-smi | grep -q "RTX 3060"; then
    echo "❌ Error: Este script requiere RTX 3060"
    exit 1
fi

# Verificar memoria disponible
VRAM_TOTAL=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits)
if [ "$VRAM_TOTAL" -lt 12000 ]; then
    echo "❌ Error: Se requieren al menos 12GB VRAM"
    exit 1
fi

echo "✅ RTX 3060 detectado con ${VRAM_TOTAL}MB VRAM"

# Crear directorios necesarios
mkdir -p cluster_updates/procesados
mkdir -p modelos_actualizados
mkdir -p logs_actualizaciones

# Función de logging
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a logs_actualizaciones/actualizacion_$(date +%Y%m%d).log
}

log_message "Iniciando proceso de actualización automática"

# Verificar conexión al cluster (ajusta según tu configuración)
if ping -c 1 cluster.tars.local &> /dev/null; then
    log_message "✅ Conexión al cluster establecida"

    # Descargar actualizaciones del cluster
    log_message "📥 Descargando actualizaciones del cluster..."
    rsync -avz --remove-source-files cluster.tars.local:/data/tars_updates/ ./cluster_updates/ 2>/dev/null || {
        log_message "⚠️ No se pudieron descargar actualizaciones del cluster"
    }
else
    log_message "⚠️ No se pudo conectar al cluster - usando actualizaciones locales"
fi

# Verificar si hay actualizaciones pendientes
if [ -z "$(find cluster_updates -name "*.json" -type f)" ]; then
    log_message "📋 No hay actualizaciones pendientes"
    exit 0
fi

log_message "🎯 Actualizaciones encontradas: $(find cluster_updates -name "*.json" -type f | wc -l)"

# Activar entorno virtual
if [ -d "venv_rtx3060" ]; then
    source venv_rtx3060/bin/activate
    log_message "✅ Entorno virtual activado"
else
    log_message "❌ Error: Entorno virtual no encontrado"
    exit 1
fi

# Ejecutar actualización del modelo
log_message "🚀 Iniciando actualización del modelo..."

python3 -c "
from core_ia_rtx3060 import TarsVisionRTX3060
import sys

try:
    # Inicializar TARS RTX 3060
    tars = TarsVisionRTX3060()
    log_message('✅ TARS RTX 3060 inicializado')

    # Cargar checkpoint personalizado si existe
    if tars.cargar_checkpoint_personalizado():
        log_message('✅ Checkpoint personalizado cargado')
    else:
        log_message('ℹ️ Usando modelo base')

    # Aplicar actualizaciones automáticas
    if tars.aplicar_actualizacion_automatica():
        log_message('✅ Actualización automática completada exitosamente')
        sys.exit(0)
    else:
        log_message('⚠️ No se aplicaron actualizaciones')
        sys.exit(0)

except Exception as e:
    log_message(f'❌ Error durante actualización: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    log_message "🎉 Proceso de actualización completado exitosamente"

    # Backup automático
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    cp -r modelos_actualizados modelos_backup_$TIMESTAMP
    log_message "💾 Backup creado: modelos_backup_$TIMESTAMP"

    # Limpiar archivos procesados antiguos (mantener últimos 7 días)
    find cluster_updates/procesados -name "*.json" -mtime +7 -delete 2>/dev/null || true

else
    log_message "❌ Error en el proceso de actualización"
    exit 1
fi

log_message "=================================================="
log_message "Actualización automática finalizada"
echo ""
echo "📊 Resumen:"
echo "   - Logs: logs_actualizaciones/actualizacion_$(date +%Y%m%d).log"
echo "   - Modelos actualizados: modelos_actualizados/"
echo "   - Backups: modelos_backup_*"
echo ""
echo "✅ ¡TARS está más inteligente que nunca!"