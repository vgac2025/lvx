#!/bin/bash
# Script de démarrage API Dashboard avec PYTHONPATH correct

cd "$(dirname "$0")/.." || exit 1

export PYTHONPATH="$(pwd)/src:$PYTHONPATH"

echo "=== Démarrage API Dashboard ==="
echo "PYTHONPATH: $PYTHONPATH"
echo "Port: 8000"
echo "Logs: logs/api_dashboard.log"
echo ""

# Tuer les anciens processus
pkill -9 -f "uvicorn.*api.main" 2>/dev/null
sleep 1

# Démarrer l'API
exec uvicorn api.main:app --host 0.0.0.0 --port 8000 --log-level info

# Made with Bob
