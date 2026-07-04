#!/usr/bin/env python3
"""CLI Phase 1 — encode / decode IR ARTCB."""

from __future__ import annotations

import argparse
import json
import sys

from artcb.ir.decoder import IRDecoder
from artcb.ir.encoder import IREncoder
from artcb.logging_config import setup_logging


def main() -> int:
    parser = argparse.ArgumentParser(description="ARTCB IR Engine CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    enc = sub.add_parser("encode", help="Encoder un texte en graphe IR")
    enc.add_argument("text", help="Texte source")
    enc.add_argument("--session", default=None, help="ID session")

    dec = sub.add_parser("decode", help="Décoder un graphe IR JSON")
    dec.add_argument("graph_file", help="Fichier JSON graphe")

    args = parser.parse_args()
    setup_logging("artcb.cli")

    if args.command == "encode":
        graph = IREncoder().encode(args.text, session_id=args.session)
        print(graph.to_json())
        return 0

    with open(args.graph_file, encoding="utf-8") as handle:
        data = json.load(handle)
    from artcb.ir.models import IRGraph

    graph = IRGraph.from_dict(data)
    metrics = IRDecoder().decode_with_metrics(graph)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
