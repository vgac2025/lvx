"""Tests notifications API."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from api.main import create_app


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("ARTCB_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("ARTCB_LOG_DIR", str(tmp_path / "logs"))
    return TestClient(create_app())


def test_save_telegram_channel(client: TestClient) -> None:
    r = client.post(
        "/api/v1/notifications/channels",
        json={
            "channel_type": "telegram",
            "label": "Mon bot",
            "secret": "1234567890:telegram-bot-token-test",
            "config": {"chat_id": "12345"},
        },
    )
    assert r.status_code == 200, r.text
    listed = client.get("/api/v1/notifications/channels")
    assert listed.json()["count"] == 1
    assert listed.json()["supported"] == ["telegram"]


def test_gmail_rejected(client: TestClient) -> None:
    r = client.post(
        "/api/v1/notifications/channels",
        json={
            "channel_type": "gmail",
            "label": "mail",
            "secret": "password12345678",
            "config": {"email": "a@b.com"},
        },
    )
    assert r.status_code == 422


@patch("artcb.notifications.manager.httpx.Client")
def test_send_telegram_mock(mock_client_cls: MagicMock, client: TestClient) -> None:
    save = client.post(
        "/api/v1/notifications/channels",
        json={
            "channel_type": "telegram",
            "label": "bot",
            "secret": "1234567890:telegram-bot-token-test",
            "config": {"chat_id": "99"},
        },
    )
    assert save.status_code == 200
    cid = client.get("/api/v1/notifications/channels").json()["channels"][0]["channel_id"]
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"ok": True, "result": {"message_id": 1}}
    mock_resp.raise_for_status = MagicMock()
    mock_client_cls.return_value.__enter__.return_value.post.return_value = mock_resp

    r2 = client.post(
        "/api/v1/notifications/send",
        json={"channel_id": cid, "subject": "T", "body": "Hello ARTCB"},
    )
    assert r2.status_code == 200, r2.text
    assert r2.json()["provider"] == "telegram"
