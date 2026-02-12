"""
GPU Optimization Guide for RTX 3060 + GTX 1660 Super
Estrategias de optimización específicas para tu hardware
"""

# ============================================================================
# RTX 3060 (12GB VRAM) - OPTIMIZACIONES
# ============================================================================

RTX_3060_SPECS = {
    "name": "NVIDIA RTX 3060",
    "vram": "12GB",
    "cuda_cores": 3660,
    "boost_clock": "2.5 GHz",
    "memory_bandwidth": "360 GB/s",
    "fp32_performance": "13.1 TFLOPS",
    "tensor_performance": "52.4 TFLOPS (with sparsity)",
}

RTX_3060_OPTIMIZATIONS = {
    "memory": {
        "strategy": "4-bit quantization",
        "max_model_size": "13B parameters",
        "batch_size": 8,
        "gradient_accumulation": 4,
        "flash_attention": True,  # Para transformers
        "xformers": True,  # Memory efficient attention
    },
    
    "inference": {
        "models": [
            "mistral-7b-instruct",
            "neural-chat-7b",
            "llama2-7b-chat",
            "openchat-3.5-0106",
        ],
        "inference_framework": "ollama or llama.cpp",
        "batch_inference": True,
        "tensor_parallel": False,  # No needed with 12GB
    },
    
    "embeddings": {
        "models": [
            "sentence-transformers/all-MiniLM-L12-v2",
            "sentence-transformers/all-mpnet-base-v2",
        ],
        "batch_size": 32,
        "pool_size": "mean",
    },
    
    "pytorch_settings": {
        "CUDA_LAUNCH_BLOCKING": False,  # Async launches
        "CUDA_DEVICE_ORDER": "PCI_BUS_ID",
        "CUDA_VISIBLE_DEVICES": "0",
        "CUBLAS_WORKSPACE_CONFIG": ":16:8",  # For some ops
        "TORCH_CUDA_MEMORY_FRACTION": 0.9,
    },
    
    "performance_tuning": {
        "cudnn_benchmark": True,  # Auto-tune kernels
        "deterministic": False,  # Allow non-deterministic for speed
        "num_workers": 4,  # DataLoader workers
        "pin_memory": True,  # For faster transfer
    }
}

# ============================================================================
# GTX 1660 SUPER (6GB VRAM) - OPTIMIZACIONES
# ============================================================================

GTX_1660_SUPER_SPECS = {
    "name": "NVIDIA GeForce GTX 1660 SUPER",
    "vram": "6GB",
    "cuda_cores": 1408,
    "boost_clock": "1.8 GHz",
    "memory_bandwidth": "336 GB/s",
    "fp32_performance": "5.1 TFLOPS",
    "tensor_performance": "5.1 TFLOPS (no tensor cores)",
}

GTX_1660_SUPER_OPTIMIZATIONS = {
    "memory": {
        "strategy": "8-bit quantization",
        "max_model_size": "3.3B parameters",
        "batch_size": 4,
        "gradient_accumulation": 2,
        "flash_attention": False,  # Too memory hungry
        "xformers": True,  # Still helps
        "memory_optimization": "eager (not autograd)",
    },
    
    "inference": {
        "models": [
            "mistral-7b (8-bit only)",
            "phi-2-3.8b",
            "stablelm-3b",
            "orca-mini-3b",
        ],
        "inference_framework": "ollama (gguf quantized)",
        "batch_inference": False,  # One at a time
        "tensor_parallel": False,
    },
    
    "embeddings": {
        "models": [
            "sentence-transformers/all-MiniLM-L6-v2",  # Lightweight
            "sentence-transformers/paraphrase-MiniLM-L6-v2",
        ],
        "batch_size": 8,  # Smaller batches
        "pool_size": "mean",
    },
    
    "pytorch_settings": {
        "CUDA_LAUNCH_BLOCKING": True,  # Sync launches for stability
        "CUDA_DEVICE_ORDER": "PCI_BUS_ID",
        "CUDA_VISIBLE_DEVICES": "0",
        "TORCH_CUDA_MEMORY_FRACTION": 0.95,
    },
    
    "performance_tuning": {
        "cudnn_benchmark": True,
        "deterministic": True,  # Stability over speed
        "num_workers": 2,  # Fewer workers (less VRAM)
        "pin_memory": True,
    }
}

# ============================================================================
# DISTRIBUTED STRATEGY
# ============================================================================

