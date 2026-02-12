"""
TARS Distributed System
Multi-GPU support for RTX 3060 (PC1) + GTX 1660 Super (PC2)

This module provides:
- GPU detection and configuration
- RPC communication between PCs
- Distributed inference and embeddings
- Load distribution based on VRAM
"""

from .gpu_config import (
    GPUDetector,
    GPUType,
    GPUInfo,
    SystemConfig,
    DistributedConfig,
    ModelDistribution
)

from .rpc_communicator import (
    RPCClient,
    RPCServer,
    RPCRequest,
    RPCResponse,
    RPCMethod,
    DistributedCoordinator
)

from .api_distributed import (
    DistributedApp,
    create_app,
    HealthResponse,
    InferenceRequest,
    EmbeddingRequest,
    BatchEmbeddingRequest,
    StatusResponse
)

__all__ = [
    # GPU Config
    "GPUDetector",
    "GPUType",
    "GPUInfo",
    "SystemConfig",
    "DistributedConfig",
    "ModelDistribution",
    # RPC
    "RPCClient",
    "RPCServer",
    "RPCRequest",
    "RPCResponse",
    "RPCMethod",
    "DistributedCoordinator",
    # API
    "DistributedApp",
    "create_app",
    "HealthResponse",
    "InferenceRequest",
    "EmbeddingRequest",
    "BatchEmbeddingRequest",
    "StatusResponse",
]

__version__ = "1.0.0"
__author__ = "TARS Team"
__description__ = "Distributed AI System for Multi-GPU Setup"
