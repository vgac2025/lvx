"""LLM enrichment path B — Bob client + rule-based fallback (D-008)."""

from __future__ import annotations

import logging

from artcb.ir.bob_client import BobClient
from artcb.ir.encoder import IREncoder
from artcb.ir.grammar import NodeType
from artcb.ir.models import IRGraph

logger = logging.getLogger("artcb.ir.llm_encoder")


class LLMEncoder:
    """Wraps rule-based encoder; optionally enriches node types via Bob HTTP."""

    def __init__(
        self,
        encoder: IREncoder | None = None,
        bob: BobClient | None = None,
    ) -> None:
        self.encoder = encoder or IREncoder()
        self.bob = bob or BobClient()

    def encode(self, text: str, *, use_llm: bool = False, session_id: str | None = None) -> IRGraph:
        graph = self.encoder.encode(text, session_id=session_id)
        if not use_llm:
            return graph

        sentences = [node.txt for node in graph.nodes]
        classifications = self.bob.classify_sentences(sentences)
        if not classifications:
            logger.debug("LLM enrichment skipped — rule-based graph returned")
            return graph

        type_map = {member.value: member for member in NodeType}
        nodes = list(graph.nodes)
        for item in classifications:
            try:
                idx = int(item["index"])
            except (TypeError, ValueError):
                continue
            if idx < 0 or idx >= len(nodes):
                continue
            node = nodes[idx]
            node_type = type_map.get(item["type"].upper(), NodeType.FACT)
            symbol = item.get("symbol") or node.sym
            nodes[idx] = node.model_copy(update={"t": node_type.value, "sym": symbol})

        enriched = graph.model_copy(update={"nodes": nodes})
        logger.debug("LLM enrichment applied nodes=%d", len(nodes))
        return enriched
