"""Pool calcul distribué E2E — ML-KEM chiffrement morceaux et résultats."""

from src.artcb.pool.discovery import build_peer_urls, discover_workers
from src.artcb.pool.e2e import (
    decrypt_chunk_payload,
    decrypt_result_payload,
    encrypt_chunk_payload,
    encrypt_result_payload,
)
from src.artcb.pool.orchestrator import run_distributed_pool, run_local_mining, run_mining_with_options
from src.artcb.pool.policy import PoolPolicyError, validate_pool_options
from src.artcb.pool.preferences import PoolPreferences, PoolPreferencesStore
from src.artcb.pool.service import PoolChunk, PoolError, PoolJob, PoolService, split_text_chunks

__all__ = [
    "PoolChunk",
    "PoolError",
    "PoolJob",
    "PoolPreferences",
    "PoolPreferencesStore",
    "PoolPolicyError",
    "PoolService",
    "build_peer_urls",
    "decrypt_chunk_payload",
    "decrypt_result_payload",
    "discover_workers",
    "encrypt_chunk_payload",
    "encrypt_result_payload",
    "run_distributed_pool",
    "run_local_mining",
    "run_mining_with_options",
    "split_text_chunks",
    "validate_pool_options",
]
