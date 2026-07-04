#!/usr/bin/env bash
# Exécution RÉELLE locale ARTCB — PROTOCOLE: pas de mock, logs obligatoires.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=============================================="
echo " ARTCB — EXÉCUTION RÉELLE LOCALE"
echo " Répertoire: $ROOT"
echo " Horodatage: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "=============================================="

echo ""
echo "[1/4] Build lib C..."
make chain

echo ""
echo "[2/4] Tests pytest..."
python3 -m pytest tests/ -q --tb=line

API_BASE="http://127.0.0.1:8000/api/v1"
if ! curl -sf "$API_BASE/health" >/dev/null 2>&1; then
  echo ""
  echo "[!] API absente sur :8000 — démarrage uvicorn..."
  uvicorn api.main:app --app-dir src --host 127.0.0.1 --port 8000 &
  API_PID=$!
  trap 'kill $API_PID 2>/dev/null || true' EXIT
  for i in $(seq 1 30); do
    curl -sf "$API_BASE/health" >/dev/null 2>&1 && break
    sleep 0.5
  done
  if ! curl -sf "$API_BASE/health" >/dev/null 2>&1; then
    echo "ERREUR: API ne démarre pas sur :8000" >&2
    exit 1
  fi
  echo "    API démarrée (pid $API_PID)"
else
  echo ""
  echo "[2b] API déjà active sur :8000"
fi

echo ""
echo "[3/4] Health (curl réel):"
curl -s "$API_BASE/health" | python3 -m json.tool

echo ""
echo "[4/4] Démo 9 étapes (HTTP réel, pas de navigateur)..."
python3 scripts/demo_live.py

echo ""
echo "=== LOGS GÉNÉRÉS (vérification PROTOCOLE) ==="
ls -la logs/demo_live_latest.txt logs/demo_live_*.json 2>/dev/null | tail -5
echo ""
echo "--- Contenu logs/demo_live_latest.txt ---"
cat logs/demo_live_latest.txt
echo ""
echo "--- Vérification chaîne C ---"
PYTHONPATH=src python3 -c "
from pathlib import Path
from artcb.chain.ffi import verify_chain_file
p = Path('data/chain/blocks.jsonl')
v, msg = verify_chain_file(p)
print('blocks.jsonl:', p.resolve())
print('valid:', v, 'msg:', repr(msg))
print('lignes:', len(p.read_text().strip().split(chr(10))) if p.exists() else 0)
"
echo ""
echo "=== FIN EXÉCUTION RÉELLE — lisez logs/demo_live_latest.txt ==="
