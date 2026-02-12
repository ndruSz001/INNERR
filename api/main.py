"""
FastAPI REST API - Punto de entrada HTTP para TARS

Endpoints:
  GET  /health                  - Health status
  POST /chat/query              - Procesar query
  GET  /chat/conversations      - Listar conversaciones
  GET  /memory/projects         - Listar proyectos
  POST /memory/project          - Crear proyecto
  GET  /memory/project/{id}     - Obtener proyecto
  
WebSocket:
  WS /ws/chat                   - Real-time chat connection
"""

from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from datetime import datetime
import asyncio
import json
import uuid
import sys
sys.path.insert(0, '/home/ndrz02/keys_1')

from websocket.websocket_handler import WebSocketHandler, WebSocketMessage, MessageType

logger = logging.getLogger(__name__)


# ========== Pydantic Models ==========

class ChatRequest(BaseModel):
    """Solicitud de chat"""
    query: str
    user_id: str = "default_user"
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Respuesta de chat"""
    response: str
    routing_type: str
    processing_time: float
    conversation_id: str
    query_id: str


class HealthResponse(BaseModel):
    """Respuesta de health check"""
    overall_healthy: bool
    uptime_seconds: float
    components: Dict[str, Any]
    timestamp: str


class ProjectData(BaseModel):
    """Datos de proyecto"""
    name: str
    summary: str
    keywords: List[str] = []
    tags: List[str] = []


class ProjectResponse(BaseModel):
    """Respuesta de proyecto"""
    project_id: str
    name: str
    summary: str
    keywords: List[str]
    tags: List[str]


# ========== Factory de FastAPI app ==========

def create_app(
    orchestrator=None,
    conversation_store=None,
    project_store=None,
    health_checker=None,
    embedding_engine=None,
    vector_index=None
) -> FastAPI:
    """
    Crear app FastAPI configurada
    
    Args:
        orchestrator: Instancia de Orchestrator
        conversation_store: Instancia de ConversationStore
        project_store: Instancia de ProjectStore
        health_checker: Instancia de HealthChecker
        embedding_engine: Instancia de EmbeddingEngine
        vector_index: Instancia de VectorIndex
        
    Returns:
        FastAPI app lista para uvicorn
    """
    
    app = FastAPI(
        title="TARS API",
        description="Distributed AI System API",
        version="1.0.0"
    )

    # Add CORS middleware for frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize WebSocket handler
    ws_handler = WebSocketHandler(orchestrator=orchestrator)
    
    # ========== HEALTH CHECK ==========
    
    @app.get("/health", response_model=HealthResponse)
    async def get_health() -> HealthResponse:
        """Health check endpoint"""
        if not health_checker:
            return HealthResponse(
                overall_healthy=True,
                uptime_seconds=0,
                components={},
                timestamp=datetime.now().isoformat()
            )
        
        result = health_checker.check_all(
            orchestrator=orchestrator,
            conversation_store=conversation_store,
            project_store=project_store,
            vector_index=vector_index,
            embedding_engine=embedding_engine
        )
        
        return HealthResponse(**result)
    
    # ========== CHAT ENDPOINTS ==========
    
    @app.post("/chat/query", response_model=ChatResponse)
    async def chat_query(request: ChatRequest) -> ChatResponse:
        """Procesar query de usuario"""
        if not orchestrator:
            raise HTTPException(status_code=503, detail="Orchestrator no disponible")
        
        try:
            result = orchestrator.process(
                query=request.query,
                user_id=request.user_id,
                conversation_id=request.conversation_id
            )
            
            return ChatResponse(**result)
        
        except Exception as e:
            logger.error(f"❌ Error procesando query: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/chat/conversations")
    async def get_conversations(
        user_id: str = Query("default_user"),
        limit: int = Query(10, le=50)
    ) -> List[Dict[str, Any]]:
        """Listar conversaciones del usuario"""
        if not conversation_store:
            return []
        
        try:
            convs = conversation_store.list_conversations(user_id, limit=limit)
            return convs
        except Exception as e:
            logger.error(f"❌ Error listando conversaciones: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/chat/conversation/{conversation_id}")
    async def get_conversation(conversation_id: str) -> Dict[str, Any]:
        """Obtener conversación específica"""
        if not conversation_store:
            raise HTTPException(status_code=404)
        
        conv = conversation_store.get_conversation(conversation_id)
        if not conv:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")
        
        return conv
    
    # ========== MEMORY ENDPOINTS ==========
    
    @app.get("/memory/projects")
    async def get_projects(
        keywords: Optional[List[str]] = Query(None),
        tags: Optional[List[str]] = Query(None),
        limit: int = Query(10, le=100)
    ) -> List[Dict[str, Any]]:
        """Buscar proyectos"""
        if not project_store:
            return []
        
        try:
            projects = project_store.search_projects(
                keywords=keywords,
                tags=tags,
                limit=limit
            )
            return projects
        except Exception as e:
            logger.error(f"❌ Error buscando proyectos: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/memory/project/{project_id}")
    async def get_project(project_id: str) -> Dict[str, Any]:
        """Obtener proyecto específico"""
        if not project_store:
            raise HTTPException(status_code=404)
        
        project = project_store.get_project_summary(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        
        return project
    
    @app.post("/memory/project", response_model=ProjectResponse)
    async def create_project(data: ProjectData) -> ProjectResponse:
        """Crear nuevo proyecto"""
        if not project_store:
            raise HTTPException(status_code=503, detail="Project store no disponible")
        
        try:
            project_id = project_store.create_project_summary(
                name=data.name,
                summary=data.summary,
                keywords=data.keywords,
                tags=data.tags
            )
            
            project = project_store.get_project_summary(project_id)
            
            return ProjectResponse(**project)
        
        except Exception as e:
            logger.error(f"❌ Error creando proyecto: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ========== INFO ENDPOINTS ==========
    
    @app.get("/info/status")
    async def get_status() -> Dict[str, Any]:
        """Obtener estado general del sistema"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'orchestrator': bool(orchestrator),
            'conversation_store': bool(conversation_store),
            'project_store': bool(project_store),
            'vector_index': bool(vector_index),
            'embedding_engine': bool(embedding_engine)
        }
        
        if conversation_store:
            status['conversation_stats'] = conversation_store.get_stats()
        
        if project_store:
            status['project_stats'] = project_store.get_stats()
        
        if vector_index:
            status['vector_index_stats'] = vector_index.get_stats()
        
        if embedding_engine:
            status['embedding_stats'] = embedding_engine.get_stats()
        
        return status
    
    return app


