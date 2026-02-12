"""
Integration Test - Sprint 2 Completo

Valida que todos los módulos de Sprint 2 funcionan correctamente
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_sprint2_phase4():
    """Prueba FASE 4: Procesamiento"""
    logger.info("\n" + "="*70)
    logger.info("🧪 Testing FASE 4: Procesamiento")
    logger.info("="*70)
    
    # Document Ingester
    logger.info("✓ Testing Document Ingester...")
    from processing.ingestion.document_ingester import DocumentIngester
    
    ingester = DocumentIngester()
    result = ingester.ingest(
        "This is a test document with some content.",
        title="Test Doc"
    )
    assert result is not None
    assert len(result.chunks) > 0
    logger.info("  ✅ Document Ingester OK")
    
    # Embedding Engine
    logger.info("✓ Testing Embedding Engine...")
    from processing.embeddings.embedding_engine import EmbeddingEngine
    
    engine = EmbeddingEngine()
    embedding = engine.embed_text("Test text")
    assert embedding.shape == (384,)
    logger.info("  ✅ Embedding Engine OK")
    
    # Vector Index
    logger.info("✓ Testing Vector Index...")
    from processing.indexing.vector_index import VectorIndex
    
    index = VectorIndex()
    vector_id = index.add(embedding, {'text': 'test'})
    assert vector_id >= 0
    
    results = index.search(embedding, top_k=1)
    assert len(results) > 0
    logger.info("  ✅ Vector Index OK")
    
    # Nightly Synthesis Job
    logger.info("✓ Testing Nightly Synthesis Job...")
    from infrastructure.jobs.nightly_synthesis import NightlySynthesisJob
    
    job = NightlySynthesisJob()
    info = job.get_last_run_info()
    assert info is not None
    logger.info("  ✅ Nightly Synthesis Job OK")


def test_sprint2_phase5():
    """Prueba FASE 5: Infrastructure"""
    logger.info("\n" + "="*70)
    logger.info("🧪 Testing FASE 5: Infrastructure")
    logger.info("="*70)
    
    # Health Checker
    logger.info("✓ Testing Health Checker...")
    from infrastructure.monitoring.health_checker import HealthChecker
    
    checker = HealthChecker()
    result = checker.check_all()
    assert 'overall_healthy' in result
    logger.info("  ✅ Health Checker OK")
    
    # Job Scheduler
    logger.info("✓ Testing Job Scheduler...")
    from infrastructure.jobs.scheduler import JobScheduler
    
    scheduler = JobScheduler()
    assert scheduler is not None
    logger.info("  ✅ Job Scheduler OK")
    
    # Logging
    logger.info("✓ Testing Logging...")
    from infrastructure.logging.logger_config import get_logger
    
    test_logger = get_logger(__name__)
    assert test_logger is not None
    test_logger.info("Test logging message")
    logger.info("  ✅ Logging OK")


def test_sprint2_phase6():
    """Prueba FASE 6: API + CLI"""
    logger.info("\n" + "="*70)
    logger.info("🧪 Testing FASE 6: API + CLI")
    logger.info("="*70)
    
    # FastAPI
    logger.info("✓ Testing FastAPI API...")
    from api.main import create_app
    
    app = create_app()
    assert app is not None
    logger.info("  ✅ FastAPI API OK")
    
    # CLI
    logger.info("✓ Testing CLI...")
    from cli.main import TARSCLIApp
    
    cli = TARSCLIApp()
    assert cli is not None
    logger.info("  ✅ CLI OK")


def test_integration_sprint1_sprint2():
    """Prueba integración completa Sprint 1 + Sprint 2"""
    logger.info("\n" + "="*70)
    logger.info("🧪 Testing Integración Sprint 1 + Sprint 2")
    logger.info("="*70)
    
    # Cargar componentes de Sprint 1
    logger.info("✓ Sprint 1 components...")
    from orchestrator.main import Orchestrator
    from core.memory.conversation_store import ConversationStore
    from core.memory.project_store import ProjectStore
    
    # Cargar componentes de Sprint 2
    logger.info("✓ Sprint 2 components...")
    from processing.ingestion.document_ingester import DocumentIngester
    from processing.embeddings.embedding_engine import EmbeddingEngine
    from processing.indexing.vector_index import VectorIndex
    from infrastructure.monitoring.health_checker import HealthChecker
    
    # Crear instancias
    logger.info("✓ Creating instances...")
    orch = Orchestrator(enable_memory=True, enable_inference=False)
    ingester = DocumentIngester()
    embedding_engine = EmbeddingEngine()
    vector_index = VectorIndex()
    health_checker = HealthChecker()
    
    # Workflow completo
    logger.info("✓ Complete workflow...")
    
    # 1. Ingestar documento
    doc = ingester.ingest("Test document content", title="Test")
    assert doc is not None
    logger.info("  ✓ Documento ingestado")
    
    # 2. Generar embeddings
    embedding = embedding_engine.embed_text(doc.text)
    assert embedding.shape == (384,)
    logger.info("  ✓ Embedding generado")
    
    # 3. Agregar a índice
    vector_id = vector_index.add(embedding, {'text': doc.text})
    assert vector_id >= 0
    logger.info("  ✓ Vector agregado a índice")
    
    # 4. Procesar query con orchestrador
    result = orch.process("Test query", "test_user")
    assert result is not None
    assert 'response' in result
    logger.info("  ✓ Query procesada")
    
    # 5. Health check
    health = health_checker.check_all(
        orchestrator=orch,
        conversation_store=orch.conversation_store,
        project_store=orch.project_store,
        vector_index=vector_index,
        embedding_engine=embedding_engine
    )
    assert health is not None
    logger.info("  ✓ Health check ejecutado")


if __name__ == "__main__":
    logger.info("\n" + "🧪 SPRINT 2 INTEGRATION TESTS")
    logger.info("="*70)
    
    try:
        test_sprint2_phase4()
        test_sprint2_phase5()
        test_sprint2_phase6()
        test_integration_sprint1_sprint2()
        
        logger.info("\n" + "="*70)
        logger.info("✅ TODOS LOS TESTS PASARON!")
        logger.info("🎉 SPRINT 2 COMPLETADO EXITOSAMENTE")
        logger.info("="*70 + "\n")
    
    except Exception as e:
        logger.error(f"\n❌ TEST FALLÓ: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
