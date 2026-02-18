
"""
brain_medical.py
Agente biomecánico especializado en anatomía, imágenes médicas y compatibilidad biomecánica.
PRIVACIDAD: Todo el análisis es 100% local, ideal para datos médicos sensibles.

Ejemplo de uso:
    from brain_medical import BrainMedical
    brain = BrainMedical()
    brain.analyze("rx.png", user_context="adulto", tipo_imagen="radiografia")
"""

from pathlib import Path
import json
from datetime import datetime


class BrainMedical:
    """Análisis de imágenes médicas y compatibilidad biomecánica para prototipos."""
    
    def __init__(self, vision_model=None):
        self.expertise = "biomecánica, anatomía y análisis de imágenes médicas"
        self.vision_model = vision_model  # LLaVA se pasa desde TarsVision
        self.casos_analizados = []
        self.data_dir = Path("./data/medical")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze(self, image_path, user_context="", patient_id=None, tipo_imagen="radiografia"):
        """
        Analiza imágenes médicas (radiografías, resonancias, etc) de forma privada.
        
        Args:
            image_path: Ruta a la imagen médica
            user_context: Contexto adicional (historial, síntomas, etc)
            patient_id: ID anónimo del paciente (para privacidad)
            tipo_imagen: Tipo de imagen (radiografia, resonancia, ecografia, etc)
        
        Returns:
            Dict con análisis biomecánico
        """
        print(f"\n🏥 Analizando imagen médica ({tipo_imagen})...")
        print(f"📁 Archivo: {image_path}")
        print(f"🔒 PRIVACIDAD: Análisis 100% local, sin conexión a internet")
        
        # Prompt especializado para análisis médico
        medical_prompt = f"""Eres un experto en {self.expertise}. 
        
Analiza esta {tipo_imagen} médica con enfoque en:

1. ESTRUCTURA ANATÓMICA:
   - Identificar estructuras óseas y articulaciones visibles
   - Evaluar alineación y simetría
   - Detectar posibles anomalías estructurales

2. COMPATIBILIDAD BIOMECÁNICA:
   - Puntos de anclaje para dispositivos ortopédicos/exoesqueletos
   - Rangos de movimiento articular
   - Áreas de carga y tensión

3. CONSIDERACIONES PARA PRÓTESIS/EXOESQUELETOS:
   - Zonas de contacto óptimas
   - Limitaciones anatómicas
   - Recomendaciones de diseño

Contexto del paciente: {user_context}

Proporciona un análisis detallado, profesional y útil para diseño de dispositivos médicos."""
        
        from medical.brain import BrainMedical
        analisis = {
            "fecha": datetime.now().isoformat()
        }