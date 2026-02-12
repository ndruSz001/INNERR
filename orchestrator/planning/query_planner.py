"""
Query Planner - Construye plan de ejecución para queries

Responsabilidad: Crear secuencia de pasos basado en tipo de query
- Deterministic execution plan
- Fallback strategies
- Resource optimization
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class StepType(str, Enum):
    """Tipos de pasos en plan de ejecución"""
    GENERATE_EMBEDDING = "generate_embedding"
    SEARCH_PROJECTS = "search_projects"
    SEARCH_SEMANTIC = "search_semantic"
    LOAD_HISTORY = "load_conversation_history"
    RETRIEVE_CONTEXT = "retrieve_context"
    GENERATE_RESPONSE = "generate_response"
    SYNTHESIZE = "synthesize_response"
    VALIDATE = "validate_response"


@dataclass
class ExecutionStep:
    """Un paso en el plan de ejecución"""
    step_type: StepType
    description: str
    target: str  # "pc1" o "pc2"
    params: Dict[str, Any] = field(default_factory=dict)
    fallback: Optional['ExecutionStep'] = None
    timeout_seconds: int = 30
    
    def __repr__(self) -> str:
        return f"Step({self.step_type.value}→{self.target})"


@dataclass
class ExecutionPlan:
    """Plan de ejecución para una query"""
    query_id: str
    steps: List[ExecutionStep]
    estimated_time_seconds: float
    fallback_plan: Optional['ExecutionPlan'] = None
    
    def __repr__(self) -> str:
        return f"Plan({self.query_id}, {len(self.steps)} steps, {self.estimated_time_seconds:.1f}s)"


class QueryPlanner:
    """Planificador de queries - construye planes de ejecución"""
    
    def __init__(self):
        """Inicializar planner"""
        self.step_timings = {
            StepType.GENERATE_EMBEDDING: 0.5,
            StepType.SEARCH_PROJECTS: 0.3,
            StepType.SEARCH_SEMANTIC: 1.0,
            StepType.LOAD_HISTORY: 0.2,
            StepType.RETRIEVE_CONTEXT: 0.5,
            StepType.GENERATE_RESPONSE: 3.0,
            StepType.SYNTHESIZE: 2.0,
            StepType.VALIDATE: 0.5,
        }
    
    def plan(
        self,
        query: str,
        query_id: str,
        routing_decision: Any  # RoutingDecision
    ) -> ExecutionPlan:
        """
        Construir plan de ejecución para query
        
        Args:
            query: Query del usuario
            query_id: ID único para esta query
            routing_decision: Decisión de routing (de QueryRouter)
            
        Returns:
            ExecutionPlan con secuencia de pasos
        """
        steps = []
        total_time = 0.0
        
        route_type = routing_decision.route_type
        
        # ========== PASOS COMUNES ==========
        
        if routing_decision.needs_embedding:
            step = ExecutionStep(
                step_type=StepType.GENERATE_EMBEDDING,
                description="Generar embedding de query",
                target="pc1",
                params={'query': query},
                timeout_seconds=5
            )
            steps.append(step)
            total_time += self.step_timings[StepType.GENERATE_EMBEDDING]
        
        if routing_decision.needs_conversation_history:
            step = ExecutionStep(
                step_type=StepType.LOAD_HISTORY,
                description="Cargar historial de conversación",
                target="pc1",
                params={'limit': 5},
                timeout_seconds=5
            )
            steps.append(step)
            total_time += self.step_timings[StepType.LOAD_HISTORY]
        
        # ========== PASOS ESPECÍFICOS POR RUTA ==========
        
        if route_type.value == "needs_context":
            
            if routing_decision.needs_project_search:
                step = ExecutionStep(
                    step_type=StepType.SEARCH_PROJECTS,
                    description="Buscar proyectos relevantes",
                    target="pc1",
                    params={'query': query, 'limit': 3},
                    timeout_seconds=10,
                    fallback=ExecutionStep(
                        step_type=StepType.GENERATE_RESPONSE,
                        description="Fallback: generar sin contexto",
                        target="pc1",
                        timeout_seconds=30
                    )
                )
                steps.append(step)
                total_time += self.step_timings[StepType.SEARCH_PROJECTS]
            
            # Buscar contexto semántico
            step = ExecutionStep(
                step_type=StepType.RETRIEVE_CONTEXT,
                description="Recuperar contexto relevante",
                target="pc2",
                params={'top_k': 3},
                timeout_seconds=15,
                fallback=ExecutionStep(
                    step_type=StepType.GENERATE_RESPONSE,
                    description="Fallback: generar sin contexto",
                    target="pc1",
                    timeout_seconds=30
                )
            )
            steps.append(step)
            total_time += self.step_timings[StepType.RETRIEVE_CONTEXT]
            
            # Generar respuesta con contexto
            step = ExecutionStep(
                step_type=StepType.GENERATE_RESPONSE,
                description="Generar respuesta con contexto",
                target="pc1",
                params={'with_context': True},
                timeout_seconds=30
            )
            steps.append(step)
            total_time += self.step_timings[StepType.GENERATE_RESPONSE]
        
        elif route_type.value == "synthesis":
            
            # Buscar múltiples fuentes
            step = ExecutionStep(
                step_type=StepType.SEARCH_SEMANTIC,
                description="Buscar múltiples fuentes para síntesis",
                target="pc2",
                params={'top_k': 5},
                timeout_seconds=20,
                fallback=ExecutionStep(
                    step_type=StepType.GENERATE_RESPONSE,
                    description="Fallback: generar sin síntesis",
                    target="pc1",
                    timeout_seconds=30
                )
            )
            steps.append(step)
            total_time += self.step_timings[StepType.SEARCH_SEMANTIC]
            
            # Sintetizar respuesta
            step = ExecutionStep(
                step_type=StepType.SYNTHESIZE,
                description="Sintetizar respuesta de múltiples fuentes",
                target="pc2",
                params={'sources': 'multiple'},
                timeout_seconds=30
            )
            steps.append(step)
            total_time += self.step_timings[StepType.SYNTHESIZE]
        
        else:  # inference_only
            
            # Simple: generar respuesta directo
            step = ExecutionStep(
                step_type=StepType.GENERATE_RESPONSE,
                description="Generar respuesta",
                target="pc1",
                params={'with_context': False},
                timeout_seconds=30
            )
            steps.append(step)
            total_time += self.step_timings[StepType.GENERATE_RESPONSE]
        
        # ========== VALIDACIÓN FINAL ==========
        
        step = ExecutionStep(
            step_type=StepType.VALIDATE,
            description="Validar respuesta",
            target="pc1",
            params={},
            timeout_seconds=5
        )
        steps.append(step)
        total_time += self.step_timings[StepType.VALIDATE]
        
        plan = ExecutionPlan(
            query_id=query_id,
            steps=steps,
            estimated_time_seconds=total_time
        )
        
        logger.info(f"📋 Plan creado: {plan}")
        logger.debug(f"   Steps: {[str(s) for s in plan.steps]}")
        
        return plan
    
    def get_steps_for_target(
        self,
        plan: ExecutionPlan,
        target: str
    ) -> List[ExecutionStep]:
        """
        Obtener pasos para un target específico
        
        Args:
            plan: ExecutionPlan
            target: "pc1" o "pc2"
            
        Returns:
            Pasos para ese target
        """
        return [step for step in plan.steps if step.target == target]
