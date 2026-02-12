#!/usr/bin/env python3
"""
TARS Distributed - Hardware Detection & Smart Setup
Detecta hardware disponible y optimiza automáticamente
"""

import os
import sys
import json
import subprocess
import platform
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class GPUTier(Enum):
    """GPU Performance Tier"""
    HIGH = "high"          # RTX 3060+, RTX 4080+, A100
    MEDIUM = "medium"      # RTX 3050, GTX 1660 Super
    LOW = "low"           # GTX 1650, GTX 1050
    NONE = "none"         # CPU only

@dataclass
class HardwareProfile:
    """Complete hardware profile"""
    pc_name: str
    os_type: str
    python_version: str
    cpu_cores: int
    cpu_cores_logical: int
    ram_gb: float
    gpu_count: int
    gpu_info: Dict
    gpu_tier: GPUTier
    has_cuda: bool
    cuda_version: str
    total_vram_gb: float
    storage_available_gb: float

@dataclass
class OptimizationProfile:
    """Optimization recommendations"""
    num_workers: int
    batch_size: int
    max_batch_size: int
    memory_fraction: float
    quantization: str
    inference_framework: str
    embedding_model_size: str
    recommended_models: List[str]
    cpu_threads: int
    ffmpeg_required: bool

class HardwareDetector:
    """Detect system hardware and capabilities"""
    
    @staticmethod
    def get_os_type() -> str:
        """Get OS type"""
        system = platform.system()
        if system == "Darwin":
            return f"macOS {platform.mac_ver()[0]}"
        elif system == "Linux":
            try:
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME"):
                            return line.split("=")[1].strip().strip('"')
            except:
                pass
            return "Linux"
        elif system == "Windows":
            return f"Windows {platform.win32_ver()[1]}"
        return "Unknown"
    
    @staticmethod
    def get_cpu_info() -> Tuple[int, int, float]:
        """Get CPU cores, logical cores, and RAM"""
        import psutil
        cpu_physical = psutil.cpu_count(logical=False) or 1
        cpu_logical = psutil.cpu_count(logical=True) or 1
        ram_gb = psutil.virtual_memory().total / (1024**3)
        return cpu_physical, cpu_logical, ram_gb
    
    @staticmethod
    def get_gpu_info() -> Tuple[bool, str, List[Dict], float]:
        """Detect NVIDIA GPUs"""
        try:
            import torch
            has_cuda = torch.cuda.is_available()
            cuda_version = torch.version.cuda if has_cuda else "N/A"
            
            gpu_list = []
            total_vram = 0.0
            
            if has_cuda:
                gpu_count = torch.cuda.device_count()
                for i in range(gpu_count):
                    name = torch.cuda.get_device_name(i)
                    vram = torch.cuda.get_device_properties(i).total_memory / (1024**3)
                    total_vram += vram
                    
                    gpu_list.append({
                        "index": i,
                        "name": name,
                        "vram_gb": vram,
                        "cuda_cores": HardwareDetector._get_cuda_cores(name)
                    })
            
            return has_cuda, str(cuda_version), gpu_list, total_vram
        
        except Exception as e:
            return False, "N/A", [], 0.0
    
    @staticmethod
    def _get_cuda_cores(gpu_name: str) -> int:
        """Get CUDA cores from GPU name"""
        cuda_cores_map = {
            "RTX 3060": 3660,
            "RTX 3050": 2560,
            "RTX 4090": 16384,
            "RTX 4080": 9728,
            "GTX 1660 Super": 1408,
            "GTX 1660": 1152,
            "GTX 1650": 896,
            "A100": 6912,
            "A10": 6144,
        }
        
        for key, cores in cuda_cores_map.items():
            if key in gpu_name:
                return cores
        return 0
    
    @staticmethod
    def get_storage_info() -> float:
        """Get available storage"""
        try:
            import shutil
            stat = shutil.disk_usage("/")
            return stat.free / (1024**3)
        except:
            return 0.0
    
    @staticmethod
    def get_python_version() -> str:
        """Get Python version"""
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    @staticmethod
    def detect_gpu_tier(vram_gb: float, gpu_count: int) -> GPUTier:
        """Determine GPU tier"""
        if gpu_count == 0:
            return GPUTier.NONE
        elif vram_gb >= 10:  # 12GB+, 16GB+, etc
            return GPUTier.HIGH
        elif vram_gb >= 4:   # 6GB, 8GB
            return GPUTier.MEDIUM
        else:                # 2GB-4GB
            return GPUTier.LOW
    
    @staticmethod
    def detect_hardware(pc_name: str = "NewPC") -> HardwareProfile:
        """Complete hardware detection"""
        
        os_type = HardwareDetector.get_os_type()
        python_version = HardwareDetector.get_python_version()
        cpu_cores, cpu_cores_logical, ram_gb = HardwareDetector.get_cpu_info()
        has_cuda, cuda_version, gpu_list, total_vram = HardwareDetector.get_gpu_info()
        storage = HardwareDetector.get_storage_info()
        gpu_tier = HardwareDetector.detect_gpu_tier(total_vram, len(gpu_list))
        
        gpu_info = {
            "count": len(gpu_list),
            "total_vram_gb": total_vram,
            "devices": gpu_list
        }
        
        return HardwareProfile(
            pc_name=pc_name,
            os_type=os_type,
            python_version=python_version,
            cpu_cores=cpu_cores,
            cpu_cores_logical=cpu_cores_logical,
            ram_gb=ram_gb,
            gpu_count=len(gpu_list),
            gpu_info=gpu_info,
            gpu_tier=gpu_tier,
            has_cuda=has_cuda,
            cuda_version=str(cuda_version),
            total_vram_gb=total_vram,
            storage_available_gb=storage
        )


