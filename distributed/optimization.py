"""
optimization.py
Optimization profile generation for TARS Distributed
"""

from dataclasses import dataclass
from typing import List
from .hardware import HardwareProfile, GPUTier

@dataclass
class OptimizationProfile:
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

class OptimizationEngine:
    @staticmethod
    def generate_profile(hardware: HardwareProfile) -> OptimizationProfile:
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
