#!/usr/bin/env python3
"""Faucet tARTCB — artcb-devnet."""

from __future__ import annotations

import argparse
import json
import os
import sys

import httpx

DEFAULT_BASE = os.getenv("ARTCB_API_BASE", "http://127.0.0.1:8000").rstrip("/")


def main() -> int:
    parser = argparse.ArgumentParser(description="Faucet tARTCB artcb-devnet")
    parser.add_argument("address", help="Adresse artcb1...")
    parser.add_argument("--base", default=DEFAULT_BASE)
    parser.add_argument("--status", action="store_true", help="Afficher statut faucet")
    args = parser.parse_args()

    with httpx.Client(base_url=args.base, timeout=30.0) as client:
        if args.status:
            r = client.get("/api/v1/devnet/faucet/status")
        else:
            r = client.post("/api/v1/devnet/faucet", json={"address": args.address})
    print(json.dumps(r.json(), ensure_ascii=False, indent=2))
    return 0 if r.status_code < 400 else 1


if __name__ == "__main__":
    sys.exit(main())