# ========== Funciones de utilidad ==========

# ========== WEBSOCKET ENDPOINT ==========
    
    @app.websocket("/ws/chat")
    async def websocket_endpoint(websocket: WebSocket):
        """
        WebSocket endpoint for real-time chat.
        
        Handles:
        - Connection establishment
        - Message streaming
        - Error recovery
        """
        client_id = str(uuid.uuid4())
        await websocket.accept()
        
        try:
            await ws_handler.handle_connection(websocket, client_id)
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: {client_id}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            try:
                await websocket.close(code=1011, reason=str(e))
            except:
                pass

    # ========== WEBSOCKET STATUS ==========
    
    @app.get("/ws/status")
    async def websocket_status():
        """Get WebSocket connection status"""
        return ws_handler.get_connection_status()

async def start_server(
    app: FastAPI,
    host: str = "0.0.0.0",
    port: int = 8000,
    log_level: str = "info"
) -> None:
    """
    Iniciar servidor FastAPI
    
    Args:
        app: FastAPI app
        host: Host a escuchar
        port: Puerto
        log_level: Nivel de logging
        
    Uso:
        app = create_app(...)
        await start_server(app)
    """
    import uvicorn
    
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level=log_level
    )
    
    server = uvicorn.Server(config)
    logger.info(f"🚀 API iniciada: http://{host}:{port}")
    logger.info(f"📚 Docs: http://{host}:{port}/docs")
    logger.info(f"🔌 WebSocket: ws://{host}:{port}/ws/chat")
    
    await server.serve()
