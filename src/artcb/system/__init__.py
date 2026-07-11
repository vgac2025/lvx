"""ARTCB system — hardware detection et optimisations runtime."""

from src.artcb.system.hardware import HardwareProfile, detect_hardware, live_metrics
from src.artcb.system.optimizer import (
    OptimizationProfile,
    apply_optimization_profile,
    build_optimization_profile,
    default_pool_chunk_chars,
)

__all__ = [
    "HardwareProfile",
    "OptimizationProfile",
    "apply_optimization_profile",
    "build_optimization_profile",
    "default_pool_chunk_chars",
    "detect_hardware",
    "live_metrics",
]
