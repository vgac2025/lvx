#!/usr/bin/env bash
# Installation dépendances sur la machine UTILISATEUR (pas cloud-only).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== ARTCB setup — machine: $(hostname) user: $(whoami) ==="

if ! command -v python3 >/dev/null; then
  echo "ERREUR: python3 manquant. Installez Python 3.11+" >&2
  exit 1
fi

if ! command -v gcc >/dev/null; then
  echo "ERREUR: gcc manquant. Installez build-essential (Linux) ou Xcode CLI (Mac)" >&2
  exit 1
fi

if ! pkg-config --exists libssl 2>/dev/null && ! ldconfig -p 2>/dev/null | grep -q libssl; then
  echo "ATTENTION: libssl-dev peut être requis pour compiler libartcb_chain.so"
  echo "  Debian/Ubuntu: sudo apt install libssl-dev"
fi

python3 -m pip install --upgrade pip
python3 -m pip install -e ".[dev]"

echo ""
echo "Build chaîne C..."
make chain

echo ""
echo "Tests..."
python3 -m pytest tests/ -q --tb=line

echo ""
echo "=== Setup OK — lancez: bash scripts/run_real_local.sh ==="
