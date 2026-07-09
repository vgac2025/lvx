"""Encodage texte humain → graphe IR ARTCB v0.1 (fallback rule-based)."""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass

from artcb.ir.grammar import (
    ACTION_TRIGGERS,
    CONTEXT_KEYWORDS,
    DECISION_KEYWORDS,
    EVENT_KEYWORDS,
    GOAL_KEYWORDS,
    HYPOTHESIS_KEYWORDS,
    OBJECT_TRIGGERS,
    PROOF_KEYWORDS,
    REASON_KEYWORDS,
    EdgeType,
    NodeType,
)
from artcb.ir.macros import apply_macros_to_graph
from artcb.ir.models import IREdge, IRGraph, IRNode, sha256_text
from artcb.ir.symbols import SymbolRegistry

logger = logging.getLogger("artcb.ir.encoder")


@dataclass
class SentenceSpan:
    text: str
    start: int
    end: int


class IREncoder:
    """Encode text into IR graph with guaranteed reversibility via source_text + spans."""

    def __init__(self, symbol_registry: SymbolRegistry | None = None, enable_cache: bool = True) -> None:
        self._registry = symbol_registry or SymbolRegistry()
        self._cache: dict[str, IRGraph] = {} if enable_cache else None
        self._cache_enabled = enable_cache

    def encode(self, text: str, session_id: str | None = None) -> IRGraph:
        # Cache optimization: Check if text already encoded
        if self._cache_enabled and self._cache is not None:
            text_hash = sha256_text(text)
            if text_hash in self._cache:
                cached = self._cache[text_hash]
                logger.debug("Cache HIT text_hash=%s reusing graph", text_hash[:16])
                # Return copy with new session_id if provided
                new_graph_id = session_id or f"g_{uuid.uuid4().hex[:12]}"
                return cached.model_copy(update={"graph_id": new_graph_id})

        # Cache MISS or cache disabled: perform full encoding
        if not text or not text.strip():
            raise ValueError("Le texte à encoder ne peut pas être vide.")

        graph_id = session_id or f"g_{uuid.uuid4().hex[:12]}"
        spans = self._split_into_spans(text)
        logger.debug("Encodage graph_id=%s spans=%d chars=%d", graph_id, len(spans), len(text))

        nodes: list[IRNode] = []
        edges: list[IREdge] = []

        for index, span in enumerate(spans, start=1):
            node_id = f"n{index}"
            node_type = self._classify_sentence(span.text)
            symbol = self._build_symbol(span.text, node_type)
            nodes.append(
                IRNode(
                    id=node_id,
                    t=node_type.value,
                    sym=symbol,
                    txt=span.text,
                    checksum=sha256_text(span.text),
                    start=span.start,
                    end=span.end,
                )
            )
            if index > 1:
                edges.append(
                    IREdge(
                        **{
                            "from": f"n{index - 1}",
                            "to": node_id,
                            "rel": EdgeType.TEMPORAL.value,
                            "w": 1.0,
                        }
                    )
                )
                if self._has_causal_link(spans[index - 2].text, span.text):
                    edges.append(
                        IREdge(
                            **{
                                "from": f"n{index - 1}",
                                "to": node_id,
                                "rel": EdgeType.CAUSES.value,
                                "w": 0.8,
                            }
                        )
                    )

        join_sep = self._detect_join_separator(text, spans)
        graph = IRGraph(
            graph_id=graph_id,
            source_text=text,
            nodes=nodes,
            edges=edges,
            checksum=sha256_text(text),
            join_sep=join_sep,
            orig_symbols=self._registry.export(),
        )

        if not graph.verify_integrity():
            raise RuntimeError("Échec vérification intégrité après encodage.")

        graph = apply_macros_to_graph(graph)

        # Store in cache for future reuse
        if self._cache_enabled and self._cache is not None:
            text_hash = sha256_text(text)
            self._cache[text_hash] = graph
            logger.debug("Cache STORE text_hash=%s", text_hash[:16])

        logger.debug(
            "Encodage terminé nodes=%d edges=%d macros=%d compression=%.2f cache_size=%d",
            len(graph.nodes),
            len(graph.edges),
            len(graph.macros),
            self.compression_ratio(graph),
            len(self._cache) if self._cache else 0,
        )
        return graph

    @staticmethod
    def compression_ratio(graph: IRGraph) -> float:
        if not graph.source_text:
            return 0.0
        ir_size = len(graph.to_json(indent=None))
        return round(1.0 - (ir_size / len(graph.source_text)), 4)

    def _split_into_spans(self, text: str) -> list[SentenceSpan]:
        spans: list[SentenceSpan] = []
        cursor = 0
        length = len(text)

        while cursor < length:
            while cursor < length and text[cursor].isspace():
                cursor += 1
            if cursor >= length:
                break

            boundary = self._find_sentence_end(text, cursor)
            segment = text[cursor:boundary]
            if segment.strip():
                spans.append(SentenceSpan(text=segment, start=cursor, end=boundary))
            cursor = boundary

        if not spans:
            spans.append(SentenceSpan(text=text, start=0, end=len(text)))

        return spans

    @staticmethod
    def _find_sentence_end(text: str, start: int) -> int:
        length = len(text)
        i = start
        while i < length:
            char = text[i]
            if char in ".!?…":
                j = i + 1
                while j < length and text[j] in "\"'»)":
                    j += 1
                if j >= length or text[j].isspace() or text[j] == "\n":
                    return j if j < length else length
            i += 1
        return length

    @staticmethod
    def _detect_join_separator(text: str, spans: list[SentenceSpan]) -> str:
        if len(spans) < 2:
            return ""
        between = text[spans[0].end : spans[1].start]
        if between:
            return between
        return " "

    def _classify_sentence(self, sentence: str) -> NodeType:
        lowered = sentence.lower()
        if any(k in lowered for k in DECISION_KEYWORDS):
            return NodeType.DECISION
        if any(k in lowered for k in HYPOTHESIS_KEYWORDS):
            return NodeType.HYPOTHESIS
        if any(k in lowered for k in REASON_KEYWORDS):
            return NodeType.REASON
        if any(k in lowered for k in GOAL_KEYWORDS):
            return NodeType.GOAL
        if any(k in lowered for k in PROOF_KEYWORDS):
            return NodeType.PROOF
        if any(k in lowered for k in EVENT_KEYWORDS):
            return NodeType.EVENT
        if any(k in lowered for k in CONTEXT_KEYWORDS):
            return NodeType.CONTEXT
        return NodeType.FACT

    def _build_symbol(self, sentence: str, node_type: NodeType) -> str:
        lowered = sentence.lower()
        action = "O1"
        for trigger, code in ACTION_TRIGGERS.items():
            if trigger in lowered:
                action = code
                break

        obj = ""
        for trigger, code in OBJECT_TRIGGERS.items():
            if trigger in lowered:
                obj = code
                break

        if not obj:
            type_fallback = {
                NodeType.DECISION: "K1",
                NodeType.HYPOTHESIS: "H",
                NodeType.REASON: "R1",
                NodeType.GOAL: "G",
                NodeType.PROOF: "P",
                NodeType.EVENT: "E",
                NodeType.CONTEXT: "M2",
            }
            obj = type_fallback.get(node_type, self._registry.mint_original(sentence))

        return f"{action}{obj}"

    @staticmethod
    def _has_causal_link(previous: str, current: str) -> bool:
        causal_markers = ("donc", "ainsi", "par conséquent", "par consequent", "alors", "c'est pourquoi")
        return any(marker in current.lower() for marker in causal_markers)
