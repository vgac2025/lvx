"""Tests pool calcul distribué E2E — ML-KEM chiffrement morceaux/résultats."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from artcb.crypto.kem import generate_kem_keypair
from artcb.pool.e2e import (
    decrypt_chunk_payload,
    decrypt_result_payload,
    encrypt_chunk_payload,
    encrypt_result_payload,
)
from artcb.pool.service import PoolService


def test_pool_chunk_crypto_roundtrip() -> None:
    sk, pk = generate_kem_keypair()
    text = "Fragment secret pour raisonnement local worker."
    envelope = encrypt_chunk_payload(text, pk.hex())
    assert decrypt_chunk_payload(envelope, sk.hex()) == text


def test_pool_result_crypto_roundtrip() -> None:
    sk_owner, pk_owner = generate_kem_keypair()
    result = {
        "chunk_id": "chk_abc",
        "pol_score": 0.82,
        "graph_id": "g_test",
        "contributor_address": "artcb1worker",
    }
    envelope = encrypt_result_payload(result, pk_owner.hex())
    decrypted = decrypt_result_payload(envelope, sk_owner.hex())
    assert decrypted["chunk_id"] == "chk_abc"
    assert decrypted["pol_score"] == 0.82


def test_pool_service_local_job_finalize(tmp_path: Path) -> None:
    sk_owner, pk_owner = generate_kem_keypair()
    sk_worker, pk_worker = generate_kem_keypair()

    def run_reasoning(text: str) -> dict[str, Any]:
        return {
            "graph_id": f"g_{hash(text) % 10000}",
            "pol_score": 0.75,
            "graph_root": "abc123",
            "node_count": 3,
        }

    finalized: list[dict] = []

    def finalize(job, full_text: str, extra: list[dict]) -> dict[str, Any]:
        finalized.append({"text_len": len(full_text), "extra": extra})
        return {"graph_id": "g_final", "block_index": 1, "contributors": extra}

    owner = PoolService(
        tmp_path,
        node_id="node_owner",
        kem_public_hex=pk_owner.hex(),
        kem_secret_hex=sk_owner.hex(),
        run_reasoning=run_reasoning,
        finalize_job=finalize,
    )
    worker = PoolService(
        tmp_path / "worker",
        node_id="node_worker",
        kem_public_hex=pk_worker.hex(),
        kem_secret_hex=sk_worker.hex(),
        run_reasoning=run_reasoning,
    )

    text = "Phrase unique pour worker distant."
    job = owner.create_job(
        text,
        visibility="private",
        workers=[{
            "node_id": "node_worker",
            "kem_public_hex": pk_worker.hex(),
            "base_url": "http://worker.local",
        }],
        chunk_chars=400,
    )
    assert len(job.chunks) == 1
    assert "kem_ct" in job.chunks[0].envelope

    peer_urls = {"node_owner": "http://owner.local", "node_worker": "http://worker.local"}
    # Simule réception worker (dispatch HTTP non exécuté en test unitaire)
    chunk = job.chunks[0]
    worker.receive_incoming_chunk({
        "job_id": job.job_id,
        "owner_node_id": "node_owner",
        "owner_kem_public_hex": pk_owner.hex(),
        "owner_callback_base": peer_urls["node_owner"],
        "visibility": "private",
        **chunk.to_dict(),
    })

    incoming = worker.list_incoming()
    assert len(incoming) >= 1
    chunk_id = incoming[0]["chunk_id"]

    # Simule callback owner sans HTTP
    item = incoming[0]
    plain = decrypt_chunk_payload(item["envelope"], sk_worker.hex())
    reasoning = run_reasoning(plain)
    result_env = encrypt_result_payload({
        "chunk_id": chunk_id,
        "job_id": job.job_id,
        "worker_node_id": "node_worker",
        "graph_id": reasoning["graph_id"],
        "pol_score": reasoning["pol_score"],
        "graph_root": reasoning["graph_root"],
        "node_count": reasoning["node_count"],
        "contributor_address": "artcb1worker",
        "signature": "",
    }, pk_owner.hex())
    owner.receive_result(job.job_id, chunk_id, result_env)

    out = owner.finalize_job(job.job_id, text)
    assert out["graph_id"] == "g_final"
    assert finalized[0]["extra"][0]["role"] == "pool_worker"


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("ARTCB_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("ARTCB_LOG_DIR", str(tmp_path / "logs"))
    monkeypatch.setenv("ARTCB_MIN_BLOCK_INTERVAL_SEC", "0")
    return TestClient(create_app())


def test_pool_api_status(client: TestClient) -> None:
    r = client.get("/api/v1/pool/status")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["crypto"] == "ML-KEM-768"
    assert body["plaintext_on_network"] is False


def test_pool_api_create_job_local(client: TestClient) -> None:
    status = client.get("/api/v1/p2p/status").json()
    r = client.post(
        "/api/v1/pool/jobs",
        json={
            "text": "Texte de test pool chiffré E2E pour validation.",
            "visibility": "private",
            "workers": [{
                "node_id": status["node_id"],
                "kem_public_hex": status["kem_public_key_hex"],
                "base_url": "http://testserver",
            }],
            "auto_dispatch": False,
        },
    )
    assert r.status_code == 200, r.text
    job = r.json()["job"]
    assert job["chunks"][0]["envelope"]["kem_alg"] == "ML-KEM-768"
    assert "ciphertext" in job["chunks"][0]["envelope"]
