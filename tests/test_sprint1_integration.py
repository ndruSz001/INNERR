"""
Integration Test - Sprint 1 Completo

Valida que todos los módulos de Sprint 1 se importan y funcionan
en conjunto correctamente.
"""

import pytest
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestSprint1Integration:
    """Test de integración completa Sprint 1"""
    
    def test_imports_phase1_inference(self):
        """✅ FASE 1: Importar módulos de inferencia"""
        logger.info("🧪 Test: FASE 1 - Imports Inference")
        
        from core.inference.llm_backend import LlamaCppBackend
        from core.inference.ollama_backend import OllamaBackend
        from core.inference.transformers_backend import TransformersBackend
        from core.inference.inference_engine import InferenceEngine
        
        logger.info("   ✅ Todos los backends importados correctamente")
    
    def test_imports_phase2_memory(self):
        """✅ FASE 2: Importar módulos de memoria"""
        logger.info("🧪 Test: FASE 2 - Imports Memory")
        
        from core.memory.conversation_store import ConversationStore
        from core.memory.project_store import ProjectStore
        from core.memory.semantic_index import SemanticIndex
        from core.apis.memory_api import MemoryAPI
        
        logger.info("   ✅ Todos los módulos de memoria importados")
    
    def test_imports_phase3_orchestrator(self):
        """✅ FASE 3: Importar módulos de orquestador"""
        logger.info("🧪 Test: FASE 3 - Imports Orchestrator")
        
        from orchestrator.routes.router import QueryRouter, RoutingType
        from orchestrator.planning.query_planner import QueryPlanner
        from orchestrator.synthesis.response_synthesizer import ResponseSynthesizer
        from orchestrator.main import Orchestrator
        
        logger.info("   ✅ Todos los módulos del orquestador importados")
    
    def test_conversation_store_basic(self):
        """✅ Conversation Store CRUD"""
        logger.info("🧪 Test: Conversation Store")
        
        from core.memory.conversation_store import ConversationStore
        
        store = ConversationStore()
        
        # Create
        conv_id = store.add_conversation("user1", "Test Conversation", "Hola")
        assert conv_id is not None
        logger.info(f"   ✅ Conversación creada: {conv_id}")
        
        # Add message
        result = store.add_message(conv_id, "user", "¿Cómo estás?")
        assert result is True
        logger.info("   ✅ Mensaje agregado")
        
        # Get
        conv = store.get_conversation(conv_id)
        assert conv is not None
        assert len(conv['messages']) >= 1
        logger.info("   ✅ Conversación recuperada")
        
        # List
        convs = store.list_conversations("user1")
        assert len(convs) > 0
        logger.info(f"   ✅ Conversaciones listadas: {len(convs)}")
        
        # Cleanup
        result = store.delete_conversation(conv_id)
        assert result is True
        logger.info("   ✅ Conversación eliminada")
    
    def test_project_store_basic(self):
        """✅ Project Store CRUD"""
        logger.info("🧪 Test: Project Store")
        
        from core.memory.project_store import ProjectStore
        
        store = ProjectStore()
        
        # Create
        proj_id = store.create_project_summary(
            name="Test Project",
            summary="This is a test project summary",
            keywords=["test", "python"],
            tags=["completed"]
        )
        assert proj_id is not None
        logger.info(f"   ✅ Proyecto creado: {proj_id}")
        
        # Get
        proj = store.get_project_summary(proj_id)
        assert proj is not None
        assert proj['name'] == "Test Project"
        logger.info("   ✅ Proyecto recuperado")
        
        # Search
        results = store.search_projects(keywords=["test"])
        assert len(results) > 0
        logger.info(f"   ✅ Búsqueda funcionó: {len(results)} resultados")
        
        # Delete
        result = store.delete_project(proj_id)
        assert result is True
        logger.info("   ✅ Proyecto eliminado")
    
    def test_semantic_index_stub(self):
        """✅ Semantic Index (stub)"""
        logger.info("🧪 Test: Semantic Index")
        
        from core.memory.semantic_index import SemanticIndex
        
        index = SemanticIndex(enabled=False)  # Stub, PC2 no disponible
        
        # Search (debería devolver vacio en stub)
        results = index.search_similar([0.1, 0.2, 0.3], top_k=5)
        assert results == []
        logger.info("   ✅ Búsqueda semántica stub funcionando")
        
        # Status
        status = index.get_embedding_status()
        assert status is not None
        logger.info("   ✅ Status obtenido")
    
    def test_query_router(self):
        """✅ Query Router"""
        logger.info("🧪 Test: Query Router")
        
        from orchestrator.routes.router import QueryRouter, RoutingType
        
        router = QueryRouter()
        
        # Simple query
        decision = router.route("Hola, ¿cómo estás?", {})
        assert decision.route_type in [
            RoutingType.INFERENCE_ONLY,
            RoutingType.NEEDS_CONTEXT,
            RoutingType.SYNTHESIS
        ]
        logger.info(f"   ✅ Query simple routed: {decision.route_type.value}")
        
        # Context query
        decision = router.route("¿Qué archivos tengo en el proyecto?", {})
        assert decision.route_type is not None
        logger.info(f"   ✅ Query con contexto routed: {decision.route_type.value}")
        
        # Synthesis query
        decision = router.route("Compara los dos últimos proyectos", {})
        assert decision.route_type is not None
        logger.info(f"   ✅ Query de síntesis routed: {decision.route_type.value}")
    
    def test_query_planner(self):
        """✅ Query Planner"""
        logger.info("🧪 Test: Query Planner")
        
        from orchestrator.planning.query_planner import QueryPlanner
        from orchestrator.routes.router import QueryRouter, RoutingType, RoutingDecision
        
        planner = QueryPlanner()
        router = QueryRouter()
        
        # Plan for simple query
        decision = router.route("Hola", {})
        plan = planner.plan("Hola", "query_123", decision)
        
        assert plan is not None
        assert len(plan.steps) > 0
        logger.info(f"   ✅ Plan creado: {len(plan.steps)} pasos")
        
        for i, step in enumerate(plan.steps, 1):
            logger.debug(f"      Paso {i}: {step.step_type.value} → {step.target}")
    
    def test_response_synthesizer(self):
        """✅ Response Synthesizer"""
        logger.info("🧪 Test: Response Synthesizer")
        
        from orchestrator.synthesis.response_synthesizer import ResponseSynthesizer
        
        synth = ResponseSynthesizer()
        
        # Simple synthesis
        response = synth.synthesize(
            query="¿Cuál es la capital de Francia?",
            generated_response="París"
        )
        
        assert response is not None
        assert len(response) > 0
        logger.info(f"   ✅ Síntesis exitosa: {len(response)} chars")
        
        # Validate
        valid = synth.validate_synthesis(response)
        assert valid is True
        logger.info("   ✅ Validación exitosa")
    
    def test_orchestrator_initialization(self):
        """✅ Orchestrator Initialization"""
        logger.info("🧪 Test: Orchestrator")
        
        from orchestrator.main import Orchestrator
        
        orch = Orchestrator(
            enable_memory=True,
            enable_inference=False,  # No inference engine por ahora
            enable_semantic=False    # PC2 no disponible
        )
        
        assert orch is not None
        assert orch.orchestrator_id is not None
        logger.info(f"   ✅ Orquestador inicializado: {orch.orchestrator_id}")
        
        # Status
        status = orch.get_status()
        assert status is not None
        logger.info(f"   ✅ Status: {status}")
    
    def test_full_pipeline_without_inference(self):
        """⚠️ Full Pipeline (sin inference engine)"""
        logger.info("🧪 Test: Full Pipeline (sin LLM)")
        
        from orchestrator.main import Orchestrator
        
        orch = Orchestrator(
            enable_memory=True,
            enable_inference=False,  # Sin LLM en test
            enable_semantic=False
        )
        
        # Procesar query
        result = orch.process(
            query="Hola mundo",
            user_id="test_user"
        )
        
        assert result is not None
        assert 'routing_type' in result
        assert 'processing_time' in result
        assert 'conversation_id' in result
        
        logger.info(f"   ✅ Pipeline completo funcionó")
        logger.info(f"      Ruta: {result['routing_type']}")
        logger.info(f"      Tiempo: {result['processing_time']:.2f}s")


