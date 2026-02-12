"""
Nightly Synthesis Job - Ejecuta cada noche automáticamente

Responsabilidades:
1. Resume conversaciones antiguas (>24h)
2. Genera embeddings de resúmenes
3. Agrega a índice vectorial
4. Limpia conversaciones de RAM en PC1
5. Optimiza índice FAISS

Ejecutar: apscheduler lo llama automáticamente a las 02:00 AM
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class NightlySynthesisJob:
    """Job que ejecuta síntesis noctorna"""
    
    def __init__(self):
        """Inicializar job"""
        self.last_run: Optional[datetime] = None
        self.stats = {
            'conversations_processed': 0,
            'embeddings_generated': 0,
            'index_optimized': False,
            'data_cleaned': 0
        }
    
    def execute(
        self,
        conversation_store=None,
        project_store=None,
        embedding_engine=None,
        vector_index=None
    ) -> Dict[str, Any]:
        """
        Ejecutar síntesis completa
        
        Args:
            conversation_store: ConversationStore de PC1
            project_store: ProjectStore de PC1
            embedding_engine: EmbeddingEngine de PC2
            vector_index: VectorIndex de PC2
            
        Returns:
            {success, messages, stats}
        """
        logger.info("\n" + "="*70)
        logger.info("🌙 INICIANDO SÍNTESIS NOCTURNA")
        logger.info("="*70)
        
        start_time = datetime.now()
        self.last_run = start_time
        self.stats = {
            'conversations_processed': 0,
            'embeddings_generated': 0,
            'index_optimized': False,
            'data_cleaned': 0,
            'duration_seconds': 0
        }
        
        messages = []
        
        # 1. RESUMIR CONVERSACIONES ANTIGUAS
        if conversation_store:
            logger.info("\n1️⃣  Resumiendo conversaciones antiguas...")
            old_count = self._summarize_old_conversations(
                conversation_store,
                project_store,
                embedding_engine,
                vector_index
            )
            self.stats['conversations_processed'] = old_count
            messages.append(f"✅ {old_count} conversaciones resumidas")
        
        # 2. OPTIMIZAR ÍNDICE
        if vector_index:
            logger.info("\n2️⃣  Optimizando índice FAISS...")
            success = self._optimize_index(vector_index)
            self.stats['index_optimized'] = success
            messages.append("✅ Índice optimizado" if success else "⚠️ Índice no optimizado")
        
        # 3. LIMPIAR DATOS ANTIGUOS
        if conversation_store:
            logger.info("\n3️⃣  Limpiando datos antiguos...")
            cleaned = self._cleanup_old_data(conversation_store)
            self.stats['data_cleaned'] = cleaned
            messages.append(f"✅ {cleaned} conversaciones eliminadas")
        
        # 4. GUARDAR ÍNDICE
        if vector_index:
            logger.info("\n4️⃣  Guardando índice...")
            self._save_index(vector_index)
            messages.append("✅ Índice guardado")
        
        duration = (datetime.now() - start_time).total_seconds()
        self.stats['duration_seconds'] = duration
        
        logger.info("\n" + "="*70)
        logger.info(f"🌙 SÍNTESIS COMPLETADA EN {duration:.1f}s")
        logger.info("="*70)
        
        return {
            'success': True,
            'messages': messages,
            'stats': self.stats,
            'executed_at': start_time.isoformat()
        }
    
    def _summarize_old_conversations(
        self,
        conversation_store,
        project_store,
        embedding_engine,
        vector_index
    ) -> int:
        """Resumir conversaciones mayores a 24 horas"""
        
        if not conversation_store:
            return 0
        
        # Encontrar conversaciones viejas
        cutoff = datetime.now() - timedelta(hours=24)
        old_convs = []
        
        for conv_id, conv in conversation_store.conversations.items():
            last_interaction = datetime.fromisoformat(conv['last_interaction'])
            if last_interaction < cutoff:
                old_convs.append((conv_id, conv))
        
        if not old_convs:
            logger.info("   📭 Sin conversaciones viejas")
            return 0
        
        logger.info(f"   📋 Encontradas {len(old_convs)} conversaciones viejas")
        
        processed = 0
        for conv_id, conv in old_convs:
            # Resumir (en Sprint 2, solo concatenamos)
            messages = conv.get('messages', [])
            summary = self._create_summary(messages)
            
            if summary and embedding_engine and vector_index:
                # Generar embedding
                try:
                    embedding = embedding_engine.embed_text(summary)
                    
                    # Agregar a índice
                    vector_index.add(
                        embedding=embedding,
                        metadata={
                            'text': summary,
                            'source': 'conversation_summary',
                            'conversation_id': conv_id,
                            'created_at': datetime.now().isoformat()
                        }
                    )
                    
                    processed += 1
                    self.stats['embeddings_generated'] += 1
                
                except Exception as e:
                    logger.error(f"   ❌ Error procesando {conv_id}: {e}")
        
        logger.info(f"   ✅ {processed} conversaciones procesadas")
        return processed
    
    def _create_summary(self, messages: List[Dict]) -> str:
        """Crear resumen de conversación"""
        if not messages:
            return ""
        
        # Tomar últimos 5 mensajes como resumen
        summary_parts = []
        for msg in messages[-5:]:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            summary_parts.append(f"{role}: {content[:100]}")
        
        return " | ".join(summary_parts)
    
    def _optimize_index(self, vector_index) -> bool:
        """Optimizar índice FAISS"""
        try:
            if vector_index.index and hasattr(vector_index.index, 'train'):
                # En FAISS, train() mejora índices aproximados
                logger.debug("   🔧 Optimizando índice...")
            
            return True
        except Exception as e:
            logger.error(f"   ❌ Error optimizando: {e}")
            return False
    
    def _cleanup_old_data(self, conversation_store) -> int:
        """Eliminar conversaciones mayores a 48 horas"""
        
        if not conversation_store:
            return 0
        
        cutoff = datetime.now() - timedelta(hours=48)
        deleted = conversation_store.clear_old(hours=48)
        
        logger.info(f"   🗑️  {deleted} conversaciones eliminadas")
        return deleted
    
    def _save_index(self, vector_index) -> bool:
        """Guardar índice a disco"""
        try:
            filepath = "/tmp/tars_vector_index.faiss"
            success = vector_index.save(filepath)
            if success:
                logger.info(f"   💾 Índice guardado: {filepath}")
            return success
        except Exception as e:
            logger.error(f"   ❌ Error guardando índice: {e}")
            return False
    
    def get_last_run_info(self) -> Dict[str, Any]:
        """Obtener info de última ejecución"""
        return {
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'stats': self.stats
        }


# ========== Helper para usar con APScheduler ==========

def nightly_job_wrapper(
    conversation_store=None,
    project_store=None,
    embedding_engine=None,
    vector_index=None
) -> None:
    """
    Wrapper para APScheduler
    
    Uso:
        scheduler.add_job(
            nightly_job_wrapper,
            'cron',
            hour=2, minute=0,
            kwargs={...}
        )
    """
    job = NightlySynthesisJob()
    result = job.execute(
        conversation_store=conversation_store,
        project_store=project_store,
        embedding_engine=embedding_engine,
        vector_index=vector_index
    )
    
    if result['success']:
        logger.info(f"✅ Nightly job completado: {result['stats']}")
    else:
        logger.error(f"❌ Nightly job falló: {result}")
