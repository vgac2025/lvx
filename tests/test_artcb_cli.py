"""Tests CLI artcb_cli.py — intégration API."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from threading import Thread

import httpx
import pytest
import uvicorn

from api.main import create_app

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "artcb_cli.py"


@pytest.fixture
def api_port(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> int:
    monkeypatch.setenv("ARTCB_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("ARTCB_LOG_DIR", str(tmp_path / "logs"))
    monkeypatch.setenv("ARTCB_MIN_BLOCK_INTERVAL_SEC", "0")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    app = create_app()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)
    thread = Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(50):
        try:
            if httpx.get(f"http://127.0.0.1:{port}/api/v1/health", timeout=1).status_code == 200:
                return port
        except Exception:
            pass
        time.sleep(0.1)
    pytest.skip("API server did not start in time")


def _run_cli(*args: str, port: int) -> subprocess.CompletedProcess:
    env = {**os.environ, "ARTCB_API_BASE": f"http://127.0.0.1:{port}"}
    return subprocess.run(
        [sys.executable, str(CLI), "--base", f"http://127.0.0.1:{port}", *args],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(ROOT),
        timeout=60,
    )


def test_cli_help_exits_zero() -> None:
    r = subprocess.run([sys.executable, str(CLI), "--help"], capture_output=True, text=True)
    assert r.returncode == 0
    assert "pool" in r.stdout


def test_cli_health(api_port: int) -> None:
    r = _run_cli("health", port=api_port)
    assert r.returncode == 0, r.stderr
    assert "ok" in r.stdout.lower() or "status" in r.stdout.lower()


def test_cli_wallet_and_pool_status(api_port: int) -> None:
    w = _run_cli("wallet", "create", "--name", "cli_test", port=api_port)
    assert w.returncode == 0, w.stderr
    s = _run_cli("pool", "status", port=api_port)
    assert s.returncode == 0, s.stderr
    assert "ML-KEM" in s.stdout


def test_cli_p2p_status(api_port: int) -> None:
    r = _run_cli("p2p", "status", port=api_port)
    assert r.returncode == 0, r.stderr
    assert "kem" in r.stdout.lower()


def test_cli_mining_local(api_port: int) -> None:
    _run_cli("wallet", "create", "--name", "mine_cli", port=api_port)
    r = _run_cli(
        "mining", "pipeline",
        "--text", "CLI minage local ARTCB test intégration bout en bout.",
        "--visibility", "private",
        "--wallet", "mine_cli",
        port=api_port,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert "local" in r.stdout.lower() or "graph_id" in r.stdout.lower()
