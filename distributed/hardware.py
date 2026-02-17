"""
hardware.py
Hardware detection utilities for TARS Distributed
"""

import platform
import sys
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class GPUTier(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

@dataclass
class HardwareProfile:
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

class HardwareDetector:
    @staticmethod
    def get_os_type() -> str:
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
        import psutil
        cpu_physical = psutil.cpu_count(logical=False) or 1
        cpu_logical = psutil.cpu_count(logical=True) or 1
        ram_gb = psutil.virtual_memory().total / (1024**3)
        return cpu_physical, cpu_logical, ram_gb

    @staticmethod
    def get_gpu_info() -> Tuple[bool, str, List[Dict], float]:
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
        except Exception:
            return False, "N/A", [], 0.0

    @staticmethod
    def _get_cuda_cores(gpu_name: str) -> int:
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
        try:
            import shutil
            stat = shutil.disk_usage("/")
            return stat.free / (1024**3)
        except:
            return 0.0

    @staticmethod
    def get_python_version() -> str:
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    @staticmethod
    def detect_gpu_tier(vram_gb: float, gpu_count: int) -> GPUTier:
        if gpu_count == 0:
            return GPUTier.NONE
        elif vram_gb >= 10:
            return GPUTier.HIGH
        elif vram_gb >= 4:
            return GPUTier.MEDIUM
        else:
            return GPUTier.LOW

    @staticmethod
    def detect_hardware(pc_name: str = "NewPC") -> HardwareProfile:
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
