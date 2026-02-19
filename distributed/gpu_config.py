"""
GPU Detection and Configuration for Distributed System
Optimizes for dual-GPU setup: RTX 3060 (PC1) vs GTX 1660 Super (PC2)

RTX 3060: 12GB VRAM - Large models, primary inference
GTX 1660 Super: 6GB VRAM - Smaller models, embeddings, light inference
"""

import os
import sys
import torch
import psutil
import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from enum import Enum


class GPUType(Enum):
    """GPU Types in system"""
    RTX_3060 = "RTX 3060"          # 12GB, 3660 CUDA cores
    GTX_1660_SUPER = "GTX 1660 Super"  # 6GB, 1408 CUDA cores
    UNKNOWN = "Unknown"


@dataclass
class GPUInfo:
    """GPU Information"""
    index: int
    name: str
    gpu_type: GPUType
    vram_total_gb: float
    vram_free_gb: float
    cuda_cores: int
    compute_capability: Tuple[int, int]
    device_id: str
    
    def to_dict(self):
        return {
            **asdict(self),
            "gpu_type": self.gpu_type.value,
            "compute_capability": f"{self.compute_capability[0]}.{self.compute_capability[1]}"
        }


@dataclass
class SystemConfig:
    """Complete system configuration for distributed setup"""
    pc_name: str                    # "PC1" or "PC2"
    host: str                       # IP address or hostname
    port: int                       # Service port
    gpus: List[GPUInfo]            # Available GPUs
    total_vram_gb: float           # Total VRAM across all GPUs
    cpu_cores: int                 # CPU cores available
    ram_gb: float                  # System RAM
    primary_gpu_index: int         # Main GPU for inference
    is_coordinator: bool           # If PC1
    coordinator_host: str          # PC1 address (for PC2)
    coordinator_port: int          # PC1 port (for PC2)
    
    def to_dict(self):
        return {
            "pc_name": self.pc_name,
            "host": self.host,
            "port": self.port,
            "gpus": [gpu.to_dict() for gpu in self.gpus],
            "total_vram_gb": self.total_vram_gb,
            "cpu_cores": self.cpu_cores,
            "ram_gb": self.ram_gb,
            "primary_gpu_index": self.primary_gpu_index,
            "is_coordinator": self.is_coordinator,
            "coordinator_host": self.coordinator_host,
            "coordinator_port": self.coordinator_port
        }


class GPUDetector:
    """Detect and identify GPUs in system"""
    
    GPU_SPECS = {
        # RTX Series (3000s)
        "RTX 3060": GPUType.RTX_3060,
        "RTX 3060 Ti": GPUType.RTX_3060,
        
        # GTX Series (1600s)
        "GTX 1660 Super": GPUType.GTX_1660_SUPER,
        "GTX 1660": GPUType.GTX_1660_SUPER,
        "GTX 1660 Ti": GPUType.GTX_1660_SUPER,
    }
    
    VRAM_SPECS = {
        GPUType.RTX_3060: 12.0,
        GPUType.GTX_1660_SUPER: 6.0,
    }
    
    CUDA_CORES = {
        GPUType.RTX_3060: 3660,
        GPUType.GTX_1660_SUPER: 1408,
    }
    
    COMPUTE_CAP = {
        GPUType.RTX_3060: (8, 6),
        GPUType.GTX_1660_SUPER: (7, 5),
    }
    
    @staticmethod
    def detect_gpus() -> List[GPUInfo]:
        """Detect all CUDA GPUs available"""
        gpus = []
        
        if not torch.cuda.is_available():
            print("⚠️  CUDA not available!")
            return gpus
        
        num_gpus = torch.cuda.device_count()
        print(f"🔍 Detected {num_gpus} GPU(s)")
        
        for i in range(num_gpus):
            try:
                name = torch.cuda.get_device_name(i)
                vram_total = torch.cuda.get_device_properties(i).total_memory / (1024**3)
                vram_free = torch.cuda.mem_get_info(i)[0] / (1024**3)
                
                # Identify GPU type
                gpu_type = GPUType.UNKNOWN
                for key, gtype in GPUDetector.GPU_SPECS.items():
                    if key in name:
                        gpu_type = gtype
                        break
                
                # Get specs if known
                if gpu_type == GPUType.UNKNOWN:
                    cuda_cores = 0
                    compute_cap = (0, 0)
                else:
                    cuda_cores = GPUDetector.CUDA_CORES.get(gpu_type, 0)
                    compute_cap = GPUDetector.COMPUTE_CAP.get(gpu_type, (0, 0))
                
                gpu_info = GPUInfo(
                    index=i,
                    name=name,
                    gpu_type=gpu_type,
                    vram_total_gb=vram_total,
                    vram_free_gb=vram_free,
                    cuda_cores=cuda_cores,
                    compute_capability=compute_cap,
                    device_id=torch.cuda.get_device_name(i)
                )
                gpus.append(gpu_info)
                
                print(f"✅ GPU {i}: {name} ({vram_total:.1f}GB)")
                
            except Exception as e:
                print(f"❌ Error detecting GPU {i}: {e}")
        
        return gpus
    
    @staticmethod
    def get_system_info() -> Dict:
        """Get system information"""
        return {
            "cpu_cores": psutil.cpu_count(logical=False),
            "cpu_cores_logical": psutil.cpu_count(logical=True),
            "ram_gb": psutil.virtual_memory().total / (1024**3),
            "python_version": os.popen(sys.executable + " --version").read().strip(),
            "torch_version": torch.__version__,
            "cuda_version": torch.version.cuda,
        }


