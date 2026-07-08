"""Mining REST routes — pipeline apprentissage + raisonnement + PoL collectif."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from artcb.connectors.sources import DataSourceError
from artcb.mining.pipeline import MiningPipeline

logger = logging.getLogger("artcb.api.mining")
router = APIRouter(prefix="/api/v1/mining", tags=["mining"])


class MiningPipelineRequest(BaseModel):
    text: str | None = Field(default=None, min_length=1)
    connector_id: str | None = None
    session_id: str = "mining_session"
    use_llm: bool = False
    llm_provider: str | None = None
    actor_address: str | None = None
    wallet_name: str | None = None
    visibility: str = "private"
    group_id: str | None = None
    store_block: bool = True
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    batch_index: int = 0


class BulkMiningRequest(BaseModel):
    connector_id: str
    max_batches: int = Field(default=10, ge=1, le=1000)
    batch_size: int = Field(default=100, ge=1, le=1000)
    actor_address: str | None = None
    wallet_name: str | None = None
    visibility: str = "private"
    group_id: str | None = None
    use_llm: bool = False
    llm_provider: str | None = None


def _state(request: Request):
    return request.app.state.artcb


def _pipeline(request: Request) -> MiningPipeline:
    state = _state(request)
    from artcb.wallet.manager import WalletManager

    return MiningPipeline(
        dual=state.dual,
        chain=state.chain,
        wallet_manager=WalletManager(),
        connectors=state.connectors,
        groups=state.groups,
        timeline=state.timeline,
        register_graph=state.register_graph,
    )


@router.post("/pipeline")
def run_mining_pipeline(body: MiningPipelineRequest, request: Request) -> dict:
    """
    Pipeline unifié : source d'apprentissage → raisonnement (dual-agent) → minage PoL.

    Les deux types de minage sont connectés :
    - **Apprentissage** : ingestion texte / base client
    - **Raisonnement** : Explorateur + Critique + score PoL
    - **Minage** : bloc + reward collectif ``contributors[]``
    """
    pipeline = _pipeline(request)
    try:
        if body.connector_id:
            result = pipeline.run_from_connector(
                body.connector_id,
                limit=body.limit,
                offset=body.offset,
                batch_index=body.batch_index,
                session_id=body.session_id,
                use_llm=body.use_llm,
                llm_provider=body.llm_provider,
                actor_address=body.actor_address,
                wallet_name=body.wallet_name,
                visibility=body.visibility,
                group_id=body.group_id,
                store_block=body.store_block,
            )
        elif body.text:
            result = pipeline.run_from_text(
                body.text,
                session_id=body.session_id,
                use_llm=body.use_llm,
                llm_provider=body.llm_provider,
                actor_address=body.actor_address,
                wallet_name=body.wallet_name,
                visibility=body.visibility,
                group_id=body.group_id,
                store_block=body.store_block,
            )
        else:
            raise HTTPException(status_code=422, detail="text or connector_id required")
    except (DataSourceError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "graph_id": result.graph_id,
        "node_count": result.node_count,
        "pol_score": result.pol_score,
        "block_index": result.block_index,
        "block_hash": result.block_hash,
        "block_reward": result.block_reward,
        "contributors": result.contributors,
        "phases": result.phases,
        "message": result.message,
    }


@router.post("/bulk")
def run_bulk_mining(body: BulkMiningRequest, request: Request) -> dict:
    """
  Minage par lots — banque / grosses bases : lit batch par batch, raisonne et mine chaque lot.
    """
    pipeline = _pipeline(request)
    results = []
    offset = 0
    for batch_i in range(body.max_batches):
        try:
            result = pipeline.run_from_connector(
                body.connector_id,
                limit=body.batch_size,
                offset=offset,
                batch_index=batch_i,
                use_llm=body.use_llm,
                llm_provider=body.llm_provider,
                actor_address=body.actor_address,
                wallet_name=body.wallet_name,
                visibility=body.visibility,
                group_id=body.group_id,
                store_block=True,
            )
        except DataSourceError as exc:
            if batch_i == 0:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            break

        row_count = result.phases.get("learning", {}).get("chars", 0)
        results.append({
            "batch": batch_i,
            "offset": offset,
            "graph_id": result.graph_id,
            "pol_score": result.pol_score,
            "block_index": result.block_index,
            "block_reward": result.block_reward,
            "chars": row_count,
        })

        if result.block_index is None:
            break

        offset += body.batch_size

        record = _state(request).connectors.get_connector(body.connector_id)
        if not record:
            break
        from artcb.connectors.sources import fetch_learning_text_batched

        probe = fetch_learning_text_batched(record, limit=1, offset=offset)
        if not probe.has_more and probe.row_count == 0:
            break

    return {
        "batches_processed": len(results),
        "results": results,
        "message": f"Minage bulk terminé — {len(results)} lots traités (apprentissage + raisonnement + blocs)",
    }
