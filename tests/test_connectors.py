"""Tests connecteurs — stockage local chiffré + API."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from artcb.connectors.manager import ConnectorManager


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("ARTCB_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("ARTCB_LOG_DIR", str(tmp_path / "logs"))
    return TestClient(create_app())


def test_save_and_list_connector_masked(client: TestClient) -> None:
    r = client.post(
        "/api/v1/connectors",
        json={
            "provider": "openai",
            "label": "Mon ChatGPT",
            "api_key": "sk-test-openai-key-12345678",
            "config": {"model": "gpt-4o-mini"},
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["connector"]["provider"] == "openai"
    assert "sk-t" in (body["connector"].get("api_key_masked") or "")
    assert "sk-test-openai-key" not in json.dumps(body)

    listed = client.get("/api/v1/connectors?kind=llm")
    assert listed.status_code == 200
    assert listed.json()["count"] == 1
    assert listed.json()["storage"] == "local_encrypted"


def test_delete_connector(client: TestClient) -> None:
    save = client.post(
        "/api/v1/connectors",
        json={"provider": "anthropic", "label": "Claude", "api_key": "sk-ant-test-key-abcdef12"},
    )
    cid = save.json()["connector"]["connector_id"]
    assert client.delete(f"/api/v1/connectors/{cid}").status_code == 200
    assert client.get("/api/v1/connectors").json()["count"] == 0


def test_save_openrouter_connector(client: TestClient) -> None:
    r = client.post(
        "/api/v1/connectors",
        json={
            "provider": "openrouter",
            "label": "OpenRouter",
            "api_key": "sk-or-test-key-12345678",
            "config": {"model": "anthropic/claude-3.5-haiku"},
        },
    )
    assert r.status_code == 200, r.text
    assert r.json()["connector"]["provider"] == "openrouter"


def test_sqlite_source_learn(tmp_path: Path, client: TestClient) -> None:
    db = tmp_path / "learn.db"
    import sqlite3

    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE docs (id INTEGER PRIMARY KEY, content TEXT)")
    conn.executemany("INSERT INTO docs (content) VALUES (?)", [("Phrase A",), ("Phrase B",)])
    conn.commit()
    conn.close()

    save = client.post(
        "/api/v1/connectors",
        json={
            "provider": "sqlite",
            "label": "Ma base locale",
            "api_key": "not-used-for-sqlite",
            "config": {"database_path": str(db), "table": "docs", "text_column": "content"},
        },
    )
    cid = save.json()["connector"]["connector_id"]
    learn = client.post(
        f"/api/v1/connectors/{cid}/learn",
        json={"connector_id": cid, "use_llm": False, "limit": 10},
    )
    assert learn.status_code == 200, learn.text
    assert learn.json()["node_count"] >= 1
    assert learn.json()["chars_ingested"] > 0


def test_connector_manager_encrypts_on_disk(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARTCB_WALLET_PASSPHRASE", "test-passphrase-artcb-dev-32chars!")
    mgr = ConnectorManager(tmp_path / "data")
    mgr.save_connector(
        provider="openai",
        label="x",
        api_key="sk-test-key-abcdefghijklmnop",
        config={"model": "gpt-4o-mini"},
    )
    raw = (tmp_path / "data" / "connectors" / "connectors.json").read_text()
    assert "sk-test-key" not in raw
    assert "secret_encrypted" in raw
