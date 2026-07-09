"""Configuration logging ARTCB — mode DEBUG par défaut (PROTOCOLE)."""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path


def _debug_enabled() -> bool:
    value = os.getenv("ARTCB_DEBUG", "true").lower()
    return value in {"1", "true", "yes", "on"}


def setup_logging(module: str) -> logging.Logger:
    level_name = os.getenv("ARTCB_LOG_LEVEL", "DEBUG" if _debug_enabled() else "INFO")
    level = getattr(logging, level_name.upper(), logging.DEBUG)

    log_dir = Path(os.getenv("ARTCB_LOG_DIR", "./logs"))
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(module)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_path = log_dir / f"{datetime.now(UTC).strftime('%Y%m%d')}_{module.replace('.', '_')}.json"
    file_handler = logging.FileHandler(file_path, encoding="utf-8")

    class JsonLineFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            payload = {
                "ts": datetime.now(UTC).isoformat(),
                "level": record.levelname,
                "module": record.name,
                "message": record.getMessage(),
            }
            return json.dumps(payload, ensure_ascii=False)

    file_handler.setFormatter(JsonLineFormatter())
    logger.addHandler(file_handler)
    logger.propagate = False
    return logger
