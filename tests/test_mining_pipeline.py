"""Tests pipeline minage — apprentissage + raisonnement connectés."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from artcb.chain.manager import ChainManager
from artcb.mining.pipeline import MiningPipeline, build_contributors
from artcb.wallet.manager import WalletManager


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("ARTCB_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("ARTCB_LOG_DIR", str(tmp_path / "logs"))
    return TestClient(create_app())


def test_build_contributors_with_wallet(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARTCB_WALLET_PASSPHRASE", "test-passphrase-artcb-dev-32chars!")
    wm = WalletManager(wallet_dir=tmp_path)
    wallet = wm.create_wallet(name="miner")
    contributors = build_contributors(
        actor_address=wallet.address,
        pol_score=0.85,
        wallet=wallet,
        graph_root="abc123" * 8,
    )
    assert len(contributors) == 1
    assert contributors[0]["role"] == "reasoner"
    assert contributors[0]["pol_score"] == 0.85
    assert len(contributors[0]["signature"]) > 0


def test_store_with_actor_creates_contributors(client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARTCB_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("ARTCB_WALLET_PASSPHRASE", "test-passphrase-artcb-dev-32chars!")
    wm = WalletManager()
    wallet = wm.create_wallet(name="store_miner")

    agents = client.post(
        "/api/v1/agents/run",
        json={"text": "Le roi de l'inconnu apprend la mémoire persistante des agents IA.", "session_id": "t1"},
    )
    assert agents.status_code == 200, agents.text
    graph_id = agents.json()["graph_id"]

    store = client.post(
        "/api/v1/store",
        json={
            "graph_id": graph_id,
            "actor_address": wallet.address,
            "wallet_name": "store_miner",
            "visibility": "private",
        },
    )
    assert store.status_code == 200, store.text
    body = store.json()
    assert body["contributors"]
    assert body["contributors"][0]["address"] == wallet.address
    assert body["contributors"][0]["reward_satoshi"] > 0
    assert body["block_reward"] > 0


def test_mining_pipeline_sqlite_source(client: TestClient, tmp_path: Path) -> None:
    db = tmp_path / "bank.db"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE transactions (id INTEGER PRIMARY KEY, content TEXT)")
    for i in range(5):
        conn.execute("INSERT INTO transactions (content) VALUES (?)", (f"Transaction bancaire {i} privée",))
    conn.commit()
    conn.close()

    monkeypatch_pass = pytest.MonkeyPatch()
    monkeypatch_pass.setenv("ARTCB_WALLET_PASSPHRASE", "test-passphrase-artcb-dev-32chars!")
    monkeypatch_pass.setenv("ARTCB_DATA_DIR", str(tmp_path / "data"))
    monkeypatch_pass.setenv("ARTCB_LOG_DIR", str(tmp_path / "logs"))

    wm = WalletManager()
    wallet = wm.create_wallet(name="bank_miner")

    save = client.post(
        "/api/v1/connectors",
        json={
            "provider": "sqlite",
            "label": "Banque transactions",
            "api_key": "local-sqlite-key",
            "config": {"database_path": str(db), "table": "transactions", "text_column": "content"},
        },
    )
    cid = save.json()["connector"]["connector_id"]

    pipeline = client.post(
        "/api/v1/mining/pipeline",
        json={
            "connector_id": cid,
            "actor_address": wallet.address,
            "wallet_name": "bank_miner",
            "visibility": "private",
            "limit": 5,
        },
    )
    assert pipeline.status_code == 200, pipeline.text
    data = pipeline.json()
    assert data["phases"]["reasoning"]["pol_score"] >= 0.6
    assert data["block_index"] is not None
    assert data["contributors"]
    assert data["phases"]["learning"] is not None
    monkeypatch_pass.undo()


def test_bulk_mining_batches(client: TestClient, tmp_path: Path) -> None:
    db = tmp_path / "bulk.db"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE docs (id INTEGER PRIMARY KEY, content TEXT)")
    for i in range(12):
        conn.execute("INSERT INTO docs (content) VALUES (?)", (f"Document {i} pour apprentissage batch",))
    conn.commit()
    conn.close()

    mp = pytest.MonkeyPatch()
    mp.setenv("ARTCB_WALLET_PASSPHRASE", "test-passphrase-artcb-dev-32chars!")
    mp.setenv("ARTCB_DATA_DIR", str(tmp_path / "data2"))
    mp.setenv("ARTCB_LOG_DIR", str(tmp_path / "logs2"))
    c = TestClient(create_app())

    wm = WalletManager()
    wallet = wm.create_wallet(name="bulk")

    save = c.post(
        "/api/v1/connectors",
        json={
            "provider": "sqlite",
            "label": "bulk",
            "api_key": "local-key-bulk",
            "config": {"database_path": str(db), "table": "docs", "text_column": "content"},
        },
    )
    cid = save.json()["connector"]["connector_id"]

    bulk = c.post(
        "/api/v1/mining/bulk",
        json={
            "connector_id": cid,
            "max_batches": 3,
            "batch_size": 5,
            "actor_address": wallet.address,
            "wallet_name": "bulk",
        },
    )
    assert bulk.status_code == 200, bulk.text
    assert bulk.json()["batches_processed"] >= 2
    mp.undo()
