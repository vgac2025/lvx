"""FastAPI application — ARTCB MVP Phase 2."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from artcb.agents.critic import DualAgentLoop
from artcb.config import load_settings
from artcb.ir.decoder import IRDecoder
from artcb.ir.encoder import IREncoder
from artcb.ir.models import IRGraph
from artcb.pol.scorer import PolScorer
from artcb.rtleg.events import RTLEGEvent
from artcb.rtleg.timeline import RTLEGTimeline

logger = logging.getLogger("artcb.api")
settings = load_settings()

app = FastAPI(title="ARTCB API", version="0.2.0")

_graph_store: dict[str, IRGraph] = {}
_pol_state: dict[str, Any] = {
    "pol_score": None,
    "compression_rate": None,
    "validation_rate": None,
    "retrieval_accuracy": None,
    "blocks_accepted": 0,
    "blocks_rejected": 0,
}

_encoder = IREncoder()
_decoder = IRDecoder()
_dual = DualAgentLoop()
_timeline = RTLEGTimeline()
_scorer = PolScorer()


class EncodeRequest(BaseModel):
    text: str = Field(min_length=1)
    session_id: str = "sess_default"
    use_llm: bool = False


class DecodeRequest(BaseModel):
    graph_id: str


class AgentRunRequest(BaseModel):
    text: str = Field(min_length=1)
    session_id: str = "sess_default"


@app.get("/api/v1/health")
def health() -> dict:
    return {
        "status": "ok",
        "debug": settings.debug,
        "llm_enabled": settings.llm_enabled,
        "demo_book": str(settings.demo_book_pdf),
    }


@app.post("/api/v1/encode")
def encode(body: EncodeRequest) -> dict:
    graph_id = f"g_{uuid.uuid4().hex[:12]}"
    graph = _encoder.encode(body.text)
    graph = graph.model_copy(update={"graph_id": graph_id})
    _graph_store[graph_id] = graph

    _timeline.append(
        RTLEGEvent(
            session_id=body.session_id,
            agent="explorer",
            event_type="encode",
            graph_id=graph_id,
            payload={"node_count": len(graph.nodes)},
        )
    )

    compression = IREncoder.compression_ratio(graph)
    return {
        "graph_id": graph_id,
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges),
        "compression_ratio": compression,
        "pol_score": None,
        "nodes_preview": [n.model_dump() for n in graph.nodes[:5]],
    }


@app.post("/api/v1/decode")
def decode(body: DecodeRequest) -> dict:
    graph = _graph_store.get(body.graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="graph not found")
    metrics = _decoder.decode_with_metrics(graph)
    return {
        "original_text": metrics["text"],
        "similarity": metrics["similarity"],
        "reversible": metrics["reversible"],
    }


@app.get("/api/v1/graph/{graph_id}")
def get_graph(graph_id: str) -> dict:
    graph = _graph_store.get(graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="graph not found")
    return graph.to_canonical_dict()


@app.get("/api/v1/pol/score")
def pol_score() -> dict:
    return {
        "pol_score": _pol_state["pol_score"],
        "compression_rate": _pol_state["compression_rate"],
        "validation_rate": _pol_state["validation_rate"],
        "retrieval_accuracy": _pol_state["retrieval_accuracy"],
        "blocks_accepted": _pol_state["blocks_accepted"],
        "blocks_rejected": _pol_state["blocks_rejected"],
    }


@app.post("/api/v1/agents/run")
def agents_run(body: AgentRunRequest) -> dict:
    result = _dual.run(body.text)
    graph = result.graph
    _graph_store[graph.graph_id] = graph

    pol = result.pol
    _pol_state["pol_score"] = pol.pol_score
    _pol_state["compression_rate"] = pol.delta_compression
    _pol_state["validation_rate"] = pol.validation_rate
    _pol_state["retrieval_accuracy"] = pol.retrieval_accuracy
    if pol.block_accepted:
        _pol_state["blocks_accepted"] += 1
    else:
        _pol_state["blocks_rejected"] += 1

    _timeline.append(
        RTLEGEvent(
            session_id=body.session_id,
            agent="critic",
            event_type="pol_validated",
            graph_id=graph.graph_id,
            payload=pol.to_dict(),
        )
    )

    return {
        "graph_id": graph.graph_id,
        "node_count": len(graph.nodes),
        "pol": pol.to_dict(),
        "nodes_validated": result.nodes_validated,
        "nodes_proposed": result.nodes_proposed,
    }


@app.get("/api/v1/rtleg/events")
def rtleg_events(session_id: str | None = None, limit: int = 100) -> dict:
    events = _timeline.list_events(session_id=session_id, limit=limit)
    return {"events": [e.model_dump() for e in events], "count": len(events)}
