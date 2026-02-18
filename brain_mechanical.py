
"""
brain_mechanical.py
Agente ingeniero especializado en cinemática, torque, materiales y análisis CAD.
Incluye cálculos de ingeniería para validación de diseños mecánicos.

Ejemplo de uso:
    from brain_mechanical import BrainMechanical
    brain = BrainMechanical()
    resultado = brain.analyze("pieza.png", user_context="robot", tipo_analisis="estructural")
    print(resultado)
"""

import math
from pathlib import Path
import json


class BrainMechanical:
    """Análisis mecánico y cálculos de ingeniería para prototipos."""
    
    def __init__(self, vision_model=None):
        self.expertise = "ingeniería mecánica, cinemática y análisis estructural"
        self.vision_model = vision_model
        
        # Base de datos de materiales comunes
        self.materiales = {
            "aluminio_6061": {"densidad": 2.7, "resistencia_traccion": 310, "modulo_young": 68.9},
            "acero_inox_316": {"densidad": 8.0, "resistencia_traccion": 515, "modulo_young": 193},
            "abs_impresion3d": {"densidad": 1.04, "resistencia_traccion": 40, "modulo_young": 2.3},
            "pla_impresion3d": {"densidad": 1.25, "resistencia_traccion": 50, "modulo_young": 3.5},
            "fibra_carbono": {"densidad": 1.6, "resistencia_traccion": 600, "modulo_young": 70}
        }
    
    def analyze(self, image_path, user_context="", tipo_analisis="general"):

        # Modularized: import BrainMechanical from mechanical.brain
        from mechanical.brain import BrainMechanical
            "area_mm2": area_mm2,
            "esfuerzo_MPa": round(esfuerzo_MPa, 2),
            "resistencia_material_MPa": props["resistencia_traccion"],
            "factor_seguridad": round(factor_seguridad, 2),
            "es_seguro": es_seguro,
            "recomendacion": "✅ Seguro" if es_seguro else "❌ Insuficiente - aumentar área o cambiar material"
        }
        
        print(f"\n🔬 Validación de Material: {material}")
        print(f"   Esfuerzo: {resultado['esfuerzo_MPa']} MPa")
        print(f"   Resistencia: {props['resistencia_traccion']} MPa")
        print(f"   Factor de seguridad: {resultado['factor_seguridad']}x")
        print(f"   {resultado['recomendacion']}")
        
        return resultado