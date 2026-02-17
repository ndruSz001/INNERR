import math
from pathlib import Path
import json

class BrainMechanical:
    """Análisis mecánico y cálculos de ingeniería para prototipos."""
    def __init__(self, vision_model=None):
        self.expertise = "ingeniería mecánica, cinemática y análisis estructural"
        self.vision_model = vision_model
        self.materiales = {
            "aluminio_6061": {"densidad": 2.7, "resistencia_traccion": 310, "modulo_young": 68.9},
            "acero_inox_316": {"densidad": 8.0, "resistencia_traccion": 515, "modulo_young": 193},
            "abs_impresion3d": {"densidad": 1.04, "resistencia_traccion": 40, "modulo_young": 2.3},
            "pla_impresion3d": {"densidad": 1.25, "resistencia_traccion": 50, "modulo_young": 3.5},
            "fibra_carbono": {"densidad": 1.6, "resistencia_traccion": 600, "modulo_young": 70}
        }

    def analyze(self, image_path, user_context="", tipo_analisis="general"):
        """
        Analiza diseños mecánicos, estructuras y componentes.
        Args:
            image_path: Ruta a imagen de diseño/prototipo
            user_context: Contexto del diseño
            tipo_analisis: "general", "estructural", "cinematico"
        """
        print(f"\n⚙️ Análisis mecánico ({tipo_analisis})...")
        print(f"📁 Imagen: {image_path}")
        mechanical_prompt = f"""Eres un ingeniero mecánico experto en {self.expertise}.

Analiza este diseño/prototipo mecánico enfocándote en:

1. ANÁLISIS ESTRUCTURAL:
   - Identificar componentes principales (eslabones, articulaciones, actuadores)
   - Evaluar puntos de tensión y carga
   - Detectar posibles puntos de falla

2. CINEMÁTICA:
   - Grados de libertad (DOF)
   - Rangos de movimiento
   - Cadena cinemática y configuración

3. MATERIALES Y MANUFACTURA:
   - Materiales sugeridos para cada componente
   - Procesos de fabricación recomendados
   - Consideraciones de ensamblaje

4. ACTUACIÓN Y CONTROL:
   - Ubicación óptima de actuadores
   - Estimación de torques requeridos
   - Consideraciones de control

Contexto del diseño: {user_context}

Proporciona análisis técnico detallado y recomendaciones de mejora."""
        analisis = {
            "tipo": tipo_analisis,
            "imagen": str(image_path),
            "contexto": user_context
        }
        if self.vision_model:
            try:
                resultado = self.vision_model.analizar_imagen(image_path, mechanical_prompt)
                analisis["analisis_visual"] = resultado
                analisis["metodo"] = "Análisis visual con LLaVA"
            except Exception as e:
                print(f"⚠️ Error con visión: {e}")
                analisis["analisis_visual"] = None
                analisis["metodo"] = "Análisis estructurado"
        else:
            analisis["analisis_visual"] = None
            analisis["metodo"] = "Análisis estructurado (sin visión)"
        analisis["recomendaciones"] = self._generar_recomendaciones_mecanicas(user_context)
        return analisis

    def _generar_recomendaciones_mecanicas(self, contexto):
        """Genera recomendaciones basadas en buenas prácticas de ingeniería."""
        recomendaciones = []
        if "exoesqueleto" in contexto.lower():
            recomendaciones.extend([
                "Usar actuadores con reductor planetario para mayor torque",
                "Implementar encoders para control de posición preciso",
                "Diseñar con factor de seguridad mínimo de 2.5x para cargas dinámicas",
                "Considerar backdrivability si requiere transparencia"
            ])
        if "servo" in contexto.lower() or "motor" in contexto.lower():
            recomendaciones.extend([
                "Verificar que el torque del motor supere el torque requerido + 20%",
                "Añadir disipador térmico si opera >30 min continuos",
                "Implementar límites de corriente para protección"
            ])
        return recomendaciones

    def calculate_torque(self, fuerza_N, distancia_m, angulo_deg=90):
        """
        Calcula torque requerido.
        Args:
            fuerza_N: Fuerza aplicada en Newtons
            distancia_m: Distancia al eje de rotación en metros
            angulo_deg: Ángulo de aplicación en grados (90° = perpendicular)
        Returns:
            Dict con cálculo de torque
        """
        angulo_rad = math.radians(angulo_deg)
        torque_Nm = fuerza_N * distancia_m * math.sin(angulo_rad)
        resultado = {
            "torque_Nm": round(torque_Nm, 2),
            "torque_kgcm": round(torque_Nm * 10.197, 2),
            "fuerza_N": fuerza_N,
            "distancia_m": distancia_m,
            "angulo_deg": angulo_deg,
            "formula": "τ = F × d × sin(θ)"
        }
        print(f"\n⚙️ Cálculo de Torque:")
        print(f"   Fuerza: {fuerza_N} N")
        print(f"   Distancia: {distancia_m} m")
        print(f"   Ángulo: {angulo_deg}°")
        print(f"   → Torque: {resultado['torque_Nm']} Nm ({resultado['torque_kgcm']} kg·cm)")
        return resultado

    def seleccionar_motor(self, torque_requerido_Nm, velocidad_rpm=None):
        """
        Sugiere motores apropiados basado en torque requerido.
        """
        motores = [
            {"modelo": "MG996R Servo", "torque_Nm": 1.1, "velocidad_rpm": 60, "tipo": "servo"},
            {"modelo": "DS3218 Servo", "torque_Nm": 2.0, "velocidad_rpm": 55, "tipo": "servo"},
            {"modelo": "Dynamixel MX-64", "torque_Nm": 6.0, "velocidad_rpm": 78, "tipo": "servo_smart"},
            {"modelo": "Maxon EC45 + GP52", "torque_Nm": 15.0, "velocidad_rpm": 30, "tipo": "motor_reductor"},
            {"modelo": "Motor DC 200W + Reductor 1:50", "torque_Nm": 45.0, "velocidad_rpm": 25, "tipo": "motor_reductor"}
        ]
        torque_con_margen = torque_requerido_Nm * 1.2
        motores_apropiados = [
            m for m in motores 
            if m["torque_Nm"] >= torque_con_margen
        ]
        if motores_apropiados:
            motores_apropiados.sort(key=lambda x: x["torque_Nm"])
            print(f"\n🔧 Motores recomendados para {torque_requerido_Nm} Nm:")
            for m in motores_apropiados[:3]:
                print(f"   - {m['modelo']}: {m['torque_Nm']} Nm @ {m['velocidad_rpm']} rpm")
        else:
            print(f"⚠️ No hay motores en la base de datos para {torque_requerido_Nm} Nm")
            print(f"   Considera motor custom o reductor de mayor ratio")
        return motores_apropiados

    def validar_material(self, material, carga_N, area_mm2):
        """
        Valida si un material soporta la carga especificada.
        """
        if material not in self.materiales:
            return {"error": f"Material '{material}' no en base de datos"}
        props = self.materiales[material]
        esfuerzo_MPa = carga_N / area_mm2
        factor_seguridad = props["resistencia_traccion"] / esfuerzo_MPa
        es_seguro = factor_seguridad >= 2.0
        resultado = {
            "material": material,
            "carga_N": carga_N,
            "area_mm2": area_mm2,
            "esfuerzo_MPa": round(esfuerzo_MPa, 2),
            "resistencia_material_MPa": props["resistencia_traccion"],
            "factor_seguridad": round(factor_seguridad, 2),
            "es_seguro": es_seguro,
            "recomendacion": "✅ Seguro" if es_seguro else "❌ Insuficiente - aumentar área o cambiar material"
        }
        return resultado
