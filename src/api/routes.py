"""REST routes — CDC §8."""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from artcb.ir.encoder import IREncoder
from artcb.ir.llm_encoder import LLMEncoder
from artcb.ir.models import sha256_text
from artcb.rtleg.events import RTLEGEvent

logger = logging.getLogger("artcb.api.routes")
router = APIRouter(prefix="/api/v1")


class EncodeRequest(BaseModel):
    text: str = Field(min_length=1)
    session_id: str = "sess_default"
    use_llm: bool = False


class DecodeRequest(BaseModel):
    graph_id: str


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    graph_id: str | None = None
    top_k: int = 3


class StoreRequest(BaseModel):
    graph_id: str
    session_id: str = "sess_default"
    visibility: str = "private"


class AgentRunRequest(BaseModel):
    text: str = Field(min_length=1)
    session_id: str = "sess_default"
    use_llm: bool = False


def _state(request: Request):
    return request.app.state.artcb


@router.get("/demo/wailly-excerpt")
def wailly_excerpt(request: Request, max_pages: int = 3) -> dict:
    """Load Wailly book excerpt for hackathon demo (D-010)."""
    from artcb.io.pdf_loader import extract_pdf_text, resolve_book_path

    path = resolve_book_path()
    state = _state(request)
    if path is None:
        fallback = state.settings.demo_book_pdf
        if fallback.is_file():
            path = fallback
    if path is None or not path.is_file():
        raise HTTPException(status_code=404, detail="Wailly PDF not found")
    text = extract_pdf_text(path, max_pages=max_pages)
    return {
        "source": "wailly_le_roi_de_l_inconnu.pdf",
        "max_pages": max_pages,
        "char_count": len(text),
        "text": text,
    }


@router.get("/health")
def health(request: Request) -> dict:
    state = _state(request)
    chain_status = {"available": False}
    try:
        chain_status = {"available": True, **state.chain.verify()}
    except FileNotFoundError as exc:
        chain_status = {"available": False, "message": str(exc)}
    return {
        "status": "ok",
        "debug": state.settings.debug,
        "llm_enabled": state.settings.llm_enabled,
        "bob_configured": bool(state.settings.bob_api_key),
        "demo_book": str(state.settings.demo_book_pdf),
        "chain": chain_status,
    }


@router.post("/encode")
def encode(body: EncodeRequest, request: Request) -> dict:
    state = _state(request)
    graph_id = f"g_{uuid.uuid4().hex[:12]}"
    llm_encoder = LLMEncoder(encoder=state.encoder)
    graph = llm_encoder.encode(body.text, use_llm=body.use_llm, session_id=graph_id)
    state.register_graph(graph)
    state.vectors.index_graph(graph)

    state.timeline.append(
        RTLEGEvent(
            session_id=body.session_id,
            agent="explorer",
            event_type="encode",
            graph_id=graph.graph_id,
            payload={"node_count": len(graph.nodes), "use_llm": body.use_llm},
        )
    )

    compression = IREncoder.compression_ratio(graph)
    return {
        "graph_id": graph.graph_id,
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges),
        "compression_ratio": compression,
        "pol_score": None,
        "nodes_preview": [n.model_dump() for n in graph.nodes[:5]],
    }


@router.post("/decode")
def decode(body: DecodeRequest, request: Request) -> dict:
    state = _state(request)
    graph = state.get_graph(body.graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="graph not found")
    metrics = state.decoder.decode_with_metrics(graph)
    return {
        "original_text": metrics["text"],
        "similarity": metrics["similarity"],
        "reversible": metrics["reversible"],
    }


@router.get("/graph/{graph_id}")
def get_graph(graph_id: str, request: Request) -> dict:
    state = _state(request)
    graph = state.get_graph(graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="graph not found")
    return graph.to_canonical_dict()


@router.get("/node/{node_id}")
def get_node(
    node_id: str,
    request: Request,
    graph_id: str | None = Query(default=None),
) -> dict:
    state = _state(request)
    if graph_id:
        graph = state.get_graph(graph_id)
        if not graph:
            raise HTTPException(status_code=404, detail="graph not found")
        for node in graph.nodes:
            if node.id == node_id:
                return node.model_dump()
        raise HTTPException(status_code=404, detail="node not found")

    if node_id in state.node_index:
        gid, _ = state.node_index[node_id]
        graph = state.get_graph(gid)
        if graph:
            for node in graph.nodes:
                if node.id == node_id:
                    return {**node.model_dump(), "graph_id": gid}
    raise HTTPException(status_code=404, detail="node not found")


@router.post("/search")
def search(body: SearchRequest, request: Request) -> dict:
    state = _state(request)
    results = state.vectors.search(body.query, graph_id=body.graph_id, top_k=body.top_k)
    return {"query": body.query, "results": results, "count": len(results)}


