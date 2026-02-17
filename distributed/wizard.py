"""
wizard.py
Interactive setup wizard for TARS Distributed
"""

import json
from typing import Dict, Optional
from .hardware import HardwareProfile
from .optimization import OptimizationProfile

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

class SetupWizard:
    def __init__(self, hardware: HardwareProfile, optimization: OptimizationProfile):
        self.hardware = hardware
        self.optimization = optimization
        self.config = {}

    def print_header(self):
        print("\n" + "="*80)
        print(f"{Colors.BOLD}{Colors.CYAN}TARS DISTRIBUTED - SMART SETUP WIZARD{Colors.ENDC}")
        print("="*80 + "\n")

    def print_hardware_summary(self):
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
        print(f"\n{Colors.BOLD}{Colors.BLUE}🌐 NETWORK CONFIGURATION:{Colors.ENDC}\n")
        host = input("Coordinator host (or 'localhost' for none): ").strip()
        return host if host and host != "localhost" else None

    def ask_additional_components(self) -> Dict[str, bool]:
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
        with open(filename, "w") as f:
            json.dump(config, f, indent=2)
        print(f"\n{Colors.GREEN}✅ Configuration saved to {filename}{Colors.ENDC}")

    def print_next_steps(self, config: Dict):
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
