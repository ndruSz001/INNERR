"""
Orchestrator Main - Punto de entrada del servicio de orquestación

Responsabilidad: Coordinar routers, planners y sintetizadores
Integra todas las piezas del Sprint 1
"""

import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Importar componentes
from orchestrator.routes.router import QueryRouter, RoutingType
from orchestrator.planning.query_planner import QueryPlanner
from orchestrator.synthesis.response_synthesizer import ResponseSynthesizer
from core.memory.conversation_store import ConversationStore
from core.memory.project_store import ProjectStore
from core.memory.semantic_index import SemanticIndex
from core.inference.inference_engine import InferenceEngine

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)


class Orchestrator:
    """
    Orquestador central - coordina procesamiento de queries
    
    Responsabilidades:
    1. Recibir query del usuario
    2. Decidir tipo de procesamiento (Router)
    3. Construir plan de ejecución (Planner)
    4. Ejecutar pasos
    5. Sintetizar resultado (Synthesizer)
    """
    
    def __init__(
        self,
        enable_memory: bool = True,
        enable_inference: bool = True,
        enable_semantic: bool = False
    ):
        """
        Inicializar orquestador
        
        Args:
            enable_memory: Habilitar almacenamiento en memoria
            enable_inference: Habilitar inference engine
            enable_semantic: Habilitar búsqueda semántica
        """
        self.orchestrator_id = str(uuid.uuid4())
        self.start_time = datetime.now()
        
        # Inicializar componentes
        self.router = QueryRouter()
        self.planner = QueryPlanner()
        self.synthesizer = ResponseSynthesizer()
        
        # Memoria
        self.conversation_store = ConversationStore() if enable_memory else None
        self.project_store = ProjectStore() if enable_memory else None
        self.semantic_index = SemanticIndex(enabled=enable_semantic)
        
        # Inferencia
        self.inference_engine = InferenceEngine(
            use_transformers=enable_inference
        ) if enable_inference else None
        
        logger.info(f"✅ Orchestrator initialized: {self.orchestrator_id}")
        logger.info(f"   Memory: {enable_memory}")
        logger.info(f"   Inference: {enable_inference}")
        logger.info(f"   Semantic: {enable_semantic}")
    
    def process(
        self,
        query: str,
        user_id: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Procesar query del usuario de principio a fin
        
        Args:
            query: Query del usuario
            user_id: ID del usuario
            conversation_id: ID de conversación (opcional)
            
        Returns:
            {
                'response': str,
                'routing_type': str,
                'processing_time': float,
                'sources': List[dict],
                'conversation_id': str
            }
        """
        query_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🔄 Procesando query: {query[:50]}...")
        logger.info(f"   Query ID: {query_id}")
        logger.info(f"   Usuario: {user_id}")
        logger.info(f"{'='*60}\n")
        
        # Crear o cargar conversación
        if not conversation_id and self.conversation_store:
            conversation_id = self.conversation_store.add_conversation(
                user_id=user_id,
                title=query[:50] + "...",
                initial_message=query
            )
            logger.info(f"✨ Nueva conversación: {conversation_id}")
        
        # 1. ROUTING - Decidir tipo de procesamiento
        logger.info("1️⃣  ROUTING")
        routing_decision = self.router.route(query, {})
        logger.info(f"   Decisión: {routing_decision}")
        
        # 2. PLANNING - Construir plan de ejecución
        logger.info("\n2️⃣  PLANNING")
        plan = self.planner.plan(
            query=query,
            query_id=query_id,
            routing_decision=routing_decision
        )
        logger.info(f"   Plan: {plan}")
        logger.info(f"   Pasos: {len(plan.steps)}")
        for i, step in enumerate(plan.steps, 1):
            logger.debug(f"      {i}. {step.description}")
        
        # 3. EXECUTION - Ejecutar pasos
        logger.info("\n3️⃣  EXECUTION")
        execution_results = self._execute_plan(plan, query, user_id)
        
        # 4. SYNTHESIS - Combinar resultados
        logger.info("\n4️⃣  SYNTHESIS")
        final_response = self._synthesize_response(
            query=query,
            execution_results=execution_results,
            routing_decision=routing_decision
        )
        
        # 5. SAVE - Guardar en memoria
        if self.conversation_store and conversation_id:
            self.conversation_store.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=final_response[:200] + "..."
            )
            logger.info(f"💾 Respuesta guardada en conversación")
        
        # Calcular tiempo total
        processing_time = (datetime.now() - start_time).total_seconds()
        
        result = {
            'response': final_response,
            'routing_type': routing_decision.route_type.value,
            'processing_time': processing_time,
            'query_id': query_id,
            'conversation_id': conversation_id,
            'status': 'success'
        }
        
        logger.info(f"\n✅ Procesamiento completado en {processing_time:.2f}s")
        logger.info(f"   Tipo: {result['routing_type']}")
        logger.info(f"   Respuesta: {final_response[:50]}...\n")
        
        return result
    
    def _execute_plan(
        self,
        plan: Any,  # ExecutionPlan
        query: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Ejecutar plan de ejecución
        
        Returns:
            {
                'generated_response': str,
                'context_results': List[dict],
                'project_results': List[dict],
                'execution_time': float
            }
        """
        results = {
            'generated_response': '',
            'context_results': [],
            'project_results': [],
            'history': []
        }
        
        for step in plan.steps:
            logger.debug(f"   ⚙️  Ejecutando: {step.description}")
            
            # En Sprint 1, simulamos la ejecución
            # En Sprint 2, implementaremos RPC real
            
            if step.step_type.value == "generate_response":
                # Generar respuesta con inference engine
                if self.inference_engine:
                    try:
                        response = self.inference_engine.generate(
                            prompt=query,
                            max_tokens=200
                        )
                        results['generated_response'] = response
                        logger.debug(f"      ✅ Respuesta generada ({len(response)} chars)")
                    except Exception as e:
                        logger.error(f"      ❌ Error generando: {e}")
                        results['generated_response'] = query  # Fallback
        
        return results
    
    def _synthesize_response(
        self,
        query: str,
        execution_results: Dict[str, Any],
        routing_decision: Any  # RoutingDecision
    ) -> str:
        """Sintetizar respuesta final"""
        
        generated = execution_results.get('generated_response', '')
        
        if not generated:
            generated = f"Procesé tu query: {query}"
        
        # Sintetizar con synthesizer
        response = self.synthesizer.synthesize(
            query=query,
            generated_response=generated,
            context_results=execution_results.get('context_results'),
            project_results=execution_results.get('project_results'),
            conversation_history=execution_results.get('history')
        )
        
        return response
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado del orquestador"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        status = {
            'orchestrator_id': self.orchestrator_id,
            'uptime_seconds': uptime,
            'memory_enabled': bool(self.conversation_store),
            'inference_enabled': bool(self.inference_engine),
        }
        
        if self.conversation_store:
            status['memory_stats'] = self.conversation_store.get_stats()
        
        if self.project_store:
            status['project_stats'] = self.project_store.get_stats()
        
        return status


# ============ Interfaz CLI para Sprint 1 ============

if __name__ == "__main__":
    import sys
    
    # Crear orquestador
    orch = Orchestrator(
        enable_memory=True,
        enable_inference=True,
        enable_semantic=False  # PC2 no disponible en Sprint 1
    )
    
    print("\n" + "="*70)
    print("🚀 TARS Orchestrator - Sprint 1")
    print("="*70)
    print(f"Orchestrator ID: {orch.orchestrator_id}")
    print("Escribe 'exit' para salir\n")
    
    user_id = "user_default"
    conv_id = None
    
    while True:
        try:
            query = input("Tu: ").strip()
            
            if query.lower() in ['exit', 'quit', 'salir']:
                print("\n👋 Hasta luego!")
                break
            
            if not query:
                continue
            
            # Procesar
            result = orch.process(
                query=query,
                user_id=user_id,
                conversation_id=conv_id
            )
            
            conv_id = result['conversation_id']
            
            print(f"\nTARS: {result['response']}\n")
            print(f"[{result['routing_type']} | {result['processing_time']:.2f}s]\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            logger.exception("Unhandled exception")
