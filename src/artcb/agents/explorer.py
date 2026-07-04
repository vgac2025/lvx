"""Explorer agent — hypothesis generation and node decomposition."""

from __future__ import annotations

import logging
import uuid

from artcb.ir.encoder import IREncoder
from artcb.ir.models import IRGraph

logger = logging.getLogger("artcb.agents.explorer")


class ExplorerAgent:
    """Decomposes input text into IR graph nodes (MVP: wraps IREncoder)."""

    def __init__(self, encoder: IREncoder | None = None) -> None:
        self.encoder = encoder or IREncoder()

    def explore(self, text: str, *, graph_id: str | None = None) -> IRGraph:
        gid = graph_id or f"g_{uuid.uuid4().hex[:12]}"
        logger.debug("ExplorerAgent graph_id=%s input_len=%d", gid, len(text))
        graph = self.encoder.encode(text)
        return graph.model_copy(update={"graph_id": gid})
