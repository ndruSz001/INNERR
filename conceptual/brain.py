
"""
brain.py
Análisis de diseño conceptual, ergonomía y estética para TARS.

Ejemplo de uso:
    from conceptual.brain import BrainConceptual
    brain = BrainConceptual()
    brain.analyze("boceto.png", user_context="adulto", tipo_analisis="ergonomia")
"""

from pathlib import Path
import json

class BrainConceptual:
    """Análisis de diseño conceptual, ergonomía y estética."""
    def __init__(self, vision_model=None):
        self.expertise = "diseño industrial, ergonomía y usabilidad"
        self.vision_model = vision_model
        self.principios_ergonomia = {
            "antropometria": "Adaptarse a percentiles 5-95 de población objetivo",
            "comodidad": "Minimizar presión, evitar puntos de contacto duro",
            "alcance": "Zona de trabajo dentro del alcance natural del usuario",
            "peso": "Distribución equilibrada, centro de masa cercano al cuerpo",
            "ajustabilidad": "Permitir ajustes para diferentes usuarios"
        }

    def analyze(self, image_path, user_context="", tipo_analisis="completo"):
        """
        Analiza bocetos y diseños conceptuales con enfoque en ergonomía y estética.
        Args:
            image_path: Ruta a boceto/diseño
            user_context: Contexto del diseño (usuario objetivo, aplicación, etc)
            tipo_analisis: "completo", "ergonomia", "estetica", "proporciones"
        """
        print(f"\n🎨 Análisis conceptual ({tipo_analisis})...")
        print(f"📁 Boceto: {image_path}")
        design_prompt = f"""Eres un diseñador industrial experto en {self.expertise}.

Analiza este boceto/diseño conceptual evaluando:

1. ERGONOMÍA Y USABILIDAD:
   - Comodidad de uso para el usuario objetivo
   - Puntos de contacto con el cuerpo
   - Facilidad de colocación/remoción
   - Ajustabilidad y adaptabilidad
   - Distribución de peso

2. PROPORCIONES Y GEOMETRÍA:
   - Proporciones visuales (regla áurea, tercios)
   - Simetría y balance
   - Escala respecto al cuerpo humano
   - Coherencia formal

3. ESTÉTICA Y LENGUAJE DE DISEÑO:
   - Cohesión visual
   - Modernidad y atemporalidad
   - Psicología del color y forma
   - Percepción de calidad

4. MANUFACTURABILIDAD:
   - Complejidad de fabricación
   - Número de componentes
   - Ensamblaje intuitivo
   - Materiales sugeridos

Contexto del diseño: {user_context}

Proporciona crítica constructiva y sugerencias de mejora específicas."""
        analisis = {
            "tipo": tipo_analisis,
            "imagen": str(image_path),
            "contexto": user_context
        }
        if self.vision_model:
            try:
                resultado = self.vision_model.analizar_imagen(image_path, design_prompt)
                analisis["analisis_visual"] = resultado
                analisis["metodo"] = "Análisis visual con LLaVA"
            except Exception as e:
                print(f"⚠️ Error con visión: {e}")
                analisis["analisis_visual"] = None
                analisis["metodo"] = "Análisis estructurado"
        else:
            analisis["analisis_visual"] = None
            analisis["metodo"] = "Checklist de diseño estructurado"
        analisis["checklist_ergonomia"] = self._evaluar_ergonomia(user_context)
        analisis["sugerencias"] = self.suggest_improvements(analisis)
        return analisis

    def _evaluar_ergonomia(self, contexto):
        """Evalúa principios ergonómicos aplicables al contexto."""
        checklist = {}
        for principio, descripcion in self.principios_ergonomia.items():
            checklist[principio] = {
                "descripcion": descripcion,
                "aplicable": True,
                "estado": "pendiente_verificar"
            }
        if "exoesqueleto" in contexto.lower():
            checklist["recomendaciones_especificas"] = [
                "Usar acolchado en puntos de contacto (muslo, pantorrilla)",
                "Straps ajustables con velcro o ratchet",
                "Peso total <2kg por extremidad si es posible",
                "Permitir ventilación para evitar sudoración"
            ]
        return checklist

    def suggest_improvements(self, analysis):
        """
        Genera sugerencias de mejora basadas en el análisis.
        Args:
            analysis: Dict con análisis previo
        """
        sugerencias = {
            "ergonomia": [],
            "estetica": [],
            "manufacturabilidad": []
        }
        contexto = analysis.get("contexto", "").lower()
        sugerencias["ergonomia"] = [
            "Redondear esquinas para evitar puntos de presión",
            "Añadir superficie texturizada en zonas de agarre",
            "Verificar que controles estén en zona de alcance natural"
        ]
        sugerencias["estetica"] = [
            "Unificar lenguaje de formas (curvas o rectas, no mezclar)",
            "Considerar acabados mate para reducir reflejos",
            "Usar colores neutros con acentos funcionales"
        ]
        if "impresion" in contexto or "3d" in contexto:
            sugerencias["manufacturabilidad"] = [
                "Evitar overhangs >45° para impresión sin soportes",
                "Diseñar piezas ensamblables (snap-fit) para evitar tornillos",
                "Considerar orientación de capas para máxima resistencia"
            ]
        else:
            sugerencias["manufacturabilidad"] = [
                "Simplificar geometría para reducir costos de mecanizado",
                "Usar procesos estándar (corte, doblado) cuando sea posible",
                "Minimizar número de piezas únicas"
            ]
        print(f"\n💡 Sugerencias de mejora generadas:")
        print(f"   Ergonomía: {len(sugerencias['ergonomia'])} recomendaciones")
        print(f"   Estética: {len(sugerencias['estetica'])} recomendaciones")
        print(f"   Manufacturabilidad: {len(sugerencias['manufacturabilidad'])} recomendaciones")
        return sugerencias

    def comparar_iteraciones(self, version_anterior, version_actual):
        """
        Compara dos versiones de un diseño para evaluar evolución.
        """
        print(f"\n🔄 Comparando iteraciones de diseño...")
        print(f"   V anterior: {version_anterior}")
        print(f"   V actual: {version_actual}")
        comparacion = {
            "version_anterior": version_anterior,
            "version_actual": version_actual,
            "mejoras_detectadas": [
                "Análisis comparativo requiere integración con visión"
            ]
        }
        return comparacion