DISTRIBUTED_STRATEGY = {
    "coordinator": "PC1",  # RTX 3060
    "worker": "PC2",       # GTX 1660 Super
    
    "task_assignment": {
        "large_inference": "PC1",      # 7-13B models
        "small_inference": "PC2",      # 3-5B models
        "embeddings": "PC2",           # Fast, small VRAM
        "memory_operations": "PC1",    # If persistence needed
    },
    
    "network": {
        "protocol": "HTTP/REST",
        "serialization": "JSON",
        "timeout": 30,  # seconds
        "max_retries": 3,
    },
    
    "scaling": {
        "max_concurrent_requests": 4,  # Total across both PCs
        "queue_size": 100,
        "batch_timeout": 5,  # seconds
    }
}

# ============================================================================
# SETUP CODE FOR OPTIMIZATION
# ============================================================================

import os
import torch

def setup_pc1_optimization():
    """Apply RTX 3060 optimizations"""
    
    settings = RTX_3060_OPTIMIZATIONS["pytorch_settings"]
    for key, value in settings.items():
        os.environ[key] = str(value)
    
    # Enable optimizations
    torch.backends.cudnn.benchmark = RTX_3060_OPTIMIZATIONS["performance_tuning"]["cudnn_benchmark"]
    torch.backends.cudnn.deterministic = RTX_3060_OPTIMIZATIONS["performance_tuning"]["deterministic"]
    
    print("✅ RTX 3060 optimizations applied")


def setup_pc2_optimization():
    """Apply GTX 1660 Super optimizations"""
    
    settings = GTX_1660_SUPER_OPTIMIZATIONS["pytorch_settings"]
    for key, value in settings.items():
        os.environ[key] = str(value)
    
    # Enable optimizations
    torch.backends.cudnn.benchmark = GTX_1660_SUPER_OPTIMIZATIONS["performance_tuning"]["cudnn_benchmark"]
    torch.backends.cudnn.deterministic = GTX_1660_SUPER_OPTIMIZATIONS["performance_tuning"]["deterministic"]
    
    print("✅ GTX 1660 Super optimizations applied")


def get_model_for_gpu(gpu_type: str):
    """Get recommended model size for GPU"""
    
    if gpu_type == "RTX_3060":
        return {
            "inference": "mistral-7b-instruct",
            "embedding": "all-MiniLM-L12-v2",
            "max_tokens": 2048,
        }
    elif gpu_type == "GTX_1660_SUPER":
        return {
            "inference": "phi-2-3.8b",
            "embedding": "all-MiniLM-L6-v2",
            "max_tokens": 512,
        }


# ============================================================================
# PERFORMANCE ESTIMATION
# ============================================================================

PERFORMANCE_ESTIMATES = {
    "RTX_3060": {
        "inference_7b": {
            "tokens_per_second": 25,  # 4-bit quantized
            "latency_ms": 50,  # First token
            "batch_size": 8,
        },
        "embeddings": {
            "vectors_per_second": 2000,
            "batch_size": 32,
        }
    },
    
    "GTX_1660_SUPER": {
        "inference_3b": {
            "tokens_per_second": 10,  # 8-bit quantized
            "latency_ms": 100,  # First token
            "batch_size": 4,
        },
        "embeddings": {
            "vectors_per_second": 800,
            "batch_size": 8,
        }
    }
}

# ============================================================================
# QUICK REFERENCE
# ============================================================================

OPTIMIZATION_CHECKLIST = {
    "PC1_BEFORE_START": [
        "Set CUDA_DEVICE_ORDER=PCI_BUS_ID",
        "Set CUDA_VISIBLE_DEVICES=0",
        "Disable CUDA_LAUNCH_BLOCKING for performance",
        "Enable torch.backends.cudnn.benchmark",
        "Set TORCH_CUDA_MEMORY_FRACTION=0.9",
        "Consider disabling determinism for speed",
    ],
    
    "PC2_BEFORE_START": [
        "Set CUDA_DEVICE_ORDER=PCI_BUS_ID",
        "Set CUDA_VISIBLE_DEVICES=0",
        "Enable CUDA_LAUNCH_BLOCKING for stability",
        "Enable torch.backends.cudnn.benchmark",
        "Set TORCH_CUDA_MEMORY_FRACTION=0.95",
        "Enable determinism for reliability",
    ],
    
    "BOTH_PCS": [
        "Monitor with nvidia-smi -l 1",
        "Check memory: nvidia-smi --query-gpu=memory.used,memory.free --format=csv",
        "Monitor temperature: nvidia-smi --query-gpu=temperature.gpu --format=csv",
        "Log metrics to track performance",
    ]
}

if __name__ == "__main__":
    print("RTX 3060 Specifications:")
    for key, value in RTX_3060_SPECS.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*70 + "\n")
    
    print("GTX 1660 Super Specifications:")
    for key, value in GTX_1660_SUPER_SPECS.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*70 + "\n")
    
    print("Distributed Strategy:")
    for key, value in DISTRIBUTED_STRATEGY.items():
        print(f"  {key}: {value}")
