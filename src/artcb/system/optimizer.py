"""Profil d'optimisation runtime base sur le materiel detecte."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

from src.artcb.system.hardware import HardwareProfile, detect_hardware

logger = logging.getLogger("artcb.system.optimizer")


@dataclass
class OptimizationProfile:
    agent_pool_workers: int
    pool_chunk_chars: int
    use_faiss: bool
    use_faiss_gpu: bool
    use_numpy_pol: bool
    ir_cache_enabled: bool
    pdf_async_io: bool
    graph_compression: bool
    node_index_enabled: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_pool_workers": self.agent_pool_workers,
            "pool_chunk_chars": self.pool_chunk_chars,
            "use_faiss": self.use_faiss,
            "use_faiss_gpu": self.use_faiss_gpu,
            "use_numpy_pol": self.use_numpy_pol,
            "ir_cache_enabled": self.ir_cache_enabled,
            "pdf_async_io": self.pdf_async_io,
            "graph_compression": self.graph_compression,
            "node_index_enabled": self.node_index_enabled,
            "optimizations_active": [
                "ir_cache",
                "numpy_pol",
                "pdf_async",
                "graph_compression",
                "node_index",
            ]
            + (["faiss_cpu"] if self.use_faiss and not self.use_faiss_gpu else [])
            + (["faiss_gpu"] if self.use_faiss_gpu else [])
            + (["agent_pool"] if self.agent_pool_workers > 1 else []),
        }


def _faiss_available() -> bool:
    try:
        import faiss  # noqa: F401

        return True
    except ImportError:
        return False


def build_optimization_profile(hw: HardwareProfile | None = None) -> OptimizationProfile:
    """Construit un profil d'optimisation adapte au materiel."""
    hw = hw or detect_hardware()
    workers = max(1, min(hw.cpu_count_logical - 1, 8))
    if hw.memory_total_gb < 4:
        workers = 1

    use_faiss = _faiss_available()
    use_faiss_gpu = use_faiss and (hw.faiss_gpu_count > 0 or len(hw.gpus) > 0)

    chunk = 400
    if hw.memory_total_gb >= 16:
        chunk = 600
    elif hw.memory_total_gb < 4:
        chunk = 200

    if os.getenv("ARTCB_FORCE_CPU", "").lower() in ("1", "true", "yes"):
        use_faiss_gpu = False
        workers = max(1, workers // 2)

    profile = OptimizationProfile(
        agent_pool_workers=workers,
        pool_chunk_chars=chunk,
        use_faiss=use_faiss,
        use_faiss_gpu=use_faiss_gpu,
        use_numpy_pol=True,
        ir_cache_enabled=True,
        pdf_async_io=True,
        graph_compression=True,
        node_index_enabled=True,
    )
    logger.debug(
        "Optimization profile workers=%d faiss_gpu=%s chunk=%d",
        profile.agent_pool_workers,
        profile.use_faiss_gpu,
        profile.pool_chunk_chars,
    )
    return profile


def apply_optimization_profile(profile: OptimizationProfile) -> None:
    """Expose le profil via variables d'environnement pour le runtime."""
    os.environ.setdefault("ARTCB_POOL_CHUNK_CHARS", str(profile.pool_chunk_chars))
    os.environ.setdefault("ARTCB_AGENT_POOL_WORKERS", str(profile.agent_pool_workers))
    if profile.use_faiss_gpu:
        os.environ.setdefault("ARTCB_USE_FAISS_GPU", "true")
    elif profile.use_faiss:
        os.environ.setdefault("ARTCB_USE_FAISS_GPU", "false")


def default_pool_chunk_chars() -> int:
    """Chunk pool par defaut (profil materiel ou 400)."""
    raw = os.getenv("ARTCB_POOL_CHUNK_CHARS", "")
    if raw.isdigit():
        return max(100, min(int(raw), 8000))
    return build_optimization_profile().pool_chunk_chars
