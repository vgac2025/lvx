"""Group management API tests — GROUPES_RESEAUX_ARTCB v1.1."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import create_app

FOUNDER = "artcb1founder00000000000000000000000001"
ADMIN = "artcb1admin00000000000000000000000000001"
MEMBER = "artcb1member000000000000000000000000001"
OTHER = "artcb1other00000000000000000000000000001"


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("ARTCB_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("ARTCB_LOG_DIR", str(tmp_path / "logs"))
    app = create_app()
    return TestClient(app)


def _create_group(client: TestClient, name: str = "Projet LVX") -> str:
    r = client.post(
        "/api/v1/groups",
        json={"name": name, "founder_address": FOUNDER},
    )
    assert r.status_code == 200
    return r.json()["group_id"]


def test_create_group(client: TestClient) -> None:
    group_id = _create_group(client)
    r = client.get(f"/api/v1/groups/{group_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["founder_address"] == FOUNDER
    assert data["members"][0]["role"] == "founder"
    assert data["dissolved"] is False


def test_founder_cannot_be_removed_by_admin(client: TestClient) -> None:
    group_id = _create_group(client)
    client.post(
        f"/api/v1/groups/{group_id}/members",
        json={"actor_address": FOUNDER, "address": ADMIN, "role": "admin"},
    )
    client.post(
        f"/api/v1/groups/{group_id}/members/{ADMIN}/role",
        json={"actor_address": FOUNDER, "role": "admin"},
    )
    r = client.delete(
        f"/api/v1/groups/{group_id}/members/{FOUNDER}",
        params={"actor_address": ADMIN},
    )
    assert r.status_code == 403
    assert r.json()["detail"]["code"] == "FOUNDER_IMMUTABLE"


def test_only_founder_promotes_admin(client: TestClient) -> None:
    group_id = _create_group(client)
    client.post(
        f"/api/v1/groups/{group_id}/members",
        json={"actor_address": FOUNDER, "address": MEMBER, "role": "contributor"},
    )
    r = client.post(
        f"/api/v1/groups/{group_id}/members/{MEMBER}/role",
        json={"actor_address": FOUNDER, "role": "admin"},
    )
    assert r.status_code == 200
    roles = {m["address"]: m["role"] for m in r.json()["members"]}
    assert roles[MEMBER] == "admin"


def test_admin_cannot_promote_admin(client: TestClient) -> None:
    group_id = _create_group(client)
    client.post(
        f"/api/v1/groups/{group_id}/members",
        json={"actor_address": FOUNDER, "address": ADMIN, "role": "admin"},
    )
    client.post(
        f"/api/v1/groups/{group_id}/members",
        json={"actor_address": FOUNDER, "address": MEMBER, "role": "contributor"},
    )
    r = client.post(
        f"/api/v1/groups/{group_id}/members/{MEMBER}/role",
        json={"actor_address": ADMIN, "role": "admin"},
    )
    assert r.status_code == 403


def test_dissolve_group_founder_only(client: TestClient) -> None:
    group_id = _create_group(client)
    client.post(
        f"/api/v1/groups/{group_id}/members",
        json={"actor_address": FOUNDER, "address": ADMIN, "role": "admin"},
    )
    r_admin = client.post(
        f"/api/v1/groups/{group_id}/dissolve",
        json={"actor_address": ADMIN, "confirm": "DISSOLVE"},
    )
    assert r_admin.status_code == 403

    r_founder = client.post(
        f"/api/v1/groups/{group_id}/dissolve",
        json={"actor_address": FOUNDER, "confirm": "DISSOLVE"},
    )
    assert r_founder.status_code == 200
    assert r_founder.json()["dissolved"] is True


def test_groups_api_create_list(client: TestClient) -> None:
    group_id = _create_group(client)
    client.post(
        f"/api/v1/groups/{group_id}/members",
        json={"actor_address": FOUNDER, "address": MEMBER, "role": "contributor"},
    )
    r = client.get("/api/v1/groups", params={"address": MEMBER})
    assert r.status_code == 200
    assert r.json()["count"] == 1
    assert r.json()["groups"][0]["group_id"] == group_id


def test_store_group_visibility_and_chain_filter(client: TestClient) -> None:
    group_id = _create_group(client)
    text = "Groupe test mémorisation bloc scoped."
    enc = client.post("/api/v1/encode", json={"text": text})
    assert enc.status_code == 200
    graph_id = enc.json()["graph_id"]

    r_bad = client.post(
        "/api/v1/store",
        json={
            "graph_id": graph_id,
            "visibility": "group",
            "group_id": group_id,
            "actor_address": OTHER,
        },
    )
    assert r_bad.status_code == 403

    r_ok = client.post(
        "/api/v1/store",
        json={
            "graph_id": graph_id,
            "visibility": "group",
            "group_id": group_id,
            "actor_address": FOUNDER,
        },
    )
    assert r_ok.status_code == 200
    assert r_ok.json()["group_id"] == group_id
    assert r_ok.json()["visibility"] == "group"

    chain_all = client.get("/api/v1/chain")
    chain_group = client.get("/api/v1/chain", params={"group_id": group_id})
    assert chain_all.json()["count"] >= 1
    assert chain_group.json()["count"] == 1
    assert chain_group.json()["blocks"][0]["group_id"] == group_id
