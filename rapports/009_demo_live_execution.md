# Rapport 009 — Démo live complète (logs réels)

**Horodatage :** 2026-07-04T23:30:00Z  
**Ordre utilisateur :** Lancer la démo complète avec logs réels, relire PROTOCOLE/AUTO_PROMPT, confirmer conformité.

---

## 1. État d'avancement (%)

| Phase | Avant | Après |
|-------|-------|-------|
| Phase 0 Spec | 100 % | 100 % |
| Phase 1 IR | 100 % | 100 % |
| Phase 2 Backend | 100 % | 100 % |
| Phase 3 Blockchain C | 85 % | 85 % |
| Phase 4 Frontend | 100 % | 100 % |
| **Démo live + logs** | 0 % | **100 %** |
| Phase 5 Hackathon | 0 % | 0 % |
| **Global MVP** | ~88 % | **~92 %** |

---

## 2. Exécution réelle — avant / après

### 2.1 Avant — aucun parcours automatisé CDC §9.2

**Fichier :** `logs/` — pas de `demo_live_latest.txt` ni JSON de session.

### 2.2 Après — parcours 9 étapes via HTTP réel

**Commandes :**
```bash
make chain
make api          # tmux, port 8000
make frontend     # tmux, port 5173
python3 scripts/demo_live.py
```

**Fichier log texte :** `logs/demo_live_latest.txt`

```
=== ARTCB Live Demo 2026-07-04T23:21:07.597920+00:00 ===
>>> STEP 1: Health
>>> STEP 2: Wailly excerpt
Loaded 1200 chars from Wailly
>>> STEP 3: Agents run
graph_id=g_95b4446b3a94 pol=0.6
>>> STEP 4: Graph + node
>>> STEP 5: Search
>>> STEP 6: Reconstruct
reversible=True similarity=1.0
>>> STEP 7: PoL score
>>> STEP 8: Store block
block_index=0 hash=ed1853d74ab70868...
>>> STEP 9: Chain verify
chain valid=True blocks=1
=== DEMO COMPLETE ===
```

**Fichier JSON :** `logs/demo_live_20260704_232107.json` — `"ok": true`, PoL `0.6`, `block_accepted: true`, reconstruction `similarity: 1.0`, `reversible: true`.

**Blockchain persistée :** `data/chain/blocks.jsonl` (gitignored, local)

Ligne bloc #0 (extrait) :
```json
{"index":0,"timestamp":"2026-07-04T23:21:07Z","prev_hash":"0000000000000000000000000000000000000000000000000000000000000000","graph_root":"7ed5786308857dd7a6712c232a71bf839a3ac779c7feeed57def0aac0fed414d","pol_score":0.6,"hash":"ed1853d74ab7086878020248c9342fc8f201aa9e7ba416d3250c04681ceb0398","signature":"ed25519:03fa5a9717da9e86...","graph_id":"g_95b4446b3a94"}
```

**Vérification C post-exécution :**
```python
from artcb.chain.ffi import verify_chain_file
verify_chain_file(Path("data/chain/blocks.jsonl"))  # → (True, "")
```

**Logs API DEBUG :** `logs/20260704_artcb_api.json` — lignes 40-50 (session démo) :

```json
{"ts": "2026-07-04T23:21:02.141069+00:00", "level": "DEBUG", "module": "artcb.api", "message": "ARTCB API started debug=True"}
{"ts": "2026-07-04T23:21:59.022697+00:00", "level": "DEBUG", "module": "artcb.api.websocket", "message": "WebSocket connected session_id=demo_hackathon"}
{"ts": "2026-07-04T23:21:59.031502+00:00", "level": "DEBUG", "module": "artcb.api.websocket", "message": "WebSocket disconnected session_id=demo_hackathon"}
```

**Test GUI manuel :** parcours 9 étapes sur `http://127.0.0.1:5173` — OK (Memorize → graphe → agents → search « roi » → Reconstruct 100 % → Sign block). Enregistrement : `artcb_demo_live_wailly_9_steps.mp4`.

**Bloc #1 additionnel :** créé via UI « Sign block » à 23:24:04Z (`hash=8ad8e3ac15d6449d...`) — chaîne C toujours `valid=True` (2 blocs).

---

## 3. Résultats clés (mesurés, pas simulés)

| Métrique | Valeur |
|----------|--------|
| Texte Wailly chargé | 1200 caractères (PDF `data/fixtures/wailly_le_roi_de_l_inconnu.pdf`) |
| Nœuds graphe | 15 |
| PoL score | **0.6** (seuil acceptation) |
| Reconstruction | similarity **1.0**, reversible **true** |
| Tests pytest | **42/42** passent |
| Mode DEBUG API | **true** (`/health`) |
| Mock / stub | **aucun** (httpx → API réelle, lib C réelle) |

---

## 4. Checklist PROTOCOLE_ARTCB

| Règle | Conformité |
|-------|------------|
| Pas de mock/stub/hardcoding factice | ✅ |
| Mode DEBUG actif | ✅ |
| Lire logs après exécution | ✅ |
| Vérifier génération logs | ✅ |
| Rapport .md après lecture logs | ✅ (ce fichier) |
| Avant / après avec lignes exactes | ✅ §2 |
| Notifier erreurs | ✅ favicon 302 (non bloquant) ; pas d'erreur fonctionnelle |
| Rapports FR, code EN | ✅ |
| État avancement en % | ✅ §1 |
| Push main (D-001) | ✅ commit session |

---

## 5. Livrables ajoutés

| Fichier | Rôle |
|---------|------|
| `scripts/demo_live.py` | Parcours 9 étapes HTTP réel |
| `scripts/demo_live.sh` | Variante bash (secours) |
| `Makefile` cible `demo` | Orchestration documentée |
| `logs/demo_live_*.json` | Trace JSON session |
| `logs/demo_live_latest.txt` | Trace texte lisible |

---

## 6. Écarts connus (honnêteté PROTOCOLE)

| Élément | Statut |
|---------|--------|
| Gradium TTS API | Non branché — UI utilise Web Speech API fr-FR (D-009 partiel) |
| Rewards collectifs `contributors[]` | Non codé (Phase 3 ~85 %) |
| `artcb-devnet` / faucet | Non codé |
| Bob LLM encodage | `use_llm=false` en démo ; rule-based seul (D-008 : les deux chemins existent) |
| Blockchain 100 % décentralisée | JSONL local + Ed25519 ; pas encore réseau P2P |

---

## 7. Prochaine action

Phase 5 : README public, vidéo hackathon 1 min, soumission RAISE Summit (deadline 5 juil. 2026 12h00 CEST).
