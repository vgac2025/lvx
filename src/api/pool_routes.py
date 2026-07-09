"""Pool calcul distribué E2E — routes REST ML-KEM."""

from __future__ import annotations

import logging
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from artcb.pool.service import PoolError

logger = logging.getLogger("artcb.api.pool")
router = APIRouter(prefix="/api/v1/pool", tags=["pool"])


class PoolWorkerSpec(BaseModel):
    node_id: str = Field(min_length=4)
    kem_public_hex: str = Field(min_length=32)
    base_url: str | None = None


class CreatePoolJobRequest(BaseModel):
    text: str = Field(min_length=1)
    visibility: str = "private"
    workers: list[PoolWorkerSpec] = Field(default_factory=list)
    actor_address: str | None = None
    wallet_name: str | None = None
    chunk_chars: int = Field(default=400, ge=100, le=8000)
    auto_dispatch: bool = True


class PoolResultRequest(BaseModel):
    chunk_id: str
    result_envelope: dict[str, str]


class FinalizePoolJobRequest(BaseModel):
    full_text: str = Field(min_length=1)


class ProcessIncomingRequest(BaseModel):
    wallet_name: str | None = None
    contributor_address: str | None = None


def _state(request: Request):
    return request.app.state.artcb


def _pool(request: Request):
    return _state(request).pool


def _owner_base_url(request: Request) -> str:
    return str(request.base_url).rstrip("/")


def _discover_workers(request: Request) -> list[dict[str, str]]:
    """Auto-découverte : nœud local + pairs P2P (status HTTP)."""
    state = _state(request)
    identity = state.p2p_identity
    workers: list[dict[str, str]] = [{
        "node_id": identity.node_id,
        "kem_public_hex": identity.kem_public_key_hex,
        "base_url": _owner_base_url(request),
    }]
    seen = {identity.node_id}
    for peer in state.p2p_peers.list_peers():
        try:
            with httpx.Client(timeout=8.0) as client:
                r = client.get(f"{peer.base_url}/api/v1/p2p/status")
                r.raise_for_status()
                body = r.json()
                nid = body["node_id"]
                if nid in seen:
                    continue
                workers.append({
                    "node_id": nid,
                    "kem_public_hex": body["kem_public_key_hex"],
                    "base_url": peer.base_url,
                })
                seen.add(nid)
        except Exception as exc:
            logger.warning("Pool worker discovery failed for %s: %s", peer.base_url, exc)
    return workers


def _build_peer_urls(request: Request, workers: list[dict[str, str]] | None = None) -> dict[str, str]:
    urls = {_state(request).p2p_identity.node_id: _owner_base_url(request)}
    for w in workers or _discover_workers(request):
        if w.get("base_url"):
            urls[w["node_id"]] = w["base_url"].rstrip("/")
    return urls


@router.get("/status")
def pool_status(request: Request) -> dict[str, Any]:
    state = _state(request)
    pool = state.pool
    jobs = pool.list_jobs()
    incoming = pool.list_incoming()
    return {
        "enabled": True,
        "crypto": "ML-KEM-768",
        "contexts": ["artcb-pool-chunk-v1", "artcb-pool-result-v1"],
        "node_id": state.p2p_identity.node_id,
        "kem_public_key_hex": state.p2p_identity.kem_public_key_hex,
        "job_count": len(jobs),
        "incoming_pending": len(incoming),
        "plaintext_on_network": False,
        "rule": "Calcul raisonnement local par worker — transport morceaux/résultats chiffrés E2E",
    }


@router.get("/jobs")
def list_pool_jobs(request: Request) -> dict:
    jobs = _pool(request).list_jobs()
    return {"jobs": [j.to_dict() for j in jobs], "count": len(jobs)}


@router.get("/jobs/{job_id}")
def get_pool_job(job_id: str, request: Request) -> dict:
    job = _pool(request).get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job introuvable")
    return {"job": job.to_dict()}


