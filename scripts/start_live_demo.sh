#!/bin/bash
# Script de démarrage API + Frontend pour tests manuels en temps réel

set -e

PROJECT_ROOT="/home/lvx/ARTCB/lvx"
cd "$PROJECT_ROOT"

# Couleurs pour logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Démarrage ARTCB Live Demo ===${NC}"
echo ""

# 1. Arrêter processus existants
echo -e "${YELLOW}[1/5] Arrêt processus existants...${NC}"
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
sleep 2

# 2. Vérifier dépendances Python
echo -e "${YELLOW}[2/5] Vérification dépendances Python...${NC}"
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${RED}Erreur: fastapi non installé${NC}"
    exit 1
fi

# 3. Démarrer API Backend
echo -e "${YELLOW}[3/5] Démarrage API Backend (port 8000)...${NC}"
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"
export ARTCB_DEBUG=true
export ARTCB_LOG_LEVEL=DEBUG

nohup python3 -m uvicorn api.main:app \
    --host 127.0.0.1 \
    --port 8000 \
    --reload \
    > "$PROJECT_ROOT/logs/api_live_$(date +%Y%m%d_%H%M%S).log" 2>&1 &

API_PID=$!
echo "API PID: $API_PID"
sleep 3

# Vérifier que l'API démarre
if ! ps -p $API_PID > /dev/null; then
    echo -e "${RED}Erreur: API n'a pas démarré${NC}"
    tail -20 "$PROJECT_ROOT/logs/api_live_"*.log | tail -20
    exit 1
fi

# 4. Tester endpoint API
echo -e "${YELLOW}[4/5] Test endpoint API /api/v1/health...${NC}"
sleep 2
if curl -s http://127.0.0.1:8000/api/v1/health | grep -q "ok"; then
    echo -e "${GREEN}✓ API répond correctement${NC}"
else
    echo -e "${RED}✗ API ne répond pas${NC}"
    tail -20 "$PROJECT_ROOT/logs/api_live_"*.log
    exit 1
fi

# 5. Démarrer Frontend Vite
echo -e "${YELLOW}[5/5] Démarrage Frontend Vite (port 5173)...${NC}"
cd "$PROJECT_ROOT/frontend"

if [ ! -d "node_modules" ]; then
    echo "Installation dépendances npm..."
    npm install
fi

nohup npm run dev \
    > "$PROJECT_ROOT/logs/frontend_live_$(date +%Y%m%d_%H%M%S).log" 2>&1 &

FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"
sleep 3

# Vérifier que le frontend démarre
if ! ps -p $FRONTEND_PID > /dev/null; then
    echo -e "${RED}Erreur: Frontend n'a pas démarré${NC}"
    tail -20 "$PROJECT_ROOT/logs/frontend_live_"*.log
    exit 1
fi

echo ""
echo -e "${GREEN}=== Démarrage Réussi ===${NC}"
echo ""
echo -e "${GREEN}API Backend:${NC}     http://127.0.0.1:8000"
echo -e "${GREEN}API Docs:${NC}        http://127.0.0.1:8000/docs"
echo -e "${GREEN}Frontend:${NC}        http://127.0.0.1:5173"
echo ""
echo -e "${YELLOW}Logs en temps réel:${NC}"
echo "  API:      tail -f $PROJECT_ROOT/logs/api_live_*.log | tail -1"
echo "  Frontend: tail -f $PROJECT_ROOT/logs/frontend_live_*.log | tail -1"
echo ""
echo -e "${YELLOW}Arrêter les serveurs:${NC}"
echo "  kill $API_PID $FRONTEND_PID"
echo "  ou: pkill -f 'uvicorn|vite'"
echo ""
echo -e "${GREEN}Prêt pour tests manuels !${NC}"

# Made with Bob
