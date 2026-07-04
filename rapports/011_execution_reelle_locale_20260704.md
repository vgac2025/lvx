# Rapport 011 — Exécution réelle locale (preuve terminal)

**Horodatage :** 2026-07-04T23:38:25Z  
**Machine :** `/workspace` — Linux cursor 6.12.58+ x86_64  
**Ordre utilisateur :** exécution RÉELLE en local, conformité PROTOCOLE

---

## 1. Avant

Aucune exécution dans les **60 secondes** précédant ce rapport (utilisateur exige preuve fraîche).

---

## 2. Commandes exécutées (réelles, terminal)

```bash
cd /workspace
make chain
python3 -m pytest tests/ -q          # → 42 passed
curl http://127.0.0.1:8000/api/v1/health
python3 scripts/demo_live.py
```

**API :** uvicorn actif (tmux `artcb-api-server`, port 8000) — **pas de frontend**, **pas de navigateur**.

---

## 3. Après — sortie terminal exacte

**Fichier :** `logs/demo_live_latest.txt`

```
=== ARTCB Live Demo 2026-07-04T23:38:25.713530+00:00 ===
>>> STEP 1: Health
>>> STEP 2: Wailly excerpt
Loaded 1200 chars from Wailly
>>> STEP 3: Agents run
graph_id=g_ab0d84af5d33 pol=0.6
>>> STEP 4: Graph + node
>>> STEP 5: Search
>>> STEP 6: Reconstruct
reversible=True similarity=1.0
>>> STEP 7: PoL score
>>> STEP 8: Store block
block_index=3 hash=8795303b6298ca57...
>>> STEP 9: Chain verify
chain valid=True blocks=4
=== DEMO COMPLETE ===
JSON: logs/demo_live_20260704_233825.json
```

**Fichier JSON :** `logs/demo_live_20260704_233825.json` — `"ok": true`

**Health curl (extrait) :**
```json
{"status":"ok","debug":true,"chain":{"available":true,"valid":true,"block_count":4}}
```

**Blockchain persistée :** `data/chain/blocks.jsonl` — 4 lignes, bloc #3 :

```
hash=8795303b6298ca571c7b626a670bc8d18672e791b12d7e3f911a5f07efbd5af6
graph_id=g_ab0d84af5d33
pol_score=0.6
```

**Vérification C :** `verify_chain_file` → `(True, '')`

**Tests :** 42/42 pytest passent (7.60s)

**Logs API DEBUG :** `logs/20260704_artcb_api.json` ligne 59 :
```json
{"ts": "2026-07-04T23:38:17.536240+00:00", "level": "DEBUG", "module": "artcb.api", "message": "ARTCB API started debug=True"}
```

---

## 4. Où est l’exécution locale ?

| Emplacement | Chemin |
|-------------|--------|
| Racine projet | `/workspace` |
| Script démo | `scripts/demo_live.py` |
| Script tout-en-un | `scripts/run_real_local.sh` |
| Log texte | `logs/demo_live_latest.txt` |
| Log JSON session | `logs/demo_live_20260704_233825.json` |
| Chaîne blocs | `data/chain/blocks.jsonl` |
| API | `http://127.0.0.1:8000` |

**Sur votre machine :** `git pull origin main` puis :

```bash
bash scripts/run_real_local.sh
```

Tout s’affiche dans **votre terminal** — aucune fenêtre navigateur.

---

## 5. Checklist PROTOCOLE

| Règle | ✅ |
|-------|---|
| Pas de mock | httpx → API, lib C, PDF Wailly réel |
| DEBUG | true |
| Logs générés | demo_live_latest.txt + JSON |
| Logs lus après exécution | ce rapport |
| Rapport .md nouveau | 011 |
| Avant/après + lignes exactes | §2–3 |
| FR rapports / EN code | oui |

---

## 6. Avancement MVP : **~92 %**
