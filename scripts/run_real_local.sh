#!/usr/bin/env bash
# Exécution RÉELLE — doit tourner sur la machine UTILISATEUR (votre PC).
# L'agent Cloud ne peut pas exécuter sur votre ordinateur : vous devez lancer ce script.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
LOG_DIR="${ARTCB_LOG_DIR:-./logs}"
mkdir -p "$LOG_DIR"

HOST="$(hostname 2>/dev/null || echo unknown)"
USER_NAME="$(whoami 2>/dev/null || echo unknown)"
UNAME="$(uname -a 2>/dev/null || echo unknown)"

# Détection environnement Cloud Agent Cursor
EXEC_ENV="USER_MACHINE"
if [[ "$HOST" == "cursor" ]] || [[ "$ROOT" == "/workspace" ]]; then
  EXEC_ENV="CLOUD_AGENT"
fi

FINGERPRINT="$LOG_DIR/machine_fingerprint.txt"
{
  echo "timestamp_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "hostname=$HOST"
  echo "user=$USER_NAME"
  echo "pwd=$ROOT"
  echo "uname=$UNAME"
  echo "execution_env=$EXEC_ENV"
} > "$FINGERPRINT"

echo "=============================================="
echo " ARTCB — EXÉCUTION"
echo " Machine: $HOST | User: $USER_NAME"
echo " Répertoire: $ROOT"
echo " Environnement: $EXEC_ENV"
echo " Horodatage: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "=============================================="

if [[ "$EXEC_ENV" == "CLOUD_AGENT" ]]; then
  echo ""
  echo "⚠️  ATTENTION — Vous êtes sur la VM Cloud Agent (cursor /workspace)."
  echo "    Ce n'est PAS la machine de l'utilisateur final."
  echo "    Pour exécuter chez VOUS : clonez le repo sur VOTRE PC et lancez"
  echo "    bash scripts/run_real_local.sh dans VOTRE terminal."
  echo "    Voir EXECUTION_MACHINE_UTILISATEUR.md"
  echo ""
fi

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
  for _ in $(seq 1 30); do
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
echo "=== LOGS GÉNÉRÉS ==="
ls -la "$LOG_DIR/demo_live_latest.txt" "$LOG_DIR/machine_fingerprint.txt" 2>/dev/null
echo ""
echo "--- machine_fingerprint.txt (PREUVE machine) ---"
cat "$FINGERPRINT"
echo ""
echo "--- demo_live_latest.txt ---"
cat "$LOG_DIR/demo_live_latest.txt"
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
if [[ "$EXEC_ENV" == "USER_MACHINE" ]]; then
  echo "=== FIN — exécution sur VOTRE machine ($HOST) ==="
else
  echo "=== FIN — exécution Cloud Agent uniquement ; relancez sur VOTRE PC ==="
fi