@router.post("/store")
def store(body: StoreRequest, request: Request) -> dict:
    state = _state(request)
    graph = state.get_graph(body.graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="graph not found")

    result = state.dual.critic.validate(graph)
    pol = result.pol
    if not pol.block_accepted:
        state.pol_state["blocks_rejected"] += 1
        raise HTTPException(
            status_code=422,
            detail={"message": "PoL below threshold", "pol": pol.to_dict()},
        )

    graph_root = sha256_text(graph.checksum)
    block = state.chain.append_block(
        graph_id=graph.graph_id,
        graph_root=graph_root.replace("sha256:", ""),
        pol_score=pol.pol_score,
        visibility=body.visibility,
    )
    state.pol_state["pol_score"] = pol.pol_score
    state.pol_state["compression_rate"] = pol.delta_compression
    state.pol_state["validation_rate"] = pol.validation_rate
    state.pol_state["retrieval_accuracy"] = pol.retrieval_accuracy
    state.pol_state["blocks_accepted"] += 1

    state.timeline.append(
        RTLEGEvent(
            session_id=body.session_id,
            agent="critic",
            event_type="block_stored",
            graph_id=graph.graph_id,
            payload={"index": block.index, "hash": block.hash, "pol": pol.pol_score},
        )
    )

    return {
        "block_index": block.index,
        "hash": block.hash,
        "block_reward": block.block_reward,
        "contributors": block.contributors,
        "signature": block.signature,
        "pol_score": pol.pol_score,
        "graph_id": graph.graph_id,
    }


@router.get("/chain")
def chain_list(request: Request) -> dict:
    state = _state(request)
    blocks = state.chain.list_blocks()
    return {"blocks": blocks, "count": len(blocks)}


@router.get("/chain/verify")
def chain_verify(request: Request) -> dict:
    state = _state(request)
    return state.chain.verify()


@router.get("/pol/score")
def pol_score(request: Request) -> dict:
    return _state(request).pol_state

@router.get("/metrics")
def system_metrics() -> dict:
    """Métriques système temps réel (CPU, RAM, Disk, Network)."""
    try:
        import psutil
        import platform
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # RAM
        mem = psutil.virtual_memory()
        
        # Disk
        disk = psutil.disk_usage('/')
        
        # Network
        net_io = psutil.net_io_counters()
        
        # System info
        sys_info = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "hostname": platform.node(),
            "processor": platform.processor(),
        }
        
        return {
            "cpu": {
                "percent": cpu_percent,
                "count": cpu_count,
                "freq_mhz": cpu_freq.current if cpu_freq else 0,
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
                "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 2),
                "bytes_recv_mb": round(net_io.bytes_recv / (1024**2), 2),
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
            },
            "system": sys_info,
        }
    except ImportError:
        raise HTTPException(status_code=500, detail="psutil not installed")
    except Exception as e:
        logger.error(f"Error fetching system metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WALLET ROUTES — Rewards & Balance Tracking
# ============================================================================

class CreateWalletRequest(BaseModel):
    name: str = "default"


class WalletBalanceRequest(BaseModel):
    address: str


@router.post("/wallet/create")
def wallet_create(body: CreateWalletRequest, request: Request) -> dict:
    """Create new ARTCB wallet with Ed25519 keypair."""
    from artcb.wallet.manager import WalletManager
    
    state = _state(request)
    wallet_mgr = WalletManager()
    
    try:
        wallet = wallet_mgr.create_wallet(name=body.name)
        logger.info("Created wallet name=%s address=%s", body.name, wallet.address)
        return {
            "name": body.name,
            "address": wallet.address,
            "public_key_hex": wallet.public_key_hex,
            "public_key_b64": wallet.public_key_b64,
        }
    except FileExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.get("/wallet/list")
def wallet_list(request: Request) -> dict:
    """List all wallets."""
    from artcb.wallet.manager import WalletManager
    
    wallet_mgr = WalletManager()
    wallets = wallet_mgr.list_wallets()
    return {"wallets": wallets, "count": len(wallets)}


@router.post("/wallet/balance")
def wallet_balance(body: WalletBalanceRequest, request: Request) -> dict:
    """Get wallet balance from blockchain."""
    from artcb.wallet.manager import WalletManager
    
    state = _state(request)
    wallet_mgr = WalletManager()
    
    balance = wallet_mgr.get_balance(body.address, state.chain.blocks_path)
    return balance


@router.get("/wallet/balance/{address}")
def wallet_balance_get(address: str, request: Request) -> dict:
    """Get wallet balance from blockchain (GET variant)."""
    from artcb.wallet.manager import WalletManager
    
    state = _state(request)
    wallet_mgr = WalletManager()
    
    balance = wallet_mgr.get_balance(address, state.chain.blocks_path)
    return balance




@router.post("/agents/run")
def agents_run(body: AgentRunRequest, request: Request) -> dict:
    state = _state(request)
    if body.use_llm:
        graph = LLMEncoder(encoder=state.encoder).encode(
            body.text, use_llm=True, session_id=f"g_{uuid.uuid4().hex[:12]}"
        )
        result = state.dual.critic.validate(graph)
    else:
        result = state.dual.run(body.text)

    graph = result.graph
    state.register_graph(graph)
    state.vectors.index_graph(graph)

    pol = result.pol
    state.pol_state["pol_score"] = pol.pol_score
    state.pol_state["compression_rate"] = pol.delta_compression
    state.pol_state["validation_rate"] = pol.validation_rate
    state.pol_state["retrieval_accuracy"] = pol.retrieval_accuracy
    if pol.block_accepted:
        state.pol_state["blocks_accepted"] += 1
    else:
        state.pol_state["blocks_rejected"] += 1

    state.timeline.append(
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


@router.get("/rtleg/events")
def rtleg_events(
    request: Request,
    session_id: str | None = None,
    limit: int = 100,
) -> dict:
    state = _state(request)
    events = state.timeline.list_events(session_id=session_id, limit=limit)
    return {"events": [e.model_dump() for e in events], "count": len(events)}
