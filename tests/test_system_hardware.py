"""Tests detection materielle et profil d'optimisation."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from artcb.system.hardware import detect_hardware, live_metrics
from artcb.system.optimizer import build_optimization_profile, default_pool_chunk_chars


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("ARTCB_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("ARTCB_LOG_DIR", str(tmp_path / "logs"))
    app = create_app()
    return TestClient(app)


def test_detect_hardware_returns_sane_values():
    hw = detect_hardware()
    d = hw.to_dict()
    assert d["cpu"]["logical_cores"] >= 1
    assert d["memory"]["total_gb"] > 0
    assert d["disk"]["total_gb"] > 0
    assert "system" not in d
    assert isinstance(d["gpus"], list)


def test_live_metrics_structure():
    m = live_metrics()
    assert "cpu" in m and "percent" in m["cpu"]
    assert "memory" in m and "percent" in m["memory"]
    assert "network" in m


def test_optimization_profile_defaults():
    hw = detect_hardware()
    opt = build_optimization_profile(hw)
    d = opt.to_dict()
    assert 1 <= d["agent_pool_workers"] <= 8
    assert 100 <= d["pool_chunk_chars"] <= 8000
    assert d["use_numpy_pol"] is True
    assert "optimizations_active" in d
    assert len(d["optimizations_active"]) >= 4


def test_default_pool_chunk_chars():
    chunk = default_pool_chunk_chars()
    assert 100 <= chunk <= 8000


def test_metrics_api_includes_hardware(client):
    r = client.get("/api/v1/metrics")
    assert r.status_code == 200
    body = r.json()
    assert "hardware" in body
    assert "optimization" in body
    assert body["hardware"]["cpu"]["logical_cores"] >= 1


def test_system_hardware_endpoint(client):
    r = client.get("/api/v1/system/hardware")
    assert r.status_code == 200
    assert "cpu" in r.json()


def test_system_optimization_endpoint(client):
    r = client.get("/api/v1/system/optimization")
    assert r.status_code == 200
    assert "pool_chunk_chars" in r.json()
