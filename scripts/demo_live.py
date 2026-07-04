#!/usr/bin/env python3
"""ARTCB live demo — 9 steps via real HTTP only (no browser, no frontend).

Requires: `make api` on port 8000. Writes logs/demo_live_latest.txt + JSON.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

BASE = os.getenv("ARTCB_API_BASE", "http://127.0.0.1:8000/api/v1")
LOG_DIR = Path(os.getenv("ARTCB_LOG_DIR", "./logs"))
SESSION = f"demo_live_{datetime.now(timezone.utc).strftime('%H%M%S')}"
OUT_TXT = LOG_DIR / "demo_live_latest.txt"
OUT_JSON = LOG_DIR / f"demo_live_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"


def log(msg: str) -> None:
    print(msg)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with OUT_TXT.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")


def main() -> int:
    results: dict = {"session_id": SESSION, "steps": {}, "ok": True}
    OUT_TXT.write_text(f"=== ARTCB Live Demo {datetime.now(timezone.utc).isoformat()} ===\n", encoding="utf-8")

    with httpx.Client(base_url=BASE, timeout=60.0) as client:
        try:
            log(">>> STEP 1: Health")
            r = client.get("/health")
            r.raise_for_status()
            results["steps"]["health"] = r.json()

            log(">>> STEP 2: Wailly excerpt")
            r = client.get("/demo/wailly-excerpt", params={"max_pages": 2})
            r.raise_for_status()
            excerpt = r.json()
            text = excerpt["text"][:1200]
            results["steps"]["wailly"] = {"char_count": excerpt["char_count"], "used": len(text)}
            log(f"Loaded {len(text)} chars from Wailly")

            log(">>> STEP 3: Agents run")
            r = client.post(
                "/agents/run",
                json={"text": text, "session_id": SESSION, "use_llm": False},
            )
            r.raise_for_status()
            agent = r.json()
            graph_id = agent["graph_id"]
            results["steps"]["agents"] = agent
            log(f"graph_id={graph_id} pol={agent['pol']['pol_score']}")

            log(">>> STEP 4: Graph + node")
            r = client.get(f"/graph/{graph_id}")
            r.raise_for_status()
            graph = r.json()
            node_id = graph["nodes"][0]["id"]
            r2 = client.get(f"/node/{node_id}", params={"graph_id": graph_id})
            r2.raise_for_status()
            results["steps"]["graph"] = {"nodes": len(graph["nodes"]), "node_id": node_id}

            log(">>> STEP 5: Search")
            r = client.post("/search", json={"query": "roi", "graph_id": graph_id, "top_k": 3})
            r.raise_for_status()
            results["steps"]["search"] = r.json()

            log(">>> STEP 6: Reconstruct")
            r = client.post("/decode", json={"graph_id": graph_id})
            r.raise_for_status()
            decode = r.json()
            results["steps"]["decode"] = decode
            log(f"reversible={decode['reversible']} similarity={decode['similarity']}")

            log(">>> STEP 7: PoL score")
            r = client.get("/pol/score")
            r.raise_for_status()
            results["steps"]["pol"] = r.json()

            log(">>> STEP 8: Store block")
            r = client.post("/store", json={"graph_id": graph_id, "session_id": SESSION})
            r.raise_for_status()
            store = r.json()
            results["steps"]["store"] = store
            log(f"block_index={store['block_index']} hash={store['hash'][:16]}...")

            log(">>> STEP 9: Chain verify")
            r = client.get("/chain/verify")
            r.raise_for_status()
            verify = r.json()
            results["steps"]["verify"] = verify
            r2 = client.get("/chain")
            r2.raise_for_status()
            results["steps"]["chain_count"] = r2.json()["count"]
            log(f"chain valid={verify['valid']} blocks={r2.json()['count']}")

        except httpx.HTTPError as exc:
            results["ok"] = False
            results["error"] = str(exc)
            log(f"ERROR: {exc}")
            OUT_JSON.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
            return 1

    log("=== DEMO COMPLETE ===")
    OUT_JSON.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"JSON: {OUT_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