@router.post("/jobs")
def create_pool_job(body: CreatePoolJobRequest, request: Request) -> dict:
    pool = _pool(request)
    workers = [w.model_dump() for w in body.workers] if body.workers else _discover_workers(request)
    if len(workers) < 1:
        raise HTTPException(status_code=400, detail="Aucun worker disponible")
    try:
        job = pool.create_job(
            body.text,
            visibility=body.visibility,
            workers=workers,
            actor_address=body.actor_address,
            wallet_name=body.wallet_name,
            chunk_chars=body.chunk_chars,
        )
    except PoolError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    dispatch_results = None
    if body.auto_dispatch:
        peer_urls = _build_peer_urls(request, workers)
        dispatch_results = pool.dispatch_to_peers(job, peer_urls)

    return {
        "job": job.to_dict(),
        "workers": workers,
        "dispatch": dispatch_results,
        "encrypted_transport": True,
        "message": "Job pool créé — morceaux chiffrés ML-KEM E2E par worker",
    }


@router.post("/jobs/{job_id}/dispatch")
def dispatch_pool_job(job_id: str, request: Request) -> dict:
    pool = _pool(request)
    job = pool.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job introuvable")
    peer_urls = _build_peer_urls(request)
    results = pool.dispatch_to_peers(job, peer_urls)
    return {"job_id": job_id, "results": results, "encrypted": True}


@router.post("/incoming")
def receive_pool_chunk(payload: dict, request: Request) -> dict:
    """Worker reçoit un morceau chiffré (jamais en clair)."""
    try:
        return _pool(request).receive_incoming_chunk(payload)
    except PoolError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/incoming")
def list_pool_incoming(request: Request) -> dict:
    items = _pool(request).list_incoming()
    return {"incoming": items, "count": len(items)}


@router.post("/incoming/{chunk_id}/process")
def process_pool_chunk(chunk_id: str, body: ProcessIncomingRequest, request: Request) -> dict:
    pool = _pool(request)
    sign_fn = None
    contributor = body.contributor_address
    if body.wallet_name:
        from artcb.wallet.manager import WalletManager

        try:
            wallet = WalletManager().load_wallet(name=body.wallet_name)
            contributor = contributor or wallet.address
            sign_fn = wallet.sign
        except FileNotFoundError as exc:
            raise HTTPException(status_code=400, detail=f"Wallet introuvable: {body.wallet_name}") from exc
    if not contributor:
        raise HTTPException(status_code=400, detail="contributor_address ou wallet_name requis")
    try:
        return pool.process_incoming_chunk(chunk_id, contributor_address=contributor, sign_fn=sign_fn)
    except PoolError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/incoming/process-all")
def process_all_incoming(body: ProcessIncomingRequest, request: Request) -> dict:
    pool = _pool(request)
    sign_fn = None
    contributor = body.contributor_address
    if body.wallet_name:
        from artcb.wallet.manager import WalletManager

        try:
            wallet = WalletManager().load_wallet(name=body.wallet_name)
            contributor = contributor or wallet.address
            sign_fn = wallet.sign
        except FileNotFoundError as exc:
            raise HTTPException(status_code=400, detail=f"Wallet introuvable: {body.wallet_name}") from exc
    if not contributor:
        raise HTTPException(status_code=400, detail="contributor_address ou wallet_name requis")
    results = pool.process_local_pending(contributor_address=contributor, sign_fn=sign_fn)
    return {"processed": results, "count": len(results)}


@router.post("/jobs/{job_id}/results")
def receive_pool_result(job_id: str, body: PoolResultRequest, request: Request) -> dict:
    try:
        return _pool(request).receive_result(job_id, body.chunk_id, body.result_envelope)
    except PoolError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/jobs/{job_id}/finalize")
def finalize_pool_job(job_id: str, body: FinalizePoolJobRequest, request: Request) -> dict:
    try:
        return _pool(request).finalize_job(job_id, body.full_text)
    except PoolError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
