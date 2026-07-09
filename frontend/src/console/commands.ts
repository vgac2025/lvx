#!/usr/bin/env python3
"""Console.tsx — commandes miroir CLI artcb_cli.py (fetch API réelle)."""

from __future__ import annotations

# Documentation des commandes — synchronisée avec scripts/artcb_cli.py et API_REFERENCE_ARTCB.md

CONSOLE_HELP = """ARTCB Console — commandes (API réelle, pas de mock):

  help                    — cette aide
  clear                   — effacer l'écran

  CORE
  health                  — GET /api/v1/health
  pol                     — GET /api/v1/pol/score
  metrics                 — GET /api/v1/metrics

  CHAÎNE
  chain                   — GET /api/v1/chain
  chain verify            — GET /api/v1/chain/verify
  chain block <index>     — GET /api/v1/chain/block/{index}

  WALLETS
  wallets                 — GET /api/v1/wallet/list
  wallet create <name>    — POST /api/v1/wallet/create

  AGENTS & MINAGE
  agents <texte>          — POST /api/v1/agents/run
  mining status           — GET /api/v1/dashboard/mining/status
  mining latest           — GET /api/v1/dashboard/logs/mining-latest

  POOL E2E (ML-KEM)
  pool status             — GET /api/v1/pool/status
  pool prefs              — GET /api/v1/pool/preferences
  pool jobs               — GET /api/v1/pool/jobs
  pool incoming           — GET /api/v1/pool/incoming

  P2P
  p2p status              — GET /api/v1/p2p/status
  p2p peers               — GET /api/v1/p2p/peers
  p2p sync                — POST /api/v1/p2p/sync

  GROUPES & GOUVERNANCE
  groups <address>        — GET /api/v1/groups?address=
  governance proposals    — GET /api/v1/governance/proposals

  CONNECTEURS & NOTIFS
  connectors              — GET /api/v1/connectors
  connectors formats      — GET /api/v1/connectors/formats
  notifications           — GET /api/v1/notifications/channels

  DASHBOARD
  founders                — GET /api/v1/dashboard/founders/allocation
  demo log                — GET /api/v1/dashboard/logs/demo-live

CLI terminal équivalent:
  python3 scripts/artcb_cli.py <commande> [--base URL]
  Voir API_REFERENCE_ARTCB.md
"""
