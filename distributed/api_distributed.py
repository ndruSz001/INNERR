"""
Distributed FastAPI Backend - Integrado con RPC
Funciona como PC1 (Coordinador) o PC2 (Worker)
"""

from fastapi import FastAPI, HTTPException, WebSocket, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import json
import os
import logging
from datetime import datetime

from distributed.gpu_config import DistributedConfig, GPUDetector, ModelDistribution
from distributed.rpc_communicator import (
    RPCServer, DistributedCoordinator, RPCMethod, RPCResponse
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tars_distributed")

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    pc_name: str
    total_vram_gb: float
    gpu_count: int
    is_coordinator: bool

class InferenceRequest(BaseModel):
    prompt: str
    max_tokens: int = 512
    temperature: float = 0.7
    gpu_index: int = 0

class EmbeddingRequest(BaseModel):
    text: str
    gpu_index: int = 0

class BatchEmbeddingRequest(BaseModel):
    texts: List[str]
    gpu_index: int = 0

class StatusResponse(BaseModel):
    pc_name: str
    host: str
    port: int
    is_coordinator: bool
    gpu_info: Dict[str, Any]
    uptime_seconds: float

# ============================================================================
# DISTRIBUTED FASTAPI APPLICATION
# ============================================================================

class DistributedApp:
    """Main distributed application"""
    
    def __init__(self, 
                 pc_name: str = "PC1",
                 host: str = "0.0.0.0",
                 port: int = 8000,
                 remote_host: Optional[str] = None,
                 remote_port: Optional[int] = None):
        
        self.pc_name = pc_name
        self.host = host
        self.port = port
        self.start_time = datetime.now()
        
        # Initialize FastAPI
        self.app = FastAPI(
            title=f"TARS Distributed - {pc_name}",
            description="Distributed AI system with multi-GPU support",
            version="1.0.0"
        )
        
        # Setup CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Initialize distributed coordinator
        self.coordinator = DistributedCoordinator(
            pc_name=pc_name,
            host=host,
            port=port,
            remote_host=remote_host,
            remote_port=remote_port
        )
        
        # GPU configuration
        self.config = DistributedConfig(pc_name, host, port)
        self.gpus = GPUDetector.detect_gpus()
        self.system_config = self.config.generate_config(
            coordinator_host=remote_host or "localhost",
            coordinator_port=remote_port or 8000
        )
        
        logger.info(f"✅ Initialized {pc_name} on {host}:{port}")
        logger.info(f"   Total VRAM: {self.system_config.total_vram_gb:.1f}GB")
        logger.info(f"   GPUs: {len(self.gpus)}")
        
        # Setup routes
        self._setup_routes()
        self._setup_rpc_handlers()
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.on_event("startup")
        async def startup_event():
            await self.coordinator.initialize()
            logger.info(f"🚀 {self.pc_name} is ONLINE")
        
        @self.app.on_event("shutdown")
        async def shutdown_event():
            await self.coordinator.close()
            logger.info(f"🛑 {self.pc_name} is OFFLINE")
        
        # Health check
        @self.app.get("/health", response_model=HealthResponse)
        async def health():
            """
            Health check endpoint for distributed node.
            Returns status, timestamp, PC name, VRAM, GPU count, and coordinator flag.
            """
            return HealthResponse(
                status="ok",
                timestamp=datetime.now(),
                pc_name=self.pc_name,
                total_vram_gb=self.system_config.total_vram_gb,
                gpu_count=len(self.gpus),
                is_coordinator=self.system_config.is_coordinator
            )
        
        # Status endpoint
        @self.app.get("/status", response_model=StatusResponse)
        async def status():
            """
            Returns detailed status of the node, including GPU info and uptime.
            """
            uptime = (datetime.now() - self.start_time).total_seconds()
            gpu_info = {}
            for gpu in self.gpus:
                gpu_info[f"gpu_{gpu.index}"] = {
                    "name": gpu.name,
                    "type": gpu.gpu_type.value,
                    "vram_total_gb": gpu.vram_total_gb,
                    "vram_free_gb": gpu.vram_free_gb,
                    "cuda_cores": gpu.cuda_cores
                }
            return StatusResponse(
                pc_name=self.pc_name,
                host=self.host,
                port=self.port,
                is_coordinator=self.system_config.is_coordinator,
                gpu_info=gpu_info,
                uptime_seconds=uptime
            )
        
        # Inference endpoint
        @self.app.post("/inference")
        async def inference(request: InferenceRequest):
            """Run inference on this PC or forward to remote"""
            
            # Optimización: PC2 procesa embeddings y modelos pequeños localmente,
            # reenvía solo inferencias de modelos grandes a PC1.
            LARGE_MODELS = ["mistral-7b", "llama-13b", "llama-2-13b", "falcon-7b", "falcon-40b"]
            model = getattr(request, "model", None)
            # Si PC2 y el modelo es grande, reenviar a PC1
            if not self.system_config.is_coordinator and (model in LARGE_MODELS or request.gpu_index != 0):
                try:
                    logger.info(f"PC2: Reenviando inferencia de modelo grande '{model}' a PC1...")
                    response = await self.coordinator.call_remote(
                        RPCMethod.INFERENCE_QUERY.value,
                        **request.dict()
                    )
                    if response.error:
                        raise HTTPException(status_code=500, detail=response.error)
                    return response.result
                except Exception as e:
                    logger.error(f"Remote inference failed: {e}")
                    raise HTTPException(status_code=500, detail=str(e))
            else:
                # Local inference (embeddings y modelos pequeños)
                try:
                    logger.info(f"{self.pc_name}: Procesando inferencia localmente (modelo: {model})")
                    result = await self._local_inference(request)
                    return result
                except Exception as e:
                    logger.error(f"Inference error: {e}")
                    raise HTTPException(status_code=500, detail=str(e))
        
        # Embedding endpoint
        @self.app.post("/embed")
        async def embed(request: EmbeddingRequest):
            """Generate embedding"""
            
            try:
                result = await self._local_embed(request)
                return result
            except Exception as e:
                logger.error(f"Embedding error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Batch embedding endpoint
        @self.app.post("/embed-batch")
        async def embed_batch(request: BatchEmbeddingRequest):
            """Generate batch embeddings"""
            
            try:
                result = await self._local_embed_batch(request)
                return result
            except Exception as e:
                logger.error(f"Batch embedding error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Remote status check (for coordinator check)
        @self.app.get("/remote-status")
        async def remote_status():
            """Check status of remote PC"""
            
            if self.system_config.is_coordinator:
                return {"error": "This is the coordinator, no remote to check"}
            
            status = await self.coordinator.get_remote_status()
            return status
        
        # Model info
        @self.app.get("/models")
        async def get_models():
            """Get list of available models on this PC"""
            
            distribution = ModelDistribution.recommend_distribution(self.gpus)
            
            return {
                "pc_name": self.pc_name,
                "models": distribution,
                "gpu_info": [gpu.to_dict() for gpu in self.gpus]
            }
        
        # Configuration
        @self.app.get("/config")
        async def get_config():
            """Get system configuration"""
            return self.system_config.to_dict()
    
    def _setup_rpc_handlers(self):
        """Setup RPC handlers"""
        
        # Inference handler
        async def handle_inference(**kwargs):
            request = InferenceRequest(**kwargs)
            return await self._local_inference(request)
        
        # Embedding handler
        async def handle_embed(**kwargs):
            request = EmbeddingRequest(**kwargs)
            return await self._local_embed(request)
        
        # Register handlers
        self.coordinator.server.register_handler(
            RPCMethod.INFERENCE_QUERY.value,
            handle_inference
        )
        self.coordinator.server.register_handler(
            RPCMethod.EMBED_TEXT.value,
            handle_embed
        )
        self.coordinator.server.register_handler(
            RPCMethod.HEALTH_CHECK.value,
            lambda: {"status": "ok", "pc_name": self.pc_name}
        )
    
    async def _local_inference(self, request: InferenceRequest) -> Dict[str, Any]:
        """Local inference implementation"""
        
        # For now, mock response
        # In production, integrate with actual LLM engine
        
        return {
            "prompt": request.prompt,
            "response": f"[MOCK] Response from {self.pc_name}",
            "tokens_generated": request.max_tokens,
            "gpu_used": request.gpu_index,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _local_embed(self, request: EmbeddingRequest) -> Dict[str, Any]:
        """Local embedding implementation"""
        
        # For now, mock response
        # In production, integrate with sentence-transformers
        
        return {
            "text": request.text,
            "embedding": [0.1] * 384,  # Mock 384-dim embedding
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "gpu_used": request.gpu_index,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _local_embed_batch(self, request: BatchEmbeddingRequest) -> Dict[str, Any]:
        """Local batch embedding implementation"""
        
        return {
            "texts": request.texts,
            "embeddings": [[0.1] * 384 for _ in request.texts],
            "count": len(request.texts),
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "gpu_used": request.gpu_index,
            "timestamp": datetime.now().isoformat()
        }
    
    def setup_rpc_routes(self):
        """Setup RPC endpoint in FastAPI"""
        self.coordinator.server.setup_fastapi_routes(self.app)
    
    def get_app(self) -> FastAPI:
        """Get FastAPI app"""
        self.setup_rpc_routes()
        return self.app


# ============================================================================
# MAIN APPLICATION FACTORY
# ============================================================================

def create_app(
    pc_name: str = "PC1",
    host: str = "0.0.0.0",
    port: int = 8000,
    remote_host: Optional[str] = None,
    remote_port: Optional[int] = None
) -> FastAPI:
    """Create and return FastAPI application"""
    
    distributed_app = DistributedApp(
        pc_name=pc_name,
        host=host,
        port=port,
        remote_host=remote_host,
        remote_port=remote_port
    )
    
    return distributed_app.get_app()


# ============================================================================
# CLI ENTRYPOINT
# ============================================================================

if __name__ == "__main__":
    import argparse
    import uvicorn
    
    parser = argparse.ArgumentParser(description="TARS Distributed Backend")
    parser.add_argument("--pc-name", default="PC1", help="PC name (PC1 or PC2)")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    parser.add_argument("--remote-host", default=None, help="Remote PC host (for workers)")
    parser.add_argument("--remote-port", type=int, default=None, help="Remote PC port")
    parser.add_argument("--reload", action="store_true", help="Enable hot reload")
    
    args = parser.parse_args()
    
    app = create_app(
        pc_name=args.pc_name,
        host=args.host,
        port=args.port,
        remote_host=args.remote_host,
        remote_port=args.remote_port
    )
    
    print(f"\n{'='*70}")
    print(f"🚀 Starting TARS Distributed - {args.pc_name}")
    print(f"{'='*70}")
    print(f"Host: {args.host}:{args.port}")
    if args.remote_host:
        print(f"Remote: {args.remote_host}:{args.remote_port}")
    print(f"{'='*70}\n")
    
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )
