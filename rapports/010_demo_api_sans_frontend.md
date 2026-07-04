# Rapport 010 — Correction : démo API sans frontend

**Horodatage :** 2026-07-04T23:37:00Z  
**Retour utilisateur :** Pas de fenêtre locale, pas de frontend pour valider la démo. La vidéo hackathon n’est pas dans le périmètre de cet agent.

---

## 1. Correction d’erreur (rapport 009)

| Avant (009 — incorrect pour l’utilisateur) | Après (010 — périmètre réel) |
|-------------------------------------------|------------------------------|
| Démo = API + frontend `:5173` + vidéo GUI | Démo = **`python3 scripts/demo_live.py`** → HTTP `:8000` uniquement |
| « GUI 9 étapes OK » présenté comme validation | Validation = **logs terminal + JSON** ; frontend **optionnel**, jamais requis |
| Prochaine étape « vidéo 1 min hackathon » | **Hors périmètre** — mission déjà assignée ailleurs |

**Action immédiate :** session tmux `artcb-frontend-dev` **arrêtée**. Aucune fenêtre navigateur ouverte.

---

## 2. Exécution réelle API-only (logs du 2026-07-04T23:36:57Z)

**Commandes (2 terminaux max, pas de navigateur) :**
```bash
make chain
make api          # terminal 1 — port 8000
python3 scripts/demo_live.py   # terminal 2
```

**Fichier :** `logs/demo_live_latest.txt`

```
=== ARTCB Live Demo 2026-07-04T23:36:57.582352+00:00 ===
>>> STEP 1: Health
>>> STEP 2: Wailly excerpt
Loaded 1200 chars from Wailly
>>> STEP 3: Agents run
graph_id=g_ba58a40b7872 pol=0.6
>>> STEP 4: Graph + node
>>> STEP 5: Search
>>> STEP 6: Reconstruct
reversible=True similarity=1.0
>>> STEP 7: PoL score
>>> STEP 8: Store block
block_index=2 hash=13731139bfe22e23...
>>> STEP 9: Chain verify
chain valid=True blocks=3
=== DEMO COMPLETE ===
```

**JSON :** `logs/demo_live_20260704_233657.json` — `"ok": true`

| Métrique | Valeur |
|----------|--------|
| PoL | 0.6, bloc accepté |
| Reconstruction | similarity 1.0, reversible true |
| Chaîne C | valid=True, 3 blocs |
| Frontend utilisé | **non** |
| Navigateur ouvert | **non** |

---

## 3. Aperçu du frontend (information seule — sans l’ouvrir)

Le code existe dans `frontend/` (Phase 4) mais **n’est pas nécessaire** pour prouver le MVP backend.

**Apparence (thème sombre, d’après `frontend/src/index.css`) :**
- Fond `#0b0f14`, panneaux `#121820`, texte clair `#e8eef7`
- Titre : « ARTCB — Persistent AI Memory »
- Zone 1 : textarea (extrait Wailly préchargé) + bouton violet **Memorize**
- Zone 2 (grille) : graphe Cytoscape (nœuds/liens) + recherche + boutons Reconstruct / Read aloud / Sign block
- Colonne droite : panneau agents (Explorer bleu, Critic vert) + jauge PoL
- Footer : hash bloc signé après « Sign block »

```
┌─────────────────────────────────────────────────────────────┐
│ ARTCB — Persistent AI Memory                                │
├─────────────────────────────────────────────────────────────┤
│ [ textarea Wailly …                    ] [Memorize] [Load]  │
├──────────────────────────────┬──────────────────────────────┤
│ Graphe Cytoscape (nœuds)     │ AgentPanel (messages)        │
│ [Search…] [Search][Recon…]   │ PolGauge (0.00 → 1.00)       │
├──────────────────────────────┴──────────────────────────────┤
│ Block #N signed ✓ — hash abc… · PoL 0.60                    │
└─────────────────────────────────────────────────────────────┘
```

Pour le voir un jour : `make frontend` puis ouvrir `http://localhost:5173` — **volontairement non fait ici**.

---

## 4. Conformité PROTOCOLE (démo backend)

| Règle | Statut |
|-------|--------|
| Pas de mock | ✅ httpx → API réelle, lib C |
| DEBUG | ✅ |
| Logs lus après exécution | ✅ |
| Rapport après logs | ✅ (ce fichier) |
| Avant / après | ✅ §2 |
| Pas de fenêtre imposée | ✅ corrigé |

---

## 5. État d’avancement : **~92 %** (inchangé)

Phase 5 hackathon / vidéo : **non traitée par cet agent.**
