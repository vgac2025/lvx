# Dashboard ARTCB — Wireframes ASCII (toutes pages + CLI)

**Horodatage :** 2026-07-07T04:30:00Z  
**CDC parent :** `CAHIER_DES_CHARGES_DASHBOARD_ARTCB.md` v1.6  
**Design :** `DESIGN_RETRO_2D_MINECRAFT_ARTCB.md` — pixel + blocs MC  
**Tokenomics :** block reward **1 ARTCB** (halving 210k blocs)  
**PROTOCOLE :** données réelles API, badge DEBUG, pas de mock

---

## 0. Shell global (toutes vues sauf CLI plein écran)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ ◆ ARTCB    [● API OK]  PoL 0.60  Blocs 19  Chain ✓   [DEBUG]    [⌘K]     │
├────────────┬─────────────────────────────────────────────────────────────────┤
│ CORE       │  Titre vue active                    [1d][7d][30d][All]        │
│ ▶ Accueil  │─────────────────────────────────────────────────────────────────│
│   Mémoriser│                                                                 │
│   Graphe   │              << CONTENU VUE ACTIVE >>                           │
│ CHAIN      │                                                                 │
│   Chaîne   │                                                                 │
│   Wallets  │                                                                 │
│   Minage   │                                                                 │
│ SYSTEM     │                                                                 │
│   Système  │                                                                 │
│   Logs     │                                                                 │
│   Console  │  ← mode CLI (V9)                                                │
├────────────┴─────────────────────────────────────────────────────────────────┤
│ Dernier bloc #19 · hash 8edfa3b… · session demo_hackathon · machine: USER   │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Sidebar groupes :** CORE / CHAIN / SYSTEM (style Supermemory)  
**Header :** statut API + KPI compacts (style Mempool + Cursor)

---

## V1 — Accueil (KPI + onboarding)

### V1.0 — Vue principale

```
┌─ Accueil ────────────────────────────────────────────────────────────────────┐
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│ │ PoL      │ │ Blocs    │ │ Wallets  │ │ Graphes  │ │ Chain    │          │
│ │  0.60    │ │   19     │ │    3     │ │    12    │ │  VALID ✓ │          │
│ │ +12% 7d  │ │ +2 today │ │ 1.5 ₳    │ │ IR live  │ │ verify OK│          │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│                                                                            │
│ Parcours rapide (CDC §9.2) — checklist style Cursor                        │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ [✓] Mémoriser un texte          [→ Aller Mémoriser]                  │ │
│ │ [✓] Explorer le graphe          [→ Aller Graphe]                     │ │
│ │ [ ] Rechercher un nœud          [→ Graphe + search]                  │ │
│ │ [ ] Reconstruire + signer bloc  [→ Graphe → Sign]                    │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│ Derniers blocs (style Mempool — cubes compacts)                            │
│ ┌────┐┌────┐┌────┐┌────┐┌────┐                                            │
│ │#19││#18││#17││#16││#15│  [Voir tout → Chaîne]                           │
│ │1₳ ││1₳ ││1₳ ││0.5││1₳ │  reward / bloc (1 ARTCB genesis epoch)         │
│ └────┘└────┘└────┘└────┘└────┘                                            │
│                                                                            │
│ Activité (heatmap style Cursor — blocs minés / jour)                         │
│ ░░▓▓░░▓▓▓▓░░▓░  J F M A M J J A S O N D                                   │
└────────────────────────────────────────────────────────────────────────────┘
```

### V1.1 — Sous-page : alerte DEBUG

```
┌─ Accueil › Alertes DEBUG ──────────────────────────────────────────────────┐
│ [!] API /health timeout 13:24 — redémarrer uvicorn                         │
│ [!] PDF Quintus absent du repo                                             │
│ [i] Dernière demo_live : OK — similarity 1.0                               │
│                              [Ouvrir Logs] [Copier rapport]                │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## V2 — Mémoriser (parcours cœur)

### V2.0 — Vue principale

```
┌─ Mémoriser ────────────────────────────────────────────────────────────────┐
│ Source                                                                     │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ [Texte Wailly chargé — chapitre 2…]                                    │ │
│ │                                                                        │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
│ [Mémoriser]  [Charger Wailly]  [ ] use_llm  [Importer fichier]             │
│                                                                            │
│ Animation WebSocket (temps réel — CDC §9.2 étape 2)                        │
│ ┌──────────────────────────────┬─────────────────────────────────────────┐ │
│ │ Graphe en construction…      │ AGENTS                                  │ │
│ │  ●──●──●  (live nodes)       │ Explorer: Node n1 (S): …               │ │
│ │                              │ Critic: PoL 0.60 — 14 nodes validated  │ │
│ └──────────────────────────────┴─────────────────────────────────────────┘ │
│                                                                            │
│ Résultat: graph_id=g_abc123 · PoL 0.60 · [Ouvrir dans Graphe →]            │
└────────────────────────────────────────────────────────────────────────────┘
```

### V2.1 — Sous-page : empty state (style Supermemory Documents)

```
┌─ Mémoriser ────────────────────────────────────────────────────────────────┐
│                        📄  Aucun graphe encore                               │
│     Collez un texte ou chargez l'extrait Wailly pour mémoriser.            │
│              [IMPORTER TEXTE]    [DOCS API /agents/run]                      │
└────────────────────────────────────────────────────────────────────────────┘
```

### V2.2 — Sous-page : modale setup (style Supermemory Codex)

```
┌─ Mémoriser › Session ──────────────────────────────────────────────────────┐
│                    ┌─────────────────────────────────────┐                 │
│                    │ Configurer session                  │                 │
│                    │ session_id: [demo_hackathon    ]    │                 │
│                    │ use_llm:    [ ] Ollama / Bob       │                 │
│                    │                    [Appliquer] [×]   │                 │
│                    └─────────────────────────────────────┘                 │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## V3 — Graphe IR

### V3.0 — Vue principale

```
┌─ Graphe IR ────────────────────────────────────────────────────────────────┐
│ graph_id: g_abc123                                    PoL [████░░] 0.60      │
│ ┌────────────────────────────────────────┬─────────────────────────────────┐ │
│ │         CYTOSCAPE (plein écran)        │ Explorer │ Critic              │ │
│ │            ●────●                      │ ─────────────────────────────── │ │
│ │           / \   \                      │ 14:02 Explorer: Found node…     │ │
│ │          ●   ●──●                      │ 14:02 Critic: Block ready       │ │
│ │                                        │ ─────────────────────────────── │ │
│ │  [Legend] [Zoom+][Zoom-][Fit]         │ PoL gauge: Comp 72% Val 95%     │ │
│ └────────────────────────────────────────┴─────────────────────────────────┘ │
│ Selected: "décision architecture FastAPI…"                                 │
│ [Search: architecture____] [Search] [Reconstruct] [Read] [Sign block]      │
└────────────────────────────────────────────────────────────────────────────┘
```

### V3.1 — Sous-page : recherche sémantique

```
┌─ Graphe › Recherche ───────────────────────────────────────────────────────┐
│ Query: "décision architecture"                                             │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ #1 n_42  score 0.92  "…décision sur l'architecture FastAPI…"  [Focus] │ │
│ │ #2 n_07  score 0.81  "…problème de contexte…"                 [Focus] │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

### V3.2 — Sous-page : reconstruction (split view)

```
┌─ Graphe › Reconstruct ─────────────────────────────────────────────────────┐
│ Similarité: 100%  ·  Réversible: ✓                                         │
│ ┌─────────────────────────┬─────────────────────────┐                      │
│ │ ORIGINAL                │ RECONSTRUIT             │                      │
│ │ Ligne identique         │ Ligne identique         │  (diff vert)         │
│ │ Texte modifié           │ Texte modifié           │                      │
│ └─────────────────────────┴─────────────────────────┘                      │
│                                              [Fermer] [Signer bloc →]      │
└────────────────────────────────────────────────────────────────────────────┘
```

### V3.3 — Sous-page : détail nœud

```
┌─ Graphe › Nœud n_42 ───────────────────────────────────────────────────────┐
│ Type: S (statement)  ·  Connexions: 3 entrantes, 2 sortantes              │
│ Texte complet: "Nous avons décidé d'utiliser FastAPI pour l'API…"         │
│ [Surligner connexions] [Lire à voix haute] [Copier]                         │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## V4 — Blockchain (style Mempool)

### V4.0 — Vue principale — timeline blocs

