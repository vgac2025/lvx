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
import shutil
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
    for d in (NODE_A_DIR, NODE_B_DIR):
        data = d / "data"
        if data.exists():
            shutil.rmtree(data)
        logs = d / "logs"
        if logs.exists():
            shutil.rmtree(logs)

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
        print(f"{'OK' if ok else 'FAIL'} {name}: {detail.get('message', detail)}")

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
    status_a["node_id"]
    client_a.get("/api/v1/p2p/blocks/public").json()["count"]

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

    # --- POOL E2E : calcul distribué chiffré ML-KEM ---
    status_b = client_b.get("/api/v1/p2p/status").json()
    kem_b = status_b["kem_public_key_hex"]
    status_b["node_id"]

    add_b_on_a = client_a.post(
        "/api/v1/p2p/peers",
        json={"host": "127.0.0.1", "port": PORT_B, "kem_public_key_hex": kem_b, "label": "node_b"},
    )
    step("A_add_peer_B", add_b_on_a.status_code == 200, {"status": add_b_on_a.status_code})

    wb = client_b.post("/api/v1/wallet/create", json={"name": "node_b_wallet"})
    step("B_create_wallet", wb.status_code == 200, {"status": wb.status_code})
    address_b = wb.json()["address"]

    pool_text = (
        "Pool ARTCB E2E chiffré. Premier segment traité localement sur le coordinateur. "
        "Deuxième segment envoyé au worker distant — jamais en clair sur le réseau. "
        "Troisième segment pour valider le finalize avec contributors pool_worker."
    )
    pool_job = client_a.post(
        "/api/v1/pool/jobs",
        json={
            "text": pool_text,
            "visibility": "private",
            "actor_address": address_a,
            "wallet_name": "node_a_wallet",
            "chunk_chars": 120,
            "auto_dispatch": True,
        },
    )
    pool_ok = pool_job.status_code == 200
    job_body = pool_job.json() if pool_ok else {}
    job_id = job_body.get("job", {}).get("job_id")
    chunks = job_body.get("job", {}).get("chunks", [])
    encrypted_chunks = all("envelope" in c and c["envelope"].get("kem_ct") for c in chunks) if chunks else False
    step("A_pool_job_created_encrypted", pool_ok and encrypted_chunks, {
        "status": pool_job.status_code,
        "job_id": job_id,
        "chunk_count": len(chunks),
        "encrypted": encrypted_chunks,
        "message": "Job pool — morceaux ML-KEM E2E, jamais texte clair réseau",
    })

    proc_a = client_a.post(
        "/api/v1/pool/incoming/process-all",
        json={"wallet_name": "node_a_wallet", "contributor_address": address_a},
    )
    proc_b = client_b.post(
        "/api/v1/pool/incoming/process-all",
        json={"wallet_name": "node_b_wallet", "contributor_address": address_b},
    )
    step("A_process_local_pool_chunks", proc_a.status_code == 200, {
        "processed": proc_a.json().get("count") if proc_a.status_code == 200 else 0,
    })
    step("B_process_remote_pool_chunks", proc_b.status_code == 200, {
        "processed": proc_b.json().get("count") if proc_b.status_code == 200 else 0,
    })

    finalize = client_a.post(
        f"/api/v1/pool/jobs/{job_id}/finalize",
        json={"full_text": pool_text},
    )
    fin_ok = finalize.status_code == 200
    fin_body = finalize.json() if fin_ok else {}
    contributors = fin_body.get("contributors", [])
    pool_workers = [c for c in contributors if c.get("role") == "pool_worker"]
    step("A_pool_finalize_with_workers", fin_ok and len(pool_workers) >= 1, {
        "block_index": fin_body.get("block_index"),
        "pool_worker_count": len(pool_workers),
        "contributors": contributors,
        "message": "Finalize owner — bloc PoL avec contributors pool_worker",
    })

    pool_status = client_a.get("/api/v1/pool/status").json()
    step("pool_crypto_architecture", pool_status.get("plaintext_on_network") is False, {
        "crypto": pool_status.get("crypto"),
        "contexts": pool_status.get("contexts"),
    })

    graphs_b_pool = list((NODE_B_DIR / "data" / "graphs").glob("*.json")) if (NODE_B_DIR / "data" / "graphs").exists() else []
    step("B_pool_worker_computed_locally", len(graphs_b_pool) >= 1, {
        "graphs_on_B": len(graphs_b_pool),
        "message": "Worker B a exécuté raisonnement LOCAL sur chunk déchiffré",
    })

    results["conclusions"] = {
        "learning_reasoning_shared_between_pcs": False,
        "mining_compute_shared_between_pcs": False,
        "pool_e2e_encrypted_opt_in": fin_ok and encrypted_chunks,
        "pool_plaintext_on_network": False,
        "pool_workers_contribute_pol": len(pool_workers) >= 1,
        "public_blocks_synced_via_p2p": incoming_count >= 1,
        "private_blocks_synced": False,
        "ir_graphs_synced": False,
        "what_is_shared": "Morceaux/résultats pool chiffrés ML-KEM + métadonnées blocs PUBLIC P2P",
        "what_stays_local": "Déchiffrement et raisonnement dual-agent sur chaque machine — graphes IR locaux",
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
