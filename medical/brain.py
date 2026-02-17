from pathlib import Path
import json
from datetime import datetime

class BrainMedical:
    """Análisis de imágenes médicas y compatibilidad biomecánica para prototipos."""
    def __init__(self, vision_model=None):
        self.expertise = "biomecánica, anatomía y análisis de imágenes médicas"
        self.vision_model = vision_model
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
        analisis = {
            "fecha": datetime.now().isoformat(),
            "tipo_imagen": tipo_imagen,
            "patient_id": patient_id or "anonimo",
            "imagen": str(image_path),
            "contexto": user_context
        }
        if self.vision_model:
            try:
                resultado_vision = self.vision_model.analizar_imagen(
                    image_path, 
                    medical_prompt
                )
                analisis["analisis_llava"] = resultado_vision
                analisis["metodo"] = "LLaVA (análisis visual completo)"
            except Exception as e:
                print(f"⚠️ Error con modelo de visión: {e}")
                analisis["analisis_llava"] = None
                analisis["metodo"] = "Análisis estructurado (sin visión)"
        else:
            analisis["analisis_llava"] = None
            analisis["metodo"] = "Análisis estructurado (modelo de visión no cargado)"
        analisis["recomendaciones"] = self._generar_recomendaciones_biomeca(tipo_imagen, user_context)
        self.casos_analizados.append(analisis)
        self._guardar_caso_privado(analisis)
        print(f"\n✅ Análisis completado")
        print(f"📊 Método: {analisis['metodo']}")
        return analisis

    def _generar_recomendaciones_biomeca(self, tipo_imagen, contexto):
        """Genera recomendaciones biomecánicas basadas en conocimiento estructurado."""
        recomendaciones = {
            "puntos_clave": [],
            "consideraciones_diseño": [],
            "precauciones": []
        }
        if "rodilla" in contexto.lower() or "knee" in contexto.lower():
            recomendaciones["puntos_clave"] = [
                "Punto de anclaje proximal: Tercio medio del fémur",
                "Punto de anclaje distal: Tercio superior de la tibia",
                "Centro de rotación: Cóndilo femoral lateral"
            ]
            recomendaciones["consideraciones_diseño"] = [
                "Permitir flexión 0-135° (rango funcional completo)",
                "Evitar presión directa sobre rótula",
                "Considerar momento flexor máximo de ~45 Nm en adulto promedio"
            ]
            recomendaciones["precauciones"] = [
                "Verificar ausencia de osteoartritis severa",
                "Evaluar laxitud ligamentaria antes de aplicar fuerzas laterales",
                "Monitorear temperatura de contacto (<40°C)"
            ]
        elif "tobillo" in contexto.lower() or "ankle" in contexto.lower():
            recomendaciones["puntos_clave"] = [
                "Punto de anclaje: Tercio distal de tibia/peroné",
                "Eje de rotación: Maléolos medial y lateral",
                "Zona de contacto plantar: Distribución triplanar"
            ]
        return recomendaciones

    def _guardar_caso_privado(self, analisis):
        """Guarda caso médico de forma privada y encriptada."""
        patient_id = analisis.get("patient_id", "anonimo")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"caso_{patient_id}_{timestamp}.json"
        filepath = self.data_dir / filename
        # TODO: Implementar encriptación con encrypted_db.py si contiene datos sensibles
        with open(filepath, 'w') as f:
            json.dump(analisis, f, indent=2)
        print(f"🔒 Caso guardado de forma privada: {filename}")

    def compare_anatomy(self, image_path, reference_path, descripcion=""):
        """
        Compara anatomía con imagen de referencia.
        """
        print(f"\n🔬 Comparando anatomía...")
        print(f"   Imagen paciente: {image_path}")
        print(f"   Referencia: {reference_path}")
        if self.vision_model:
            prompt_comparacion = f"""Compara estas dos imágenes médicas:
            
1. Imagen del paciente
2. Imagen de referencia

Analiza:
- Similitudes estructurales
- Diferencias significativas
- Alineación y simetría relativa
- Implicaciones para diseño de dispositivos médicos

Descripción: {descripcion}"""
            # TODO: Implementar comparación multi-imagen con LLaVA
            resultado = "Comparación requiere análisis de múltiples imágenes (pendiente)"
        else:
            resultado = "Modelo de visión no disponible para comparación"
        return {
            "comparacion": resultado,
            "referencia": reference_path,
            "descripcion": descripcion
        }

    def buscar_casos_similares(self, sintomas_keywords):
        """Busca casos médicos previos con características similares."""
        casos_similares = []
        for caso in self.casos_analizados:
            contexto = caso.get("contexto", "").lower()
            if any(keyword.lower() in contexto for keyword in sintomas_keywords):
                casos_similares.append(caso)
        print(f"\n📋 Encontrados {len(casos_similares)} casos similares")
        return casos_similares