class ModelDistribution:
    """Strategy for distributing models across GPUs"""
    
    # Model sizes (GB) - approximate
    MODEL_SIZES = {
        "llama2-7b": 7.0,      # ~7GB (4-bit quantized)
        "llama2-13b": 13.0,    # ~13GB (4-bit quantized)
        "mistral-7b": 7.0,     # ~7GB
        "neural-chat-7b": 7.0, # ~7GB
        "embedding-base": 0.5, # Sentence-transformers base
        "embedding-large": 1.5, # Sentence-transformers large
    }
    
    @staticmethod
    def recommend_distribution(gpus: List[GPUInfo]) -> Dict[str, List[str]]:
        """
        Recommend which models to run on which GPU
        
        Strategy:
        - RTX 3060 (12GB): Large models (7-13B parameters)
        - GTX 1660 Super (6GB): Small models, embeddings, quantized
        """
        distribution = {}
        
        if len(gpus) == 0:
            return {"cpu": list(ModelDistribution.MODEL_SIZES.keys())}
        
        # Sort GPUs by VRAM
        gpus_sorted = sorted(gpus, key=lambda g: g.vram_total_gb, reverse=True)
        
        for gpu in gpus_sorted:
            distribution[f"gpu_{gpu.index}"] = []
            
            if gpu.gpu_type == GPUType.RTX_3060:
                # Large models for 3060
                distribution[f"gpu_{gpu.index}"] = [
                    "llama2-7b",
                    "mistral-7b",
                    "neural-chat-7b",
                ]
            elif gpu.gpu_type == GPUType.GTX_1660_SUPER:
                # Small models + embeddings for 1660 Super
                distribution[f"gpu_{gpu.index}"] = [
                    "embedding-base",
                    "embedding-large",
                    "llama2-7b",  # Quantized
                ]
        
        return distribution
    
    @staticmethod
    def get_quantization_for_gpu(gpu_type: GPUType) -> str:
        """Get recommended quantization level"""
        if gpu_type == GPUType.RTX_3060:
            return "4bit"  # 3060 has 12GB, can handle 4-bit
        elif gpu_type == GPUType.GTX_1660_SUPER:
            return "8bit"  # 1660 needs 8-bit for smaller models
        return "4bit"


class DistributedConfig:
    """Main configuration manager for distributed system"""
    
    def __init__(self, pc_name: str, host: str = "localhost", port: int = 8000):
        self.pc_name = pc_name
        self.host = host
        self.port = port
        self.gpus = GPUDetector.detect_gpus()
        self.system_info = GPUDetector.get_system_info()
        
    def generate_config(self, 
                       coordinator_host: str = "localhost",
                       coordinator_port: int = 8000) -> SystemConfig:
        """Generate complete system configuration"""
        
        is_coordinator = self.pc_name == "PC1"
        
        config = SystemConfig(
            pc_name=self.pc_name,
            host=self.host,
            port=self.port,
            gpus=self.gpus,
            total_vram_gb=sum(gpu.vram_total_gb for gpu in self.gpus),
            cpu_cores=self.system_info["cpu_cores"],
            ram_gb=self.system_info["ram_gb"],
            primary_gpu_index=0 if self.gpus else -1,
            is_coordinator=is_coordinator,
            coordinator_host=coordinator_host,
            coordinator_port=coordinator_port
        )
        
        return config
    
    def save_config(self, output_path: str = "system_config.json"):
        """Save configuration to file"""
        config = self.generate_config()
        
        with open(output_path, "w") as f:
            json.dump(config.to_dict(), f, indent=2)
        
        print(f"✅ Configuration saved to {output_path}")
        return config
    
    def print_summary(self):
        """Print configuration summary"""
        config = self.generate_config()
        
        print("\n" + "="*70)
        print(f"🖥️  SYSTEM CONFIG - {config.pc_name}")
        print("="*70)
        print(f"Host: {config.host}:{config.port}")
        print(f"Coordinator: {config.is_coordinator}")
        print(f"\n💾 SYSTEM:")
        print(f"  CPU Cores: {config.cpu_cores}")
        print(f"  RAM: {config.ram_gb:.1f} GB")
        print(f"\n🎮 GPUS ({len(config.gpus)} total):")
        
        for gpu in config.gpus:
            print(f"\n  GPU {gpu.index}: {gpu.name}")
            print(f"    Type: {gpu.gpu_type.value}")
            print(f"    VRAM: {gpu.vram_total_gb:.1f}GB ({gpu.vram_free_gb:.1f}GB free)")
            print(f"    CUDA Cores: {gpu.cuda_cores:,}")
            print(f"    Compute Capability: {gpu.compute_capability[0]}.{gpu.compute_capability[1]}")
        
        print(f"\n📊 TOTAL VRAM: {config.total_vram_gb:.1f}GB")
        
        # Recommend distribution
        distribution = ModelDistribution.recommend_distribution(config.gpus)
        print(f"\n📦 RECOMMENDED MODEL DISTRIBUTION:")
        for gpu_key, models in distribution.items():
            print(f"  {gpu_key}:")
            for model in models:
                size = ModelDistribution.MODEL_SIZES.get(model, "?")
                print(f"    - {model} ({size}GB)")
        
        print("\n" + "="*70)


if __name__ == "__main__":
    import sys
    
    pc_name = sys.argv[1] if len(sys.argv) > 1 else "PC1"
    host = sys.argv[2] if len(sys.argv) > 2 else "localhost"
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 8000
    
    config = DistributedConfig(pc_name=pc_name, host=host, port=port)
    config.print_summary()
    config.save_config(f"{pc_name.lower()}_config.json")
