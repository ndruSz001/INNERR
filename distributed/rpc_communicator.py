"""
Distributed RPC Communication between PC1 (3060) and PC2 (1660 Super)
Lightweight REST API for inter-PC communication without Docker overhead
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import aiohttp
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("distributed_rpc")


class RPCMethod(Enum):
    """RPC methods available in distributed system"""
    # Inference
    INFERENCE_QUERY = "inference.query"
    INFERENCE_STREAM = "inference.stream"
    
    # Embeddings
    EMBED_TEXT = "embeddings.embed"
    EMBED_BATCH = "embeddings.batch"
    
    # Health & Status
    HEALTH_CHECK = "system.health"
    GET_STATUS = "system.status"
    GET_MODELS = "system.models"
    
    # Memory operations
    SAVE_MEMORY = "memory.save"
    RETRIEVE_MEMORY = "memory.retrieve"
    SEARCH_MEMORY = "memory.search"


@dataclass
class RPCRequest:
    """RPC Request structure"""
    id: str
    method: str
    params: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        return {
            "jsonrpc": "2.0",
            "id": self.id,
            "method": self.method,
            "params": self.params,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class RPCResponse:
    """RPC Response structure"""
    id: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "jsonrpc": "2.0",
            "id": self.id,
            "result": self.result,
            "error": self.error,
            "timestamp": self.timestamp.isoformat()
        }


class RPCClient:
    """RPC Client for calling remote services"""
    
    def __init__(self, remote_host: str, remote_port: int, timeout: int = 30):
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.base_url = f"http://{remote_host}:{remote_port}"
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """Initialize async session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        logger.info(f"✅ RPC Client initialized: {self.base_url}")
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()
    
    async def call(self, method: str, params: Dict[str, Any] = None, retries: int = 3, retry_delay: float = 2.0) -> RPCResponse:
        """
        Make RPC call to remote service with automatic retries and robust error handling.
        Args:
            method: RPC method name
            params: Method parameters
            retries: Number of retry attempts
            retry_delay: Delay between retries (seconds)
        Returns:
            RPCResponse with result or error
        """
        if params is None:
            params = {}
        request = RPCRequest(
            id=str(uuid.uuid4()),
            method=method,
            params=params,
            timestamp=datetime.now()
        )
        last_error = None
        for attempt in range(1, retries + 1):
            logger.info(f"RPCClient: Attempt {attempt} - Calling method '{method}' at {self.base_url}/rpc with params: {params}")
            try:
                async with self.session.post(
                    f"{self.base_url}/rpc",
                    json=request.to_dict(),
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    logger.info(f"RPCClient: Response status {resp.status} for method '{method}' (attempt {attempt})")
                    if resp.status == 200:
                        data = await resp.json()
                        logger.info(f"RPCClient: Success - method '{method}' result: {data.get('result')} (attempt {attempt})")
                        return RPCResponse(
                            id=data.get("id"),
                            result=data.get("result"),
                            error=data.get("error"),
                            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat()))
                        )
                    else:
                        last_error = f"HTTP {resp.status}"
                        logger.error(f"RPCClient: HTTP error {resp.status} for method '{method}' (attempt {attempt})")
            except asyncio.TimeoutError:
                last_error = f"Timeout after {self.timeout}s (attempt {attempt})"
                logger.error(f"RPCClient: Timeout for method '{method}' (attempt {attempt})")
            except Exception as e:
                last_error = f"{type(e).__name__}: {e} (attempt {attempt})"
                logger.error(f"RPCClient: Exception {type(e).__name__}: {e} for method '{method}' (attempt {attempt})")
            if attempt < retries:
                logger.warning(f"RPCClient: RPC call failed ({last_error}), retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
        logger.error(f"RPCClient: RPC call failed after {retries} attempts: {last_error}")
        return RPCResponse(
            id=request.id,
            error=f"RPC call failed after {retries} attempts: {last_error}"
        )
    
    async def inference(self, prompt: str, max_tokens: int = 512, 
                       temperature: float = 0.7, gpu_index: int = 0) -> RPCResponse:
        """Call remote inference"""
        return await self.call(
            RPCMethod.INFERENCE_QUERY.value,
            {
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "gpu_index": gpu_index
            }
        )
    
    async def embed_text(self, text: str, gpu_index: int = 0) -> RPCResponse:
        """Call remote embedding"""
        return await self.call(
            RPCMethod.EMBED_TEXT.value,
            {
                "text": text,
                "gpu_index": gpu_index
            }
        )
    
    async def embed_batch(self, texts: List[str], gpu_index: int = 0) -> RPCResponse:
        """Call batch embedding"""
        return await self.call(
            RPCMethod.EMBED_BATCH.value,
            {
                "texts": texts,
                "gpu_index": gpu_index
            }
        )
    
    async def health_check(self) -> RPCResponse:
        """Check remote service health"""
        return await self.call(RPCMethod.HEALTH_CHECK.value)
    
    async def get_status(self) -> RPCResponse:
        """Get remote service status"""
        return await self.call(RPCMethod.GET_STATUS.value)


class RPCServer:
    """RPC Server for handling remote calls"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.handlers: Dict[str, Callable] = {}
        self.app = None
    
    def register_handler(self, method: str, handler: Callable):
        """Register RPC method handler"""
        self.handlers[method] = handler
        logger.info(f"✅ Registered handler: {method}")
    
    async def handle_rpc(self, request_data: Dict[str, Any]) -> RPCResponse:
        """Handle incoming RPC request"""
        try:
            method = request_data.get("method")
            params = request_data.get("params", {})
            request_id = request_data.get("id")
            
            if method not in self.handlers:
                return RPCResponse(
                    id=request_id,
                    error=f"Unknown method: {method}"
                )
            
            handler = self.handlers[method]
            result = await handler(**params) if asyncio.iscoroutinefunction(handler) else handler(**params)
            
            return RPCResponse(
                id=request_id,
                result=result
            )
        
        except Exception as e:
            logger.error(f"❌ RPC Error: {e}")
            return RPCResponse(
                id=request_data.get("id"),
                error=str(e)
            )
    
    def setup_fastapi_routes(self, app):
        """Setup FastAPI routes for RPC"""
        from fastapi import Request
        
        @app.post("/rpc")
        async def rpc_endpoint(request: Request):
            data = await request.json()
            response = await self.handle_rpc(data)
            return response.to_dict()
        
        # Eliminado endpoint duplicado /health para evitar conflicto con api_distributed.py
        
        logger.info(f"✅ FastAPI routes setup at {self.host}:{self.port}")


class DistributedCoordinator:
    """Coordinates between PC1 and PC2"""
    
    def __init__(self, pc_name: str, host: str, port: int,
                 remote_host: Optional[str] = None, remote_port: Optional[int] = None):
        self.pc_name = pc_name
        self.host = host
        self.port = port
        self.is_coordinator = pc_name == "PC1"
        
        self.server = RPCServer(host=host, port=port)
        self.client: Optional[RPCClient] = None
        
        if remote_host and remote_port:
            self.client = RPCClient(remote_host, remote_port)
    
    async def initialize(self):
        """Initialize coordinator"""
        if self.client:
            await self.client.initialize()
        logger.info(f"✅ {self.pc_name} Coordinator initialized")
    
    async def close(self):
        """Close coordinator"""
        if self.client:
            await self.client.close()
    
    def register_service(self, service_name: str, handlers: Dict[str, Callable]):
        """Register service handlers"""
        for method, handler in handlers.items():
            full_method = f"{service_name}.{method}"
            self.server.register_handler(full_method, handler)
    
    async def call_remote(self, method: str, **kwargs) -> RPCResponse:
        """Call method on remote PC"""
        if not self.client:
            raise RuntimeError("No remote client configured")
        
        return await self.client.call(method, kwargs)
    
    async def get_remote_status(self) -> Dict[str, Any]:
        """Get status of remote PC"""
        if not self.client:
            return {"error": "No remote client"}
        
        response = await self.client.get_status()
        return response.to_dict()
    
    async def health_check_remote(self) -> bool:
        """Check if remote PC is healthy"""
        if not self.client:
            return False
        
        async def health_check_remote(self, auto_reconnect: bool = True) -> bool:
            """
            Periodically check health of remote node. If not healthy and auto_reconnect is True, attempt to re-initialize client.
            Returns True if healthy, False otherwise.
            """
            if not self.client:
                if auto_reconnect:
                    logger.warning("DistributedCoordinator: No remote client, attempting reconnection...")
                    await self.initialize()
                return False
            try:
                response = await self.client.health_check()
                if response.error is None:
                    logger.info("DistributedCoordinator: Remote node healthy.")
                    return True
                else:
                    logger.warning(f"DistributedCoordinator: Remote node unhealthy: {response.error}")
                    if auto_reconnect:
                        logger.info("DistributedCoordinator: Attempting reconnection...")
                        await self.initialize()
                    return False
            except Exception as e:
                logger.error(f"DistributedCoordinator: Exception during health check: {e}")
                if auto_reconnect:
                    logger.info("DistributedCoordinator: Attempting reconnection...")
                    await self.initialize()
                return False


if __name__ == "__main__":
    # Test RPC communication
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "client":
        # Test client
        async def test_client():
            client = RPCClient("localhost", 8001)
            await client.initialize()
            
            response = await client.health_check()
            print(f"Health Check: {response.to_dict()}")
            
            await client.close()
        
        asyncio.run(test_client())
    else:
        print("Distributed RPC module loaded successfully")
