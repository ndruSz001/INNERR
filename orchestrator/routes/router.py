"""
Query Router - Decide qué tipo de procesamiento necesita cada query

Responsabilidad: Clasificar queries en 3 categorías
1. inference_only: Solo generar respuesta (→ PC1)
2. needs_context: Buscar contexto primero (→ PC2)
3. synthesis: Múltiples fuentes + síntesis (→ PC2)
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RoutingType(str, Enum):
    """Tipos de routing disponibles"""
    INFERENCE_ONLY = "inference_only"    # Solo generar
    NEEDS_CONTEXT = "needs_context"      # Buscar contexto
    SYNTHESIS = "synthesis"              # Múltiples fuentes


@dataclass
class RoutingDecision:
    """Decisión de routing para una query"""
    route_type: RoutingType
    confidence: float  # 0.0 - 1.0
    reason: str
    needs_embedding: bool = False
    needs_project_search: bool = False
    needs_conversation_history: bool = False
    
    def __repr__(self) -> str:
        return f"Route({self.route_type.value}, conf={self.confidence:.2f})"


class QueryRouter:
    """Router de queries - clasifica según tipo de procesamiento"""
    
    def __init__(self):
        """Inicializar router"""
        self.keywords_context = {
            'proyecto', 'file', 'archivo', 'documento', 'búsqueda',
            'search', 'find', 'busca', 'documento', 'pdf',
            'memoria', 'recuerda', 'remember', 'previous'
        }
        
        self.keywords_synthesis = {
            'compara', 'compare', 'contrasta', 'contrast',
            'analiza', 'analyze', 'resume', 'summary', 'resumen',
            'como', 'how', 'por qué', 'why', 'diferencia', 'difference'
        }
        
        self.keywords_simple = {
            'hola', 'hi', 'hello', 'eres', 'are you', 'como estás',
            'that', 'this', 'why', 'what', 'donde', 'where'
        }
    
    def route(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> RoutingDecision:
        """
        Determinar tipo de routing para query
        
        Lógica:
        1. ¿Menciona proyectos/archivos? → needs_context
        2. ¿Pide comparación/síntesis? → synthesis
        3. ¿Es pregunta simple? → inference_only
        
        Args:
            query: Query del usuario
            context: Contexto adicional (conversación anterior, etc)
            
        Returns:
            RoutingDecision con tipo y razón
        """
        query_lower = query.lower()
        
        # Análisis de keywords
        has_context_keywords = any(
            keyword in query_lower for keyword in self.keywords_context
        )
        
        has_synthesis_keywords = any(
            keyword in query_lower for keyword in self.keywords_synthesis
        )
        
        has_simple_keywords = any(
            keyword in query_lower for keyword in self.keywords_simple
        )
        
        # Heurísticas adicionales
        is_question = query.strip().endswith('?')
        is_long = len(query.split()) > 20
        has_project_ref = 'proj_' in query or '#' in query  # IDs de proyectos
        
        # Decidir routing basado en heurísticas
        
        if has_project_ref or has_context_keywords:
            # Tiene referencias a proyectos o contexto
            logger.info(f"🔍 Route: needs_context (keywords={has_context_keywords}, refs={has_project_ref})")
            return RoutingDecision(
                route_type=RoutingType.NEEDS_CONTEXT,
                confidence=0.85,
                reason="Query menciona proyectos o archivos",
                needs_project_search=True,
                needs_embedding=True
            )
        
        if has_synthesis_keywords and (is_long or is_question):
            # Pide síntesis/análisis profundo
            logger.info(f"🔄 Route: synthesis (keywords={has_synthesis_keywords})")
            return RoutingDecision(
                route_type=RoutingType.SYNTHESIS,
                confidence=0.80,
                reason="Query pide análisis o síntesis de múltiples fuentes",
                needs_embedding=True,
                needs_conversation_history=True
            )
        
        # Por defecto: inference_only
        logger.info(f"⚡ Route: inference_only (simple query)")
        return RoutingDecision(
            route_type=RoutingType.INFERENCE_ONLY,
            confidence=0.70,
            reason="Query simple, solo generar respuesta"
        )
    
    def get_processing_steps(self, decision: RoutingDecision) -> List[str]:
        """
        Obtener pasos de procesamiento según decisión
        
        Args:
            decision: RoutingDecision
            
        Returns:
            Lista de pasos ordenados
        """
        steps = []
        
        if decision.needs_embedding:
            steps.append("generate_embedding")
        
        if decision.needs_project_search:
            steps.append("search_projects")
        
        if decision.needs_conversation_history:
            steps.append("load_conversation_history")
        
        if decision.route_type == RoutingType.NEEDS_CONTEXT:
            steps.extend([
                "retrieve_context",
                "generate_response_with_context"
            ])
        elif decision.route_type == RoutingType.SYNTHESIS:
            steps.extend([
                "retrieve_multiple_sources",
                "synthesize_response"
            ])
        else:  # inference_only
            steps.append("generate_response")
        
        return steps
