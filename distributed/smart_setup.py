
"""
smart_setup.py
Script de configuración inteligente para TARS Distributed.
Permite detectar hardware, optimizar recursos y lanzar el asistente interactivo.

Ejemplo de uso:
    from distributed.smart_setup import HardwareDetector, OptimizationEngine, SetupWizard
    hardware = HardwareDetector().detect_hardware()
    optimization = OptimizationEngine.generate_profile(hardware)
    wizard = SetupWizard(hardware, optimization)
    wizard.print_header()
    wizard.print_hardware_summary()
"""

from distributed.hardware import HardwareDetector, HardwareProfile, GPUTier
from distributed.optimization import OptimizationEngine, OptimizationProfile
from distributed.wizard import SetupWizard, Colors

if __name__ == "__main__":
    print("TARS Distributed Smart Setup is ready. Add orchestration logic here.")
