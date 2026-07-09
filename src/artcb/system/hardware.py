"""Detection materielle multi-plateforme — CPU, RAM, GPU, disque."""

from __future__ import annotations

import logging
import os
import platform
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("artcb.system.hardware")


@dataclass
class HardwareProfile:
    platform_system: str
    platform_release: str
    architecture: str
    hostname: str
    processor: str
    cpu_count_logical: int
    cpu_count_physical: int
    cpu_freq_mhz: float
    memory_total_gb: float
    memory_available_gb: float
    disk_total_gb: float
    disk_free_gb: float
    gpus: list[dict[str, Any]] = field(default_factory=list)
    faiss_gpu_count: int = 0
    cuda_visible: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "platform": {
                "system": self.platform_system,
                "release": self.platform_release,
                "architecture": self.architecture,
                "hostname": self.hostname,
                "processor": self.processor,
            },
            "cpu": {
                "logical_cores": self.cpu_count_logical,
                "physical_cores": self.cpu_count_physical,
                "freq_mhz": round(self.cpu_freq_mhz, 1),
            },
            "memory": {
                "total_gb": round(self.memory_total_gb, 2),
                "available_gb": round(self.memory_available_gb, 2),
            },
            "disk": {
                "total_gb": round(self.disk_total_gb, 2),
                "free_gb": round(self.disk_free_gb, 2),
            },
            "gpus": self.gpus,
            "faiss_gpu_count": self.faiss_gpu_count,
            "cuda_visible": self.cuda_visible,
        }


def _detect_nvidia_gpus() -> list[dict[str, Any]]:
    if not shutil.which("nvidia-smi"):
        return []
    try:
        out = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=index,name,memory.total,driver_version",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
        if out.returncode != 0:
            return []
        gpus: list[dict[str, Any]] = []
        for line in out.stdout.strip().splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 4:
                gpus.append({
                    "index": int(parts[0]),
                    "name": parts[1],
                    "memory_mb": int(float(parts[2])),
                    "driver": parts[3],
                    "backend": "cuda",
                })
        return gpus
    except Exception as exc:
        logger.debug("nvidia-smi failed: %s", exc)
        return []


def _detect_faiss_gpus() -> int:
    try:
        import faiss  # type: ignore

        return int(faiss.get_num_gpus())
    except Exception:
        return 0


def detect_hardware() -> HardwareProfile:
    """Detecte le materiel utilisable sur Linux, macOS ou Windows."""
    import psutil

    cpu_freq = psutil.cpu_freq()
    mem = psutil.virtual_memory()
    disk_path = os.environ.get("ARTCB_DATA_DIR", ".")
    if not os.path.exists(disk_path):
        disk_path = "/"
    try:
        disk = psutil.disk_usage(disk_path)
    except Exception:
        disk = psutil.disk_usage("/")

    physical = psutil.cpu_count(logical=False) or psutil.cpu_count() or 1
    logical = psutil.cpu_count(logical=True) or physical

    gpus = _detect_nvidia_gpus()
    faiss_gpus = _detect_faiss_gpus()
    if faiss_gpus > 0 and not gpus:
        for i in range(faiss_gpus):
            gpus.append({"index": i, "name": "FAISS GPU", "backend": "faiss-cuda"})

    return HardwareProfile(
        platform_system=platform.system(),
        platform_release=platform.release(),
        architecture=platform.machine(),
        hostname=platform.node(),
        processor=platform.processor() or "unknown",
        cpu_count_logical=logical,
        cpu_count_physical=physical,
        cpu_freq_mhz=cpu_freq.current if cpu_freq else 0.0,
        memory_total_gb=mem.total / (1024**3),
        memory_available_gb=mem.available / (1024**3),
        disk_total_gb=disk.total / (1024**3),
        disk_free_gb=disk.free / (1024**3),
        gpus=gpus,
        faiss_gpu_count=faiss_gpus,
        cuda_visible=bool(os.environ.get("CUDA_VISIBLE_DEVICES")),
    )


def live_metrics() -> dict[str, Any]:
    """Metriques temps reel (CPU%, RAM%, reseau)."""
    import psutil

    cpu_percent = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    disk_path = os.environ.get("ARTCB_DATA_DIR", ".")
    if not os.path.exists(disk_path):
        disk_path = "/"
    try:
        disk = psutil.disk_usage(disk_path)
    except Exception:
        disk = psutil.disk_usage("/")
    net = psutil.net_io_counters()

    return {
        "cpu": {
            "percent": cpu_percent,
            "count": psutil.cpu_count(logical=True),
            "freq_mhz": (psutil.cpu_freq().current if psutil.cpu_freq() else 0),
        },
        "memory": {
            "total_gb": round(mem.total / (1024**3), 2),
            "used_gb": round(mem.used / (1024**3), 2),
            "available_gb": round(mem.available / (1024**3), 2),
            "percent": mem.percent,
        },
        "disk": {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent": disk.percent,
        },
        "network": {
            "bytes_sent_mb": round(net.bytes_sent / (1024**2), 2),
            "bytes_recv_mb": round(net.bytes_recv / (1024**2), 2),
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv,
        },
    }
