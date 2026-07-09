"""Tests Explorateur — propositions symboles actives."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from artcb.agents.explorer import ExplorerAgent
from artcb.ir.symbol_store import PersistentSymbolRegistry


def test_explorer_proposes_symbols(tmp_path: Path) -> None:
    store = PersistentSymbolRegistry(tmp_path)
    explorer = ExplorerAgent(symbol_registry=store)
    proposals = explorer.propose_symbols("The flarnick mechanism requires observation.")
    assert len(proposals) >= 1
    concepts = [p.concept for p in proposals]
    assert "flarnick" in concepts or "mechanism" in concepts


def test_explorer_result_includes_proposals(tmp_path: Path) -> None:
    store = PersistentSymbolRegistry(tmp_path)
    explorer = ExplorerAgent(symbol_registry=store)
    result = explorer.explore("We analyze the zorbax today.")
    assert result.graph.orig_symbols
    assert isinstance(result.symbol_proposals, list)


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("ARTCB_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("ARTCB_LOG_DIR", str(tmp_path / "logs"))
    return TestClient(create_app())


def test_agents_run_returns_symbol_proposals(client: TestClient) -> None:
    r = client.post(
        "/api/v1/agents/run",
        json={"text": "The flarnick process needs validation.", "session_id": "sym_test"},
    )
    assert r.status_code == 200
    body = r.json()
    assert "symbol_proposals" in body
    assert "orig_symbols" in body


def test_symbols_registry_api(client: TestClient) -> None:
    client.post(
        "/api/v1/agents/run",
        json={"text": "Novel term xyzzyplughere appears.", "session_id": "reg_test"},
    )
    r = client.get("/api/v1/symbols/registry")
    assert r.status_code == 200
    assert r.json()["count"] >= 0