```
┌─ Chaîne ───────────────────────────────────────────────────────────────────┐
│ [Verify chain ✓]  19 blocs  ·  epoch reward: 1 ARTCB  ·  halving: 209981  │
│                                                                            │
│ Mempool ARTCB (en attente)          │  Blocs signés (récents)              │
│ ┌───┐┌───┐                          │ ┌─────┐┌─────┐┌─────┐┌─────┐        │
│ │ ? ││ ? │  graphes non stockés     │ │ #19 ││ #18 ││ #17 ││ #16 │        │
│ └───┘└───┘                          │ │ 1₳  ││ 1₳  ││ 1₳  ││ 1₳  │        │
│                                     │ └─────┘└─────┘└─────┘└─────┘        │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ #  │ Hash (16)    │ PoL  │ Reward │ Contributors │ Time              │ │
│ │ 19 │ 8edfa3b…     │ 0.60 │ 1 ₳    │ 1            │ il y a 2h         │ │
│ │ 18 │ c9514a7…     │ 0.58 │ 1 ₳    │ 2            │ il y a 3h         │ │
│ │ …  │              │      │        │              │                   │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

### V4.1 — Sous-page : détail bloc

```
┌─ Chaîne › Bloc #19 ────────────────────────────────────────────────────────┐
│ index: 19  ·  timestamp: 2026-07-05T13:24:26Z                               │
│ hash: 8edfa3b2c08b3d5c4f5e42448cf77aa9b8ccd31e…                            │
│ signature: ed25519:…  ·  graph_id: g_abc123  ·  graph_root: merkle…       │
│ block_reward: 1.00000000 ARTCB (100000000 sat)                              │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ Contributor        │ PoL   │ Reward sat    │ Reward ₳                 │ │
│ │ artcb1q…alice      │ 0.80  │ 100000000     │ 1.00000000               │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
│ [Vérifier signature] [Voir graphe] [Export JSON]                            │
└────────────────────────────────────────────────────────────────────────────┘
```

### V4.2 — Sous-page : vérification chain

```
┌─ Chaîne › Verify ──────────────────────────────────────────────────────────┐
│ GET /chain/verify                                                          │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ valid: true                                                            │ │
│ │ message: "Chain integrity OK"                                          │ │
│ │ block_count: 19                                                        │ │
│ │ public_key: base64…                                                    │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## V5 — Wallets

### V5.0 — Vue principale

```
┌─ Wallets ──────────────────────────────────────────────────────────────────┐
│ [+ Créer wallet]  [Import founders]                                         │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ Nom      │ Adresse (16)     │ Balance    │ Blocs │ Actions              │ │
│ │ miner-1  │ artcb1q7x…       │ 1.50 ARTCB │   2   │ [Détail] [Copier]   │ │
│ │ founder  │ artcb1f0u…       │ 210000 ₳   │   0   │ [Détail] (alloc)    │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
│ Founders (data/founders/founders_allocation.json) — style Cursor Members   │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐                                     │
│ │ Founder1 │ │ Founder2 │ │ …        │  1% chacun = 210000 ARTCB          │
│ │ 210k ₳   │ │ 210k ₳   │ │          │                                     │
│ └──────────┘ └──────────┘ └──────────┘                                     │
└────────────────────────────────────────────────────────────────────────────┘
```

### V5.1 — Sous-page : créer wallet

```
┌─ Wallets › Créer ──────────────────────────────────────────────────────────┐
│ Nom: [________________]                                                    │
│ ⚠ Clé privée générée localement — jamais envoyée au serveur               │
│                              [Générer] [Annuler]                           │
└────────────────────────────────────────────────────────────────────────────┘
```

### V5.2 — Sous-page : historique rewards

```
┌─ Wallets › artcb1q7x… › Rewards ───────────────────────────────────────────┐
│ Balance: 1.50 ARTCB                                                        │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ Bloc │ reward_satoshi │ PoL  │ Date                                    │ │
│ │  18  │ 100000000      │ 0.80 │ 2026-07-05                              │ │
│ │  17  │  50000000      │ 0.50 │ 2026-07-05  (50% part collective)       │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## V6 — Minage PoL

### V6.0 — Vue principale (style Mempool Mining)

```
┌─ Minage PoL ───────────────────────────────────────────────────────────────┐
│ Epoch actuelle: 1 ARTCB/bloc  ·  Prochain halving: bloc 210000 (209981 rest)│
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│ │ Dernier PoL  │ │ Blocs minés  │ │ Reward total │ │ Hashrate*    │       │
│ │    0.60      │ │     19       │ │   19 ₳       │ │  N/A (PoL)   │       │
│ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       │
│ * Pas de PoW — métrique placeholder ou bench IR                            │
│                                                                            │
│ Distribution pools contributeurs (donut — style Mempool)                     │
│        ┌─────────┐     Alice 40% · Bob 35% · Agent 25%                     │
│        │  ◐◑◐   │                                                         │
│        └─────────┘                                                         │
│                                                                            │
│ Dernier mining_results_*.json                                              │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ reward_artcb: 1.0  ·  pol: 0.60  ·  reversible: true  ·  nodes: 14    │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
│ [Lancer mine_learning_simple.py →]  (affiche sortie ou lien Console)       │
└────────────────────────────────────────────────────────────────────────────┘
```

### V6.1 — Sous-page : historique minage

```
┌─ Minage › Historique ──────────────────────────────────────────────────────┐
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ Fichier                        │ Reward │ PoL  │ Date                 │ │
│ │ mining_results_20260705.json   │ 1.0 ₳  │ 0.60 │ 2026-07-05 13:24     │ │
│ │ mining_results_20260705.json   │ 1.0 ₳  │ 0.60 │ 2026-07-05 13:18     │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## V7 — Système

### V7.0 — Vue principale

```
┌─ Système ──────────────────────────────────────────────────────────────────┐
│ Machine: USER_MACHINE  ·  fingerprint: logs/machine_fingerprint.txt          │
│ ┌──────────────── SystemMetrics (refresh 5s) ────────────────────────────┐ │
│ │ CPU [████░░░░] 42%   RAM [██████░░] 68%   Disk [███░░░░░] 31%          │ │
│ │ Network: ↑ 12 KB/s  ↓ 45 KB/s                                         │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
│ Intégrations (style Cursor)                                                │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ FastAPI :8000     [● Connecté]  [Redémarrer]                          │ │
│ │ Chain JSONL       [● 19 blocs]  [Verify]                              │ │
│ │ Ollama / Bob      [○ Non testé] [Tester]                              │ │
│ │ GitHub vgac2025   [● lvx]       [Gérer]                               │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
│ Cloud Agents config (style Cursor — lecture seule DEBUG)                   │
│ repo: vgac2025/lvx  ·  branch prefix: cursor/  ·  model: (config user)     │
└────────────────────────────────────────────────────────────────────────────┘
```

### V7.2 — Sous-page : métriques détaillées

```
┌─ Système › Métriques API ──────────────────────────────────────────────────┐
│ GET /metrics — graphique ligne 1h                                          │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │     CPU %                                                              │ │
│ │ 50┤     ╭─╮                                                          │ │
│ │  0┤─────╯ ╰────────────────────────────────────────────────────────  │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## V8 — Logs DEBUG (PROTOCOLE)

### V8.0 — Vue principale (style Supermemory Requests)

```
┌─ Logs DEBUG ───────────────────────────────────────────────────────────────┐
│ [demo_live_latest] [api JSON] [mining_*.log] [audit_*.log]    Filtre: [All]│
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                            │
│ │ Requêtes 24h│ │ Erreurs     │ │ Latence moy │                            │
│ │     42      │ │      0      │ │   120 ms    │                            │
│ └─────────────┘ └─────────────┘ └─────────────┘                            │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ TYPE     │ STATUS │ DURATION │ TIME      │ DETAIL                     │ │
│ │ POST     │ 200    │ 604ms    │ il y a 8m │ /agents/run                │ │
│ │ GET      │ 200    │ 12ms     │ il y a 8m │ /health                    │ │
│ │ POST     │ 200    │ 188ms    │ il y a 9m │ /store                     │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
│ Tail logs/demo_live_latest.txt (lecture seule)                             │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ [1/9] health OK · chain valid · 19 blocks                              │ │
│ │ [2/9] agents/run → graph_id=g_… PoL 0.60                               │ │
│ │ …                                                                      │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

### V8.1 — Sous-page : détail log demo_live JSON

```
┌─ Logs › demo_live_20260705_132451.json ────────────────────────────────────┐
│ { "steps": [ … ], "block_reward": 100000000, "similarity": 1.0 }           │
│                                              [Télécharger] [Copier]        │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## V9 — Console CLI (mode plein écran)

**Expertise :** PROTOCOLE — démo canonique = API + scripts, pas mock.  
**Inspiration :** terminal intégré + sortie `mine_learning_simple.py` / `demo_live.py`

### V9.0 — Vue Console (sidebar réduite ou masquée)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ ◆ ARTCB Console CLI                                    [DEBUG] [Plein écran]│
├──────────────────────────────────────────────────────────────────────────────┤
│ Onglets: [Terminal] [demo_live] [minage] [pytest] [api logs]               │
├──────────────────────────────────────────────────────────────────────────────┤
│ artcb@lvx:~/ARTCB/lvx$                                                     │
│                                                                            │
│ > Commandes rapides:                                                       │
│   make api              # démarrer FastAPI :8000                            │
│   python3 scripts/demo_live.py                                             │
│   python3 scripts/mine_learning_simple.py                                  │
│   pytest tests/ -q                                                         │
│   curl localhost:8000/api/v1/health | jq                                   │
│                                                                            │
│ artcb@lvx$ python3 scripts/demo_live.py                                    │
│ ┌──────────────────────────────────────────────────────────────────────────┐│
│ │ [1/9] GET /health → OK chain valid 19 blocks                             ││
│ │ [2/9] POST /agents/run → graph_id=g_… PoL 0.60                           ││
│ │ …                                                                        ││
│ │ [9/9] POST /store → block #20 signed reward 1.0 ARTCB                  ││
│ │ ✅ DEMO COMPLETE — logs/demo_live_latest.txt                             ││
│ └──────────────────────────────────────────────────────────────────────────┘│
│                                                                            │
│ artcb@lvx$ _                                                                 │
│                                                                            │
│ [Exécuter] [Copier] [Effacer]  ⚠ Exécution réelle — lire PROTOCOLE        │
└──────────────────────────────────────────────────────────────────────────────┘
```

### V9.1 — Sous-mode : minage CLI (sortie formatée)

```
┌─ Console › Minage ─────────────────────────────────────────────────────────┐
│ [6/6] Distribution rewards collectifs...                                   │
│   • Block reward          : 1.00000000 ARTCB                               │
│   • Reward mineur (100%)  : 1.00000000 ARTCB                               │
│   • Reward satoshi        : 100,000,000 sat                                │
│   • Balance totale        : 2.50000000 ARTCB                                 │
│ ─────────────────────────────────────────────────────────────────────────  │
│ ✅ MINAGE TERMINÉ — mining_results_*.json                                  │
└────────────────────────────────────────────────────────────────────────────┘
```

### V9.2 — Sous-mode : split Console + preview (optionnel)

```
┌─ Console CLI ────────────────────┬─ Preview ───────────────────────────────┐
│ $ demo_live.py running…          │ Graphe live (WS)                        │
│ [3/9] search nodes…            │   ●──●──●                               │
│                                │ PoL 0.60                                │
└────────────────────────────────┴─────────────────────────────────────────┘
```

---

## V10 — Groupes & Réseaux (NOUVEAU v1.5)

**Expertise :** multi-tenant + ACL wallet-native (inspiré Cursor Teams + Supermemory Organization).

### V10.0 — Sélecteur réseau (header global — toutes vues)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ ◆ ARTCB   [ Mon espace ▼ ]  PoL 0.60  [DEBUG]                              │
│           ┌─────────────────────┐                                          │
│           │ ● Privé (moi seul)  │  ← graphes/blocs personnels              │
│           │ ○ Groupe: Projet LVX│  ← espace collaboratif                   │
│           │ ○ Public            │  ← chaîne publique                       │
│           │ + Créer un groupe   │                                          │
│           └─────────────────────┘                                          │
└──────────────────────────────────────────────────────────────────────────────┘
```

### V10.1 — Liste des groupes

```
┌─ Groupes ──────────────────────────────────────────────────────────────────┐
│ [+ Créer un groupe]                                                         │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ Nom           │ Rôle     │ Membres │ Blocs │ Graphes │ Actions         │ │
│ │ Projet LVX    │ owner    │    4    │   12  │    8    │ [Ouvrir][Gérer] │ │
│ │ Équipe RAISE  │ contrib. │   12    │    3  │    2    │ [Ouvrir]        │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

### V10.2 — Créer un groupe

```
┌─ Groupes › Créer ──────────────────────────────────────────────────────────┐
│ Nom du projet: [ Projet LVX_________________________ ]                       │
│ Description:   [ Mémoire IR partagée hackathon_____ ]                       │
│ Votre wallet:  artcb1q7x… (owner automatique)                              │
│                              [Créer] [Annuler]                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### V10.3 — Membres & admins (fondateur protégé)

```
┌─ Groupe: Projet LVX › Membres ──────────────────────────────────────────────┐
│ Fondateur: artcb1alice…  🔒 PROTÉGÉ — non supprimable par les admins       │
│ Membres (4)                    [+ Inviter]  [Nommer admin] (fondateur seul) │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ Adresse             │ Rôle        │ Actions                          │ │
│ │ artcb1alice (vous)  │ 🔒 founder  │ [Dissoudre groupe] [Transférer]│ │
│ │ artcb1bob           │ admin       │ [Rétrograder] (fondateur)        │ │
│ │ artcb1car           │ contributor │ [Retirer] (admin+)               │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
│ ⚠ Un admin NE PEUT PAS retirer ou rétrograder le fondateur                │
└────────────────────────────────────────────────────────────────────────────┘
```

### V10.4 — Espace groupe actif (filtre toutes vues)

```
┌─ Projet LVX › Accueil (contexte GROUPE) ───────────────────────────────────┐
│ Réseau: GROUPE — visible uniquement par les 4 membres                      │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐                                     │
│ │ Graphes  │ │ Blocs    │ │ Rewards  │  ← agrégés groupe, pas perso        │
│ │    8     │ │   12     │ │  8.5 ₳   │                                     │
│ └──────────┘ └──────────┘ └──────────┘                                     │
│ [Mémoriser dans le groupe] [Voir graphe partagé] [Chaîne groupe]           │
│ ⚠ Les données privées (hors groupe) ne sont PAS visibles ici               │
└────────────────────────────────────────────────────────────────────────────┘
```

### V10.5 — Signer un bloc en mode groupe

```
┌─ Graphe › Signer bloc ─────────────────────────────────────────────────────┐
│ Visibilité:  ( ) Privé   (●) Groupe: Projet LVX   ( ) Public              │
│ Contributors groupe (PoL collectif):                                        │
│   Alice 0.80 · Bob 0.70 → reward 1 ARTCB split proportionnel              │
│                              [Signer bloc] [Annuler]                       │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Matrice pages / sous-pages / API

| Vue | Sous-pages | Endpoints / scripts |
|-----|------------|---------------------|
| V1 Accueil | Alertes DEBUG | `/health`, `/pol/score`, `/chain` |
| V2 Mémoriser | Empty, Session | `/agents/run`, WS `/ws`, `/demo/wailly-excerpt` |
| V3 Graphe | Search, Reconstruct, Nœud | `/graph/{id}`, `/search`, `/decode`, `/store` |
| V4 Chaîne | Détail bloc, Verify | `/chain`, `/chain/verify` |
| V5 Wallets | Créer, Rewards | `/wallet/*`, founders JSON |
| V6 Minage | Historique | `mining_results_*.json`, `mine_learning_simple.py` |
| V7 Système | Métriques | `/metrics`, fingerprint |
| V8 Logs | demo_live JSON | `logs/*` |
| V9 Console | demo_live, minage, split | scripts réels PROTOCOLE |
| V10 Groupes | Créer, Inviter, Espace groupe | `/groups/*` (**à créer**) |

---

## Checklist avant GO code

- [ ] Block reward **1 ARTCB** validé
- [ ] **Groupes/réseaux** validés (`GROUPES_RESEAUX_ARTCB.md`)
- [ ] Wireframes V10 Groupes OK
- [ ] Wireframes ASCII validés (ce document)
- [ ] 65 captures références OK
- [ ] Pivot dashboard vs CDC §9.3 : OUI/NON
- [ ] **GO code dashboard** explicite