# ========== Ejecución Manual ==========

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 SPRINT 1 INTEGRATION TEST")
    print("="*70 + "\n")
    
    test = TestSprint1Integration()
    
    # Ejecutar tests en orden
    tests_to_run = [
        ("FASE 1: Inferencia", test.test_imports_phase1_inference),
        ("FASE 2: Memoria", test.test_imports_phase2_memory),
        ("FASE 3: Orquestador", test.test_imports_phase3_orchestrator),
        ("Conversation Store", test.test_conversation_store_basic),
        ("Project Store", test.test_project_store_basic),
        ("Semantic Index", test.test_semantic_index_stub),
        ("Query Router", test.test_query_router),
        ("Query Planner", test.test_query_planner),
        ("Response Synthesizer", test.test_response_synthesizer),
        ("Orchestrator Init", test.test_orchestrator_initialization),
        ("Full Pipeline", test.test_full_pipeline_without_inference),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests_to_run:
        try:
            print(f"\n{'─'*70}")
            test_func()
            passed += 1
            print(f"✅ {name} PASÓ")
        except Exception as e:
            failed += 1
            print(f"\n❌ {name} FALLÓ: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print(f"📊 RESULTADOS: {passed} pasados, {failed} fallidos")
    print("="*70 + "\n")
    
    if failed == 0:
        print("🎉 ¡SPRINT 1 COMPLETADO EXITOSAMENTE!")
        print("✅ Listo para pasar a SPRINT 2")
    else:
        print(f"⚠️ Arreglar {failed} test(s) antes de continuar")
    
    sys.exit(0 if failed == 0 else 1)
