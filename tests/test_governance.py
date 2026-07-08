"""Governance vote API tests — GOUVERNANCE_ARTCB.md §3."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from artcb.wallet.manager import WalletManager


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("ARTCB_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("ARTCB_LOG_DIR", str(tmp_path / "logs"))
    return TestClient(create_app())


@pytest.fixture
def voter_wallet(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ARTCB_DATA_DIR", str(tmp_path / "data"))
    wm = WalletManager()
    return wm.create_wallet(name="voter")


def test_create_proposal(client: TestClient) -> None:
    r = client.post(
        "/api/v1/governance/proposals",
        json={
            "title": "Mise à jour tokenomics",
            "description": "Changement halving interval",
            "version": "0.4.0",
            "proposal_id": "GOV-2026-07-08-001",
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["proposal"]["proposal_id"] == "GOV-2026-07-08-001"
    assert body["proposal"]["status"] == "open"


def test_cast_vote_yes(client: TestClient, voter_wallet) -> None:
    client.post(
        "/api/v1/governance/proposals",
        json={
            "title": "Test vote",
            "description": "desc",
            "version": "0.3.1",
            "proposal_id": "GOV-2026-07-08-002",
        },
    )
    r = client.post(
        "/api/v1/governance/vote",
        json={
            "proposal_id": "GOV-2026-07-08-002",
            "wallet_address": voter_wallet.address,
            "choice": "yes",
        },
    )
    assert r.status_code == 200, r.text
    assert r.json()["tally"]["yes"] == 1
    assert r.json()["requires_rollback"] is False


def test_duplicate_vote_rejected(client: TestClient, voter_wallet) -> None:
    client.post(
        "/api/v1/governance/proposals",
        json={
            "title": "Dup vote",
            "description": "desc",
            "version": "0.3.2",
            "proposal_id": "GOV-2026-07-08-003",
        },
    )
    payload = {
        "proposal_id": "GOV-2026-07-08-003",
        "wallet_address": voter_wallet.address,
        "choice": "no",
    }
    assert client.post("/api/v1/governance/vote", json=payload).status_code == 200
    r = client.post("/api/v1/governance/vote", json=payload)
    assert r.status_code == 400


def test_list_proposals(client: TestClient) -> None:
    client.post(
        "/api/v1/governance/proposals",
        json={
            "title": "List test",
            "description": "desc",
            "version": "0.3.3",
            "proposal_id": "GOV-2026-07-08-004",
        },
    )
    r = client.get("/api/v1/governance/proposals")
    assert r.status_code == 200
    assert r.json()["count"] >= 1
