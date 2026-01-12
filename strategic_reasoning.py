import json
import os
from datetime import datetime
import logging
from typing import List, Dict, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StrategicReasoning:
    """
    Sistema de Razonamiento Estratégico para TARS.
    Permite pensar proactivamente sobre mejoras y caminos alternativos.
    """

    def __init__(self, config_file="razonamiento_estrategico.json"):
        self.config_file = config_file
        self.strategies = self._load_strategies()
        self.learning_history = self._load_learning_history()

    def _load_strategies(self):
        """Carga estrategias de mejora conocidas"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error cargando estrategias: {e}")

        # Estrategias por defecto
        return {
            "performance_optimization": {
                "c++_backend": {
                    "description": "Usar Llama.cpp como backend C++ para inferencia más rápida",
                    "benefits": ["4x más velocidad", "16°C menos temperatura", "50% menos uso CPU"],
                    "difficulty": "media",
                    "time_estimate": "2-4 horas",
                    "prerequisites": ["llama.cpp instalado", "modelo cuantizado"],
                    "steps": [
                        "Instalar llama.cpp",
                        "Convertir modelo Phi-2 a GGUF",
                        "Cuantizar a Q4_K_M",
                        "Integrar con Python",
                        "Probar rendimiento"
                    ]
                },
                "model_quantization": {
                    "description": "Cuantizar modelos para usar menos memoria y ser más rápidos",
                    "benefits": ["50% menos VRAM", "2x más velocidad", "Compatible con RTX 30xx"],
                    "difficulty": "baja",
                    "time_estimate": "1 hora",
                    "prerequisites": ["Modelos descargados"],
                    "steps": [
                        "Identificar modelos grandes",
                        "Elegir nivel de cuantización",
                        "Convertir y probar"
                    ]
                }
            },
            "voice_improvement": {
                "rvc_cloning": {
                    "description": "Clonar voz del usuario para personalidad auténtica",
                    "benefits": ["Voz única y personal", "Mejor inmersión", "Expresión emocional"],
                    "difficulty": "media",
                    "time_estimate": "30 minutos + tiempo de entrenamiento",
                    "prerequisites": ["Audio del usuario", "GPU disponible"],
                    "steps": [
                        "Grabar audio de muestra",
                        "Entrenar modelo RVC",
                        "Integrar con TTS",
                        "Probar conversión"
                    ]
                }
            },
            "memory_systems": {
                "episodic_memory": {
                    "description": "Sistema de memoria a largo plazo para relaciones continuas",
                    "benefits": ["Recuerda conversaciones", "Relaciones personalizadas", "Contexto histórico"],
                    "difficulty": "alta",
                    "time_estimate": "4-6 horas",
                    "prerequisites": ["Base de datos", "Sistema de encriptación"],
                    "steps": [
                        "Diseñar esquema de BD",
                        "Implementar encriptación",
                        "Crear API de memoria",
                        "Integrar con personalidad",
                        "Probar persistencia"
                    ]
                }
            },
            "personality_evolution": {
                "adaptive_learning": {
                    "description": "Sistema que aprende y se adapta al estilo del usuario",
                    "benefits": ["Personalización automática", "Mejor engagement", "Relaciones naturales"],
                    "difficulty": "alta",
                    "time_estimate": "6-8 horas",
                    "prerequisites": ["Datos de usuario", "Algoritmos de ML"],
                    "steps": [
                        "Recopilar datos de conversación",
                        "Analizar patrones",
                        "Implementar aprendizaje",
                        "Crear sistema de feedback",
                        "Probar adaptación"
                    ]
                }
            }
        }

    def _load_learning_history(self):
        """Carga historial de aprendizaje y decisiones"""
        history_file = "razonamiento_history.json"
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error cargando historial: {e}")

        return {
            "implemented_strategies": [],
            "considered_strategies": [],
            "performance_metrics": {},
            "user_feedback": []
        }

    def analyze_current_state(self, system_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza el estado actual del sistema y sugiere mejoras.
        """
        analysis = {
            "current_performance": self._evaluate_performance(system_metrics),
            "identified_bottlenecks": self._identify_bottlenecks(system_metrics),
            "recommended_strategies": self._recommend_strategies(system_metrics),
            "risk_assessment": self._assess_risks(),
            "implementation_priority": self._prioritize_improvements()
        }

        return analysis

    def _evaluate_performance(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Evalúa el rendimiento actual"""
        evaluation = {
            "response_time": "good" if metrics.get("avg_response_time", 2.0) < 2.0 else "needs_improvement",
            "cpu_usage": "good" if metrics.get("cpu_usage", 80) < 70 else "high",
            "memory_usage": "good" if metrics.get("memory_usage", 80) < 75 else "high",
            "temperature": "good" if metrics.get("temperature", 75) < 70 else "hot",
            "user_satisfaction": "unknown"  # Se actualizaría con feedback
        }

        return evaluation

    def _identify_bottlenecks(self, metrics: Dict[str, Any]) -> List[str]:
        """Identifica cuellos de botella"""
        bottlenecks = []

        if metrics.get("avg_response_time", 2.0) > 2.5:
            bottlenecks.append("response_time")
        if metrics.get("cpu_usage", 80) > 80:
            bottlenecks.append("cpu_overload")
        if metrics.get("temperature", 75) > 80:
            bottlenecks.append("thermal_throttling")
        if metrics.get("memory_usage", 80) > 85:
            bottlenecks.append("memory_pressure")

        return bottlenecks

    def _recommend_strategies(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recomienda estrategias basadas en métricas"""
        recommendations = []

        # Si hay problemas de rendimiento
        if metrics.get("avg_response_time", 2.0) > 2.0:
            recommendations.append({
                "strategy": "c++_backend",
                "category": "performance_optimization",
                "reason": "Tiempo de respuesta alto detectado",
                "expected_impact": "4x más rápido",
                "confidence": 0.9
            })

        # Si hay sobrecalentamiento
        if metrics.get("temperature", 75) > 75:
            recommendations.append({
                "strategy": "c++_backend",
                "category": "performance_optimization",
                "reason": "Temperatura alta del sistema",
                "expected_impact": "16°C menos",
                "confidence": 0.85
            })

        # Si no hay voz personalizada
        if not metrics.get("voice_cloned", False):
            recommendations.append({
                "strategy": "rvc_cloning",
                "category": "voice_improvement",
                "reason": "Falta voz personalizada",
                "expected_impact": "Mejor inmersión",
                "confidence": 0.7
            })

        return recommendations

    def _assess_risks(self) -> Dict[str, Any]:
        """Evalúa riesgos de implementación"""
        return {
            "technical_risks": [
                "Incompatibilidad con versiones existentes",
                "Problemas de estabilidad inicial",
                "Curva de aprendizaje de nuevas tecnologías"
            ],
            "time_risks": [
                "Tiempo de implementación mayor a lo estimado",
                "Tiempo de prueba y validación"
            ],
            "resource_risks": [
                "Uso temporal de más recursos durante transición",
                "Posibles problemas de memoria durante conversión"
            ],
            "mitigation_strategies": [
                "Crear backups antes de cambios",
                "Implementar gradualmente con fallbacks",
                "Monitorear métricas durante transición"
            ]
        }

    def _prioritize_improvements(self) -> List[Dict[str, Any]]:
        """Prioriza mejoras por impacto vs esfuerzo"""
        priorities = [
            {
                "improvement": "Backend C++",
                "impact": "alto",
                "effort": "medio",
                "priority": "crítica",
                "reason": "Mejor rendimiento inmediato"
            },
            {
                "improvement": "Cuantización de modelos",
                "impact": "medio",
                "effort": "bajo",
                "priority": "alta",
                "reason": "Mejora eficiencia sin cambios grandes"
            },
            {
                "improvement": "Voz RVC",
                "impact": "medio",
                "effort": "medio",
                "priority": "media",
                "reason": "Mejora experiencia pero requiere audio"
            },
            {
                "improvement": "Memoria episódica",
                "impact": "alto",
                "effort": "alto",
                "priority": "media",
                "reason": "Funcionalidad avanzada pero compleja"
            }
        ]

        return priorities

    def generate_improvement_plan(self, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera un plan completo de mejoras.
        """
        analysis = self.analyze_current_state(current_metrics)

        plan = {
            "timestamp": datetime.now().isoformat(),
            "current_state": analysis["current_performance"],
            "bottlenecks": analysis["identified_bottlenecks"],
            "phased_approach": {
                "phase_1_quick_wins": [
                    strategy for strategy in analysis["recommended_strategies"]
                    if self.strategies[strategy["category"]][strategy["strategy"]]["difficulty"] == "baja"
                ],
                "phase_2_major_improvements": [
                    strategy for strategy in analysis["recommended_strategies"]
                    if self.strategies[strategy["category"]][strategy["strategy"]]["difficulty"] in ["media", "alta"]
                ]
            },
            "risk_assessment": analysis["risk_assessment"],
            "success_metrics": {
                "response_time_target": "< 1.0s",
                "cpu_usage_target": "< 50%",
                "temperature_target": "< 65°C",
                "user_satisfaction_target": "> 90%"
            },
            "contingency_plans": [
                "Mantener versión anterior como fallback",
                "Implementar features gradualmente",
                "Monitorear métricas en tiempo real"
            ]
        }

        return plan

    def record_decision(self, decision: str, outcome: str, metrics: Dict[str, Any]):
        """Registra decisiones y resultados para aprendizaje futuro"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "outcome": outcome,
            "metrics_before": metrics,
            "lessons_learned": self._extract_lessons(outcome)
        }

        self.learning_history["implemented_strategies"].append(record)
        self._save_learning_history()

    def _extract_lessons(self, outcome: str) -> List[str]:
        """Extrae lecciones del resultado"""
        lessons = []

        if "success" in outcome.lower():
            lessons.extend([
                "La estrategia funcionó bien",
                "Considerar implementación similar en el futuro",
                "Documentar proceso para referencia"
            ])
        elif "failure" in outcome.lower():
            lessons.extend([
                "Revisar requisitos previos",
                "Considerar complejidad adicional",
                "Evaluar alternativas"
            ])

        return lessons

    def _save_learning_history(self):
        """Guarda el historial de aprendizaje"""
        try:
            with open("razonamiento_history.json", 'w', encoding='utf-8') as f:
                json.dump(self.learning_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando historial: {e}")

    def get_strategic_advice(self, context: str) -> str:
        """
        Proporciona consejo estratégico basado en el contexto.
        """
        context_lower = context.lower()

        # Consejos sobre optimización
        if any(word in context_lower for word in ['lento', 'calor', 'cpu', 'rendimiento']):
            return (
                "💡 **CONSEJO ESTRATÉGICO:** Si notas rendimiento lento o calor excesivo, "
                "la optimización con C++ (Llama.cpp) es el camino más efectivo. "
                "Reduce temperatura 16°C y acelera respuestas 4x. "
                "Es una mejora 'quick win' con gran impacto."
            )

        # Consejos sobre voz
        elif any(word in context_lower for word in ['voz', 'hablar', 'sonido']):
            return (
                "🎭 **CONSEJO ESTRATÉGICO:** Para voz auténtica, considera RVC voice cloning. "
                "Crea una voz única basada en tu audio real. "
                "Es más inmersivo que TTS estándar y muestra personalidad real."
            )

        # Consejos sobre memoria
        elif any(word in context_lower for word in ['recuerda', 'memoria', 'olvida']):
            return (
                "🧠 **CONSEJO ESTRATÉGICO:** La memoria episódica es clave para relaciones duraderas. "
                "Permite que TARS recuerde conversaciones pasadas y preferencias. "
                "Es complejo de implementar pero transforma la experiencia del usuario."
            )

        # Consejos generales
        else:
            return (
                "🔄 **CONSEJO ESTRATÉGICO:** Cuando pienses en mejorar TARS, considera múltiples caminos: "
                "1) **Rendimiento** (C++ backend) - Impacto inmediato, medio esfuerzo. "
                "2) **Personalización** (voz RVC, memoria) - Mejor experiencia, más esfuerzo. "
                "3) **Escalabilidad** (arquitectura modular) - Para crecimiento futuro. "
                "¿Qué aspecto te preocupa más?"
            )