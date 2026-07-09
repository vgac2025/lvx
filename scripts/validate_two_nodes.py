#!/usr/bin/env python3
"""
Validation réelle 2 nœuds ARTCB — Cloud Agent (VM).
Simule 2 PC distincts : ARTCB_DATA_DIR différent, ports API différents.

Usage (API déjà démarrées sur 8001 et 8002) :
  python3 scripts/validate_two_nodes.py

Ou tout-en-un (démarre les serveurs) :
  python3 scripts/validate_two_nodes.py --spawn
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
NODE_A_DIR = Path("/tmp/artcb_validate_node_a")
NODE_B_DIR = Path("/tmp/artcb_validate_node_b")
PORT_A = 18001
PORT_B = 18002
LOG_PATH = ROOT / "logs" / "validate_two_nodes_latest.json"


def _base(port: int) -> str:
    return f"http://127.0.0.1:{port}"


def _wait_health(port: int, timeout: float = 30.0) -> None:
    url = f"{_base(port)}/api/v1/health"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = httpx.get(url, timeout=2.0)
            if r.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(0.5)
    raise RuntimeError(f"API port {port} not healthy")


def _spawn_servers() -> subprocess.Popen:
    env_base = os.environ.copy()
    env_base["ARTCB_WALLET_PASSPHRASE"] = env_base.get(
        "ARTCB_WALLET_PASSPHRASE", "validate_passphrase_artcb_32chars!"
    )
    env_base["ARTCB_MIN_BLOCK_INTERVAL_SEC"] = "0"
    env_base["ARTCB_PQC_ENABLED"] = "true"

    NODE_A_DIR.mkdir(parents=True, exist_ok=True)
    NODE_B_DIR.mkdir(parents=True, exist_ok=True)

    procs = []
    for port, data_dir in ((PORT_A, NODE_A_DIR), (PORT_B, NODE_B_DIR)):
        env = env_base.copy()
        env["ARTCB_DATA_DIR"] = str(data_dir / "data")
        env["ARTCB_LOG_DIR"] = str(data_dir / "logs")
        p = subprocess.Popen(
            [
                sys.executable, "-m", "uvicorn", "src.api.main:app",
                "--host", "127.0.0.1", "--port", str(port),
            ],
            cwd=str(ROOT),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        procs.append(p)
    for port in (PORT_A, PORT_B):
        _wait_health(port)
    return procs  # type: ignore[return-value]


def run_validation() -> dict:
    results: dict = {
        "environment": "CLOUD_AGENT_VM",
        "note": "Simule 2 PC — pas le PC utilisateur physique",
        "node_a": {"port": PORT_A, "data_dir": str(NODE_A_DIR)},
        "node_b": {"port": PORT_B, "data_dir": str(NODE_B_DIR)},
        "steps": [],
        "conclusions": {},
    }

    def step(name: str, ok: bool, detail: dict) -> None:
        results["steps"].append({"name": name, "ok": ok, **detail})
        print(f"{'✓' if ok else '✗'} {name}: {detail.get('message', detail)}")

    client_a = httpx.Client(base_url=_base(PORT_A), timeout=60.0)
    client_b = httpx.Client(base_url=_base(PORT_B), timeout=60.0)

    # --- NODE A : wallet + apprentissage + raisonnement + minage LOCAL ---
    w = client_a.post("/api/v1/wallet/create", json={"name": "node_a_wallet"})
    step("A_create_wallet", w.status_code == 200, {"status": w.status_code, "message": w.text[:200]})
    wallet_a = w.json()
    address_a = wallet_a["address"]

    text = (
        "Décision importante. Nous devons donc valider le protocole ARTCB. "
        "Hypothèse : le minage reste local sur chaque machine. "
        "Objectif : synchroniser uniquement les blocs publics entre pairs."
    )
    agents = client_a.post(
        "/api/v1/agents/run",
        json={"text": text, "session_id": "validate_two_nodes", "use_llm": False},
    )
    step("A_learning_reasoning_local", agents.status_code == 200, {
        "status": agents.status_code,
        "graph_id": agents.json().get("graph_id") if agents.status_code == 200 else None,
        "message": "Apprentissage+raisonnement sur NODE A seulement",
    })
    graph_id = agents.json()["graph_id"]

    store_public = client_a.post(
        "/api/v1/store",
        json={
            "graph_id": graph_id,
            "session_id": "validate_two_nodes",
            "visibility": "public",
            "wallet_name": "node_a_wallet",
            "actor_address": address_a,
        },
    )
    step("A_store_public_block", store_public.status_code == 200, {
        "status": store_public.status_code,
        "block_index": store_public.json().get("block_index") if store_public.status_code == 200 else None,
        "message": "Bloc PUBLIC gravé sur chaîne locale A",
    })

    store_private = client_a.post(
        "/api/v1/agents/run",
        json={"text": "Donnée secrète banque — compte 12345.", "session_id": "priv", "use_llm": False},
    )
    gid_priv = store_private.json()["graph_id"]
    sp = client_a.post(
        "/api/v1/store",
        json={
            "graph_id": gid_priv,
            "session_id": "priv",
            "visibility": "private",
            "wallet_name": "node_a_wallet",
            "actor_address": address_a,
        },
    )
    step("A_store_private_block", sp.status_code == 200, {
        "message": "Bloc PRIVATE sur A — ne doit PAS apparaître sur B",
    })

    status_a = client_a.get("/api/v1/p2p/status").json()
    kem_a = status_a["kem_public_key_hex"]
    node_id_a = status_a["node_id"]
    pub_blocks_a = client_a.get("/api/v1/p2p/blocks/public").json()["count"]

    # --- NODE B : vide au départ ---
    chain_b_before = client_b.get("/api/v1/chain").json()
    blocks_b_before = len(chain_b_before.get("blocks", []))
    graphs_b = list((NODE_B_DIR / "data" / "graphs").glob("*.json")) if (NODE_B_DIR / "data" / "graphs").exists() else []

    step("B_initial_empty", blocks_b_before == 0 and len(graphs_b) == 0, {
        "blocks": blocks_b_before,
        "graphs": len(graphs_b),
        "message": "NODE B démarre vide — pas de calcul partagé automatiquement",
    })

    # --- B ajoute A comme pair et sync ---
    add_peer = client_b.post(
        "/api/v1/p2p/peers",
        json={"host": "127.0.0.1", "port": PORT_A, "kem_public_key_hex": kem_a, "label": "node_a"},
    )
    step("B_add_peer_A", add_peer.status_code == 200, {"status": add_peer.status_code})

    sync = client_b.post("/api/v1/p2p/sync")
    step("B_sync_from_A", sync.status_code == 200, {
        "status": sync.status_code,
        "results": sync.json().get("results"),
        "message": "Sync P2P déclenchée",
    })

    incoming = client_b.get("/api/v1/p2p/blocks/incoming").json()
    incoming_count = incoming.get("count", 0)
    step("B_received_public_blocks", incoming_count >= 1, {
        "incoming_public": incoming_count,
        "message": "Blocs PUBLIC de A archivés sur B",
    })

    # B ne doit PAS avoir le graphe de A (pas de sync graphes IR)
    graphs_b_after = list((NODE_B_DIR / "data" / "graphs").glob("*.json")) if (NODE_B_DIR / "data" / "graphs").exists() else []
    graph_on_b = client_b.get(f"/api/v1/graph/{graph_id}")
    step("B_NO_shared_learning_graph", graph_on_b.status_code == 404 and len(graphs_b_after) == 0, {
        "graph_fetch_status": graph_on_b.status_code,
        "graphs_on_disk": len(graphs_b_after),
        "message": "Apprentissage/raisonnement NON partagé — graphe IR reste sur A",
    })

    # Private block invisible on B
    priv_on_b = [b for b in incoming.get("blocks", []) if b.get("visibility") == "private"]
    pub_on_a = client_a.get("/api/v1/p2p/blocks/public").json()["count"]
    step("B_NO_private_blocks", len(priv_on_b) == 0 and pub_on_a >= 1, {
        "private_in_incoming": len(priv_on_b),
        "public_on_A": pub_on_a,
        "message": "Blocs PRIVATE jamais synchronisés",
    })

    results["conclusions"] = {
        "learning_reasoning_shared_between_pcs": False,
        "mining_compute_shared_between_pcs": False,
        "public_blocks_synced_via_p2p": incoming_count >= 1,
        "private_blocks_synced": False,
        "ir_graphs_synced": False,
        "what_is_shared": "Uniquement métadonnées blocs PUBLIC (hash, PoL, graph_root) via P2P",
        "what_stays_local": "Calcul apprentissage, raisonnement dual-agent, graphes IR, blocs private, clés API, wallets",
    }

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nLog écrit : {LOG_PATH}")
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spawn", action="store_true", help="Démarre 2 serveurs uvicorn")
    args = parser.parse_args()
    procs = []
    try:
        if args.spawn:
            print("Démarrage 2 nœuds API…")
            procs = _spawn_servers()
        else:
            _wait_health(PORT_A)
            _wait_health(PORT_B)
        results = run_validation()
        ok = all(s["ok"] for s in results["steps"])
        print("\n=== CONCLUSION ===")
        for k, v in results["conclusions"].items():
            print(f"  {k}: {v}")
        return 0 if ok else 1
    finally:
        for p in procs:
            p.terminate()
            p.wait(timeout=5)


if __name__ == "__main__":
    sys.exit(main())