class OptimizationEngine:
    """Generate optimizations based on hardware"""
    
    @staticmethod
    def generate_profile(hardware: HardwareProfile) -> OptimizationProfile:
        """Generate optimization profile"""
        
        if hardware.gpu_tier == GPUTier.HIGH:
            return OptimizationEngine._optimize_high_tier(hardware)
        elif hardware.gpu_tier == GPUTier.MEDIUM:
            return OptimizationEngine._optimize_medium_tier(hardware)
        elif hardware.gpu_tier == GPUTier.LOW:
            return OptimizationEngine._optimize_low_tier(hardware)
        else:
            return OptimizationEngine._optimize_cpu_only(hardware)
    
    @staticmethod
    def _optimize_high_tier(hw: HardwareProfile) -> OptimizationProfile:
        """RTX 3060+, RTX 4080+, A100 optimization"""
        
        return OptimizationProfile(
            num_workers=max(4, hw.cpu_cores - 2),
            batch_size=8,
            max_batch_size=16,
            memory_fraction=0.85,
            quantization="4bit",
            inference_framework="ollama",
            embedding_model_size="large",
            recommended_models=[
                "mistral-7b",
                "neural-chat-7b",
                "llama2-7b-chat",
                "openchat-3.5",
                "sentence-transformers/all-mpnet-base-v2"
            ],
            cpu_threads=hw.cpu_cores,
            ffmpeg_required=False
        )
    
    @staticmethod
    def _optimize_medium_tier(hw: HardwareProfile) -> OptimizationProfile:
        """GTX 1660, RTX 3050 optimization"""
        
        return OptimizationProfile(
            num_workers=max(2, hw.cpu_cores // 2),
            batch_size=4,
            max_batch_size=8,
            memory_fraction=0.90,
            quantization="8bit",
            inference_framework="ollama",
            embedding_model_size="base",
            recommended_models=[
                "phi-2",
                "stablelm-3b",
                "orca-mini-3b",
                "sentence-transformers/all-MiniLM-L6-v2",
                "sentence-transformers/all-MiniLM-L12-v2"
            ],
            cpu_threads=hw.cpu_cores,
            ffmpeg_required=False
        )
    
    @staticmethod
    def _optimize_low_tier(hw: HardwareProfile) -> OptimizationProfile:
        """GTX 1650, GTX 1050 optimization"""
        
        return OptimizationProfile(
            num_workers=2,
            batch_size=2,
            max_batch_size=4,
            memory_fraction=0.95,
            quantization="8bit",
            inference_framework="ollama",
            embedding_model_size="tiny",
            recommended_models=[
                "orca-mini-3b",
                "stablelm-3b",
                "sentence-transformers/all-MiniLM-L6-v2"
            ],
            cpu_threads=hw.cpu_cores,
            ffmpeg_required=False
        )
    
    @staticmethod
    def _optimize_cpu_only(hw: HardwareProfile) -> OptimizationProfile:
        """CPU-only optimization"""
        
        return OptimizationProfile(
            num_workers=max(1, hw.cpu_cores - 1),
            batch_size=1,
            max_batch_size=2,
            memory_fraction=0.7,
            quantization="8bit",
            inference_framework="ollama",
            embedding_model_size="tiny",
            recommended_models=[
                "orca-mini-3b",
                "sentence-transformers/all-MiniLM-L6-v2"
            ],
            cpu_threads=hw.cpu_cores,
            ffmpeg_required=False
        )


class SetupWizard:
    """Interactive setup wizard"""
    
    def __init__(self, hardware: HardwareProfile, optimization: OptimizationProfile):
        self.hardware = hardware
        self.optimization = optimization
        self.config = {}
    
    def print_header(self):
        """Print header"""
        print("\n" + "="*80)
        print(f"{Colors.BOLD}{Colors.CYAN}TARS DISTRIBUTED - SMART SETUP WIZARD{Colors.ENDC}")
        print("="*80 + "\n")
    
    def print_hardware_summary(self):
        """Print hardware summary"""
        print(f"{Colors.BOLD}{Colors.BLUE}📊 HARDWARE DETECTED:{Colors.ENDC}\n")
        
        print(f"  System: {self.hardware.os_type}")
        print(f"  Python: {self.hardware.python_version}")
        print(f"  CPU Cores: {self.hardware.cpu_cores} physical, {self.hardware.cpu_cores_logical} logical")
        print(f"  RAM: {self.hardware.ram_gb:.1f}GB")
        print(f"  Storage: {self.hardware.storage_available_gb:.1f}GB available")
        
        if self.hardware.gpu_count > 0:
            print(f"\n  {Colors.GREEN}🎮 GPUS DETECTED:{Colors.ENDC}")
            for gpu in self.hardware.gpu_info["devices"]:
                print(f"    • {gpu['name']} - {gpu['vram_gb']:.1f}GB VRAM")
            print(f"  Total VRAM: {self.hardware.total_vram_gb:.1f}GB")
            print(f"  GPU Tier: {Colors.GREEN}{self.hardware.gpu_tier.value.upper()}{Colors.ENDC}")
            print(f"  CUDA: {self.hardware.cuda_version}")
        else:
            print(f"\n  {Colors.YELLOW}⚠️  NO GPUS DETECTED{Colors.ENDC} (CPU-only mode)")
        
        print()
    
    def print_optimization_recommendation(self):
        """Print optimization recommendations"""
        print(f"{Colors.BOLD}{Colors.BLUE}⚙️  OPTIMIZATION PROFILE:{Colors.ENDC}\n")
        
        print(f"  Workers: {self.optimization.num_workers}")
        print(f"  Batch Size: {self.optimization.batch_size} (max: {self.optimization.max_batch_size})")
        print(f"  Memory Fraction: {self.optimization.memory_fraction*100:.0f}%")
        print(f"  Quantization: {Colors.GREEN}{self.optimization.quantization.upper()}{Colors.ENDC}")
        print(f"  Framework: {self.optimization.inference_framework}")
        print(f"  Embedding Model: {self.optimization.embedding_model_size.upper()}")
        print(f"  CPU Threads: {self.optimization.cpu_threads}")
        
        print(f"\n  {Colors.GREEN}📦 RECOMMENDED MODELS:{Colors.ENDC}")
        for model in self.optimization.recommended_models:
            print(f"    • {model}")
        
        print()
    
    def ask_pc_role(self) -> str:
        """Ask what role this PC will have"""
        print(f"{Colors.BOLD}{Colors.BLUE}🎯 PC ROLE:{Colors.ENDC}\n")
        
        roles = [
            ("1", "Coordinator (Large Models - like PC1 with RTX 3060)", "coordinator"),
            ("2", "Worker (Embeddings - like PC2 with GTX 1660)", "worker"),
            ("3", "Standalone (Self-contained AI system)", "standalone"),
        ]
        
        for opt, desc, role_id in roles:
            print(f"  {opt}. {desc}")
        
        while True:
            choice = input(f"\n{Colors.YELLOW}Select PC role (1-3): {Colors.ENDC}").strip()
            if choice in ["1", "2", "3"]:
                return [r[2] for r in roles if r[0] == choice][0]
            print(f"{Colors.RED}Invalid choice. Try again.{Colors.ENDC}")
    
    def ask_coordinator_host(self) -> Optional[str]:
        """Ask for coordinator host (if worker)"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}🌐 NETWORK CONFIGURATION:{Colors.ENDC}\n")
        
        host = input("Coordinator host (or 'localhost' for none): ").strip()
        return host if host and host != "localhost" else None
    
    def ask_additional_components(self) -> Dict[str, bool]:
        """Ask about additional components"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}📦 ADDITIONAL COMPONENTS:{Colors.ENDC}\n")
        
        components = {
            "postgresql": ("PostgreSQL (Memory persistence)", True),
            "redis": ("Redis (Caching layer)", True),
            "monitoring": ("Prometheus + Grafana (Monitoring)", False),
            "voice": ("Voice I/O (Speech recognition/TTS)", False),
            "vision": ("Vision Processing (Image analysis)", False),
        }
        
        selected = {}
        for key, (desc, default) in components.items():
            default_str = "[Y/n]" if default else "[y/N]"
            response = input(f"  {desc}? {default_str} ").strip().lower()
            
            if response == "":
                selected[key] = default
            else:
                selected[key] = response in ["y", "yes"]
        
        return selected
    
    def ask_deployment_type(self) -> str:
        """Ask deployment type"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}🚀 DEPLOYMENT TYPE:{Colors.ENDC}\n")
        
        types = [
            ("1", "Local Network (Current setup - RPC/HTTP)", "local"),
            ("2", "Single Machine (All services local)", "single"),
            ("3", "Docker (Containerized)", "docker"),
            ("4", "Kubernetes (Production cluster)", "kubernetes"),
        ]
        
        for opt, desc, _ in types:
            print(f"  {opt}. {desc}")
        
        while True:
            choice = input(f"\n{Colors.YELLOW}Select deployment type (1-4): {Colors.ENDC}").strip()
            if choice in ["1", "2", "3", "4"]:
                return [t[2] for t in types if t[0] == choice][0]
            print(f"{Colors.RED}Invalid choice. Try again.{Colors.ENDC}")
    
    def generate_config(self) -> Dict:
        """Generate final configuration"""
        self.print_hardware_summary()
        self.print_optimization_recommendation()
        
        pc_role = self.ask_pc_role()
        coordinator_host = None
        
        if pc_role == "worker":
            coordinator_host = self.ask_coordinator_host()
        
        additional_components = self.ask_additional_components()
        deployment_type = self.ask_deployment_type()
        
        return {
            "pc_role": pc_role,
            "coordinator_host": coordinator_host,
            "additional_components": additional_components,
            "deployment_type": deployment_type,
            "hardware": {
                "os": self.hardware.os_type,
                "python": self.hardware.python_version,
                "cpu_cores": self.hardware.cpu_cores,
                "ram_gb": self.hardware.ram_gb,
                "gpu_count": self.hardware.gpu_count,
                "gpu_tier": self.hardware.gpu_tier.value,
                "total_vram_gb": self.hardware.total_vram_gb,
                "storage_gb": self.hardware.storage_available_gb,
            },
            "optimization": {
                "num_workers": self.optimization.num_workers,
                "batch_size": self.optimization.batch_size,
                "memory_fraction": self.optimization.memory_fraction,
                "quantization": self.optimization.quantization,
                "framework": self.optimization.inference_framework,
                "models": self.optimization.recommended_models,
            }
        }
    
    def save_config(self, config: Dict, filename: str = "system_setup.json"):
        """Save configuration"""
        with open(filename, "w") as f:
            json.dump(config, f, indent=2)
        print(f"\n{Colors.GREEN}✅ Configuration saved to {filename}{Colors.ENDC}")
    
    def print_next_steps(self, config: Dict):
        """Print next steps"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}🚀 NEXT STEPS:{Colors.ENDC}\n")
        
        if config["pc_role"] == "coordinator":
            print("  1. Run: bash distributed/setup_pc1.sh")
            print("  2. Run: ./run_pc1.sh")
            print("  3. Note your local IP: ifconfig | grep inet")
        elif config["pc_role"] == "worker":
            print("  1. Run: bash distributed/setup_pc2.sh <COORDINATOR_IP>")
            print("  2. Run: ./run_pc2.sh")
        else:
            print("  1. Run: bash distributed/setup_standalone.sh")
            print("  2. Run: ./run_standalone.sh")
        
        print(f"\n  Config saved: {Colors.CYAN}system_setup.json{Colors.ENDC}")
        print()


def main():
    """Main entry point"""
    
    try:
        # Detect hardware
        hardware = HardwareDetector.detect_hardware("NewPC")
        
        # Generate optimization profile
        optimization = OptimizationEngine.generate_profile(hardware)
        
        # Run setup wizard
        wizard = SetupWizard(hardware, optimization)
        wizard.print_header()
        
        config = wizard.generate_config()
        wizard.save_config(config)
        wizard.print_next_steps(config)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Setup cancelled.{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
