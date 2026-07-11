"""WebSocket realtime graph updates — CDC §20."""

from __future__ import annotations

import json
import logging
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.artcb.ir.encoder import IREncoder
from src.artcb.ir.llm_encoder import LLMEncoder
from src.artcb.rtleg.events import RTLEGEvent

logger = logging.getLogger("artcb.api.websocket")
router = APIRouter()


@router.websocket("/ws/graph/{session_id}")
async def graph_ws(websocket: WebSocket, session_id: str) -> None:
    await websocket.accept()
    state = websocket.app.state.artcb
    logger.debug("WebSocket connected session_id=%s", session_id)

    try:
        while True:
            raw = await websocket.receive_text()
            message = json.loads(raw)
            msg_type = message.get("type")
            payload = message.get("payload") or message

            if msg_type == "encode":
                text = payload.get("text", "")
                use_llm = bool(payload.get("use_llm", False))
                graph_id = f"g_{uuid.uuid4().hex[:12]}"
                graph = LLMEncoder(encoder=state.encoder).encode(
                    text, use_llm=use_llm, session_id=graph_id
                )
                state.register_graph(graph)
                state.vectors.index_graph(graph)
                for node in graph.nodes:
                    await websocket.send_json(
                        {
                            "type": "node_added",
                            "node": node.model_dump(),
                            "agent": "explorer",
                        }
                    )
                state.timeline.append(
                    RTLEGEvent(
                        session_id=session_id,
                        agent="explorer",
                        event_type="ws_encode",
                        graph_id=graph.graph_id,
                        payload={"nodes": len(graph.nodes)},
                    )
                )
                await websocket.send_json(
                    {
                        "type": "encode_complete",
                        "graph_id": graph.graph_id,
                        "node_count": len(graph.nodes),
                        "compression_ratio": IREncoder.compression_ratio(graph),
                    }
                )

            elif msg_type == "search":
                query = payload.get("query", "")
                results = state.vectors.search(query, top_k=3)
                await websocket.send_json({"type": "search_results", "results": results})

            elif msg_type == "select_node":
                node_id = payload.get("node_id")
                graph_id = payload.get("graph_id")
                graph = state.get_graph(graph_id) if graph_id else None
                node = None
                if graph:
                    node = next((n for n in graph.nodes if n.id == node_id), None)
                await websocket.send_json(
                    {
                        "type": "node_selected",
                        "node_id": node_id,
                        "node": node.model_dump() if node else None,
                    }
                )

            elif msg_type == "agents_run":
                text = payload.get("text", "")
                result = state.dual.run(text)
                graph = result.graph
                state.register_graph(graph)
                state.vectors.index_graph(graph)
                await websocket.send_json(
                    {
                        "type": "pol_update",
                        "score": result.pol.pol_score,
                        "compression": result.pol.delta_compression,
                        "validation": result.pol.validation_rate,
                    }
                )
                await websocket.send_json(
                    {
                        "type": "node_validated",
                        "graph_id": graph.graph_id,
                        "agent": "critic",
                        "pol_delta": result.pol.pol_score,
                    }
                )

            else:
                await websocket.send_json(
                    {"type": "error", "code": "unknown_type", "message": f"Unknown type: {msg_type}"}
                )

    except WebSocketDisconnect:
        logger.debug("WebSocket disconnected session_id=%s", session_id)
    except json.JSONDecodeError as exc:
        logger.error("WebSocket JSON error: %s", exc)
        await websocket.send_json(
            {"type": "error", "code": "invalid_json", "message": str(exc)}
        )
