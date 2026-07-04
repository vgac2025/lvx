# Rapport 007 — Phase 2 complète + Phase 3 blockchain C

**Horodatage :** 2026-07-04T23:12:00Z  
**Ordre utilisateur :** finir Phase 2 (routes, WebSocket, Bob HTTP) puis Phase 3 blockchain C

---

## 1. État d'avancement (%)

| Phase | Avant | Après |
|-------|-------|-------|
| Phase 1 IR | 100 % | 100 % |
| Phase 2 Backend | ~40 % | **100 %** |
| Phase 3 Blockchain C | 0 % | **85 %** (C hash/verify + Ed25519 Python + store) |
| Phase 4 Frontend | 0 % | 0 % |
| **Global MVP** | ~45 % | **~62 %** |

---

## 2. Phase 2 — avant / après

### `src/api/main.py`

**Avant :** 6 endpoints monolithiques, pas de WebSocket, pas de Bob.

**Après :** `create_app()` + `routes.py` (12 endpoints CDC §8) + `websocket.py` (§20).

| Endpoint | Statut |
|----------|--------|
| POST `/encode` | ✅ + path Bob LLM |
| POST `/decode` | ✅ |
| GET `/graph/{id}` | ✅ |
| GET `/node/{id}` | ✅ |
| POST `/search` | ✅ |
| POST `/store` | ✅ → blockchain |
| GET `/chain` | ✅ |
| GET `/chain/verify` | ✅ C |
| GET `/rtleg/events` | ✅ |
| GET `/pol/score` | ✅ |
| POST `/agents/run` | ✅ |
| GET `/health` | ✅ |
| WS `/ws/graph/{session_id}` | ✅ |

### Nouveaux modules

| Fichier | Rôle |
|---------|------|
| `src/artcb/ir/bob_client.py` | HTTP Bob signé (`litellm-ibm-bob`) |
| `src/artcb/ir/llm_encoder.py` | Path B + fallback rule-based |
| `src/artcb/memory/vector_store.py` | Recherche sémantique MVP |
| `src/artcb/memory/graph_store.py` | Persistance graphes |
| `src/api/deps.py` | État application |

---

## 3. Phase 3 — blockchain C

### Fichiers C

| Fichier | Rôle |
|---------|------|
| `src/c/libartcb_chain.h` | API SHA256 + verify |
| `src/c/libartcb_chain.c` | OpenSSL SHA256, chaîne JSONL |
| `src/c/Makefile` | Build `libartcb_chain.so` |
| `src/artcb/chain/ffi.py` | ctypes Python |
| `src/artcb/chain/manager.py` | Blocs + Ed25519 + JSONL |

**Genesis `prev_hash` :** 64 zéros (fix parseur C).

---

## 4. Tests exécutés

```bash
make -C src/c all test
python3 -m pytest tests/ -v
# 41 passed
```

Log : `logs/20260704_phase2_phase3_final.json`

| Suite | Résultat |
|-------|----------|
| test_api | 6/6 ✅ |
| test_chain | 4/4 ✅ |
| test_pol | 3/3 ✅ |
| test_ir + book + symbols | 28/28 ✅ |

---

## 5. Build requis

```bash
make -C src/c all
pip install -e ".[dev]"
uvicorn api.main:app --app-dir src --reload
```

`tests/conftest.py` build automatique si `.so` absent.

---

## 6. Reste MVP

| Élément | Phase |
|---------|-------|
| Frontend graphe React | 4 |
| Contributors[] rewards on-chain | 3.7 |
| artcb-devnet P2P | 3.6 |
| Gradium TTS UI | 4 |

---

**Fin rapport 007**
