#!/usr/bin/env bash
# ARTCB live demo script — 9 steps CDC §9.2 (real HTTP, no mock)
set -euo pipefail

BASE="${ARTCB_API_BASE:-http://127.0.0.1:8000/api/v1}"
SESSION="demo_live_$(date +%H%M%S)"
LOG_DIR="${ARTCB_LOG_DIR:-./logs}"
RESULT="$LOG_DIR/demo_live_$(date +%Y%m%d_%H%M%S).json"

mkdir -p "$LOG_DIR"
echo "=== ARTCB Live Demo ===" | tee "$LOG_DIR/demo_live_latest.txt"
echo "Base: $BASE Session: $SESSION" | tee -a "$LOG_DIR/demo_live_latest.txt"

step() { echo ""; echo ">>> STEP $1: $2" | tee -a "$LOG_DIR/demo_live_latest.txt"; }

step 1 "Health"
curl -sf "$BASE/health" | tee -a "$LOG_DIR/demo_live_latest.txt"

step 2 "Wailly excerpt"
TEXT=$(curl -sf "$BASE/demo/wailly-excerpt?max_pages=2" | python3 -c "import sys,json; print(json.load(sys.stdin)['text'][:1500])")
echo "Loaded ${#TEXT} chars from Wailly" | tee -a "$LOG_DIR/demo_live_latest.txt"

step 3 "Agents run (dual-agent + PoL)"
AGENT=$(curl -sf -X POST "$BASE/agents/run" \
  -H "Content-Type: application/json" \
  -d "$(python3 -c "import json; print(json.dumps({'text': '''$TEXT'''[:800], 'session_id': '$SESSION'}))")")
echo "$AGENT" | python3 -m json.tool | tee -a "$LOG_DIR/demo_live_latest.txt"
GRAPH_ID=$(echo "$AGENT" | python3 -c "import sys,json; print(json.load(sys.stdin)['graph_id'])")

step 4 "Graph fetch + node"
curl -sf "$BASE/graph/$GRAPH_ID" | python3 -c "import sys,json; g=json.load(sys.stdin); print(f\"nodes={len(g['nodes'])} edges={len(g['edges'])}\")" | tee -a "$LOG_DIR/demo_live_latest.txt"
NODE_ID=$(curl -sf "$BASE/graph/$GRAPH_ID" | python3 -c "import sys,json; print(json.load(sys.stdin)['nodes'][0]['id'])")
curl -sf "$BASE/node/$NODE_ID?graph_id=$GRAPH_ID" | python3 -c "import sys,json; n=json.load(sys.stdin); print(n['id'], n['t'], n['txt'][:60])" | tee -a "$LOG_DIR/demo_live_latest.txt"

step 5 "Search"
curl -sf -X POST "$BASE/search" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"roi\", \"graph_id\": \"$GRAPH_ID\", \"top_k\": 3}" | python3 -m json.tool | tee -a "$LOG_DIR/demo_live_latest.txt"

step 6 "Reconstruct (decode)"
DECODE=$(curl -sf -X POST "$BASE/decode" -H "Content-Type: application/json" -d "{\"graph_id\": \"$GRAPH_ID\"}")
echo "$DECODE" | python3 -c "import sys,json; d=json.load(sys.stdin); print('reversible=', d['reversible'], 'similarity=', d['similarity'])" | tee -a "$LOG_DIR/demo_live_latest.txt"

step 7 "PoL score"
curl -sf "$BASE/pol/score" | python3 -m json.tool | tee -a "$LOG_DIR/demo_live_latest.txt"

step 8 "Store block (blockchain)"
STORE=$(curl -sf -X POST "$BASE/store" \
  -H "Content-Type: application/json" \
  -d "{\"graph_id\": \"$GRAPH_ID\", \"session_id\": \"$SESSION\"}")
echo "$STORE" | python3 -m json.tool | tee -a "$LOG_DIR/demo_live_latest.txt"

step 9 "Chain verify"
curl -sf "$BASE/chain/verify" | python3 -m json.tool | tee -a "$LOG_DIR/demo_live_latest.txt"
curl -sf "$BASE/chain" | python3 -c "import sys,json; print('blocks=', json.load(sys.stdin)['count'])" | tee -a "$LOG_DIR/demo_live_latest.txt"

echo "" | tee -a "$LOG_DIR/demo_live_latest.txt"
echo "=== DEMO COMPLETE ===" | tee -a "$LOG_DIR/demo_live_latest.txt"
echo "$AGENT" > "$RESULT"
echo "Result saved: $RESULT"
