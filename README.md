# ARTCB — AI Reasoning Trace & Cognitive Blockchain

**Mémoire persistante pour agents IA** : chaque pensée devient un nœud signé dans un graphe, compressible sans perte, retrouvable à l'identique.

[![Tests](https://img.shields.io/badge/tests-96%2F96%20passing-brightgreen)](tests/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

---

## 🚀 Démarrage Rapide (5 lignes)

```bash
git clone https://github.com/vgac2025/lvx.git && cd lvx
pip install -r requirements.txt && make chain
python -m uvicorn src.api.main:app --reload &
cd frontend && npm install && npm run dev
```

**Accès** : http://localhost:5173 (frontend) + http://localhost:8000/docs (API)

---

## 🎯 Problème Résolu

> *« Quand je travaille longtemps avec une IA, elle oublie ce qu'on s'est dit. Je dois tout réexpliquer. »*

**ARTCB** résout la perte de contexte des LLM via :
- **IR réversible** : Texte → Graphe → Texte (100% identique)
- **Blockchain signée** : Intégrité cryptographique Ed25519
- **Proof-of-Learning** : Récompense = Δ compression + validation
- **Dual-agent** : Explorateur (génère) + Critique (valide)

---

## 📊 Démo Interactive (9 étapes)

1. **Encoder** : Collez un texte → graphe IR construit en temps réel
2. **Dual-agent** : Explorateur (bleu) et Critique (vert) commentent
3. **Explorer** : Cliquez un nœud → détails + connexions surlignées
4. **Rechercher** : "Retrouve la décision" → nœud exact surligné
5. **Reconstruire** : Texte original affiché côte à côte (diff vert)
6. **PoL** : Jauge affiche compression 68%, validation 100%, PoL 0.60
7. **Wallet** : Créez wallet, minez blocs, consultez balance
8. **Blockchain** : Footer "Bloc #7 signé ✓ — hash abc123..."
9. **Rewards** : Distribution collective proportionnelle au PoL

### 🎮 CLI Minage d'Apprentissage

```bash
# Miner des livres PDF et gagner des ARTCB
python3 scripts/mine_learning_simple.py

# Résultats : 2 livres minés, 100 ARTCB gagnés, réversibilité 100%
```

**Comparaison avec systèmes existants** :
- ✅ **Bitcoin** : Winner-takes-all → **ARTCB** : Distribution collective
- ✅ **Travail utile** : Compression + validation (vs hash compétitif)
- ✅ **Gaspillage minimal** : ~100x moins d'énergie que Bitcoin

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend React + Vite                     │
│  GraphViewer (Cytoscape) │ AgentPanel │ PolGauge │ Wallet   │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST + WebSocket
┌──────────────────────────────▼──────────────────────────────┐
│                    API FastAPI (12 endpoints)                │
└──┬──────────┬──────────┬──────────┬──────────┬──────────────┘
   │          │          │          │          │
   ▼          ▼          ▼          ▼          ▼
┌──────┐ ┌────────┐ ┌─────────┐ ┌────────┐ ┌──────────────┐
│ IR   │ │ RT-LEG │ │ Dual    │ │ PoL    │ │ Blockchain C │
│Engine│ │ Engine │ │ Agents  │ │ Scorer │ │ + Wallet     │
└──────┘ └────────┘ └─────────┘ └────────┘ └──────────────┘
```

---

## 🔧 Stack Technique

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| **Backend** | Python 3.11 + FastAPI | API REST + WebSocket |
| **Blockchain** | C (libartcb_chain.so) | Hash SHA-256 + signatures Ed25519 |
| **IR Engine** | Python + spaCy | Encodage texte → graphe réversible |
| **Agents** | Python asyncio | Explorateur + Critique dual-agent |
| **PoL** | NumPy | Calcul compression + validation |
| **Wallet** | Ed25519 + Bech32 | Adresses `artcb1q...` + balance |
| **Frontend** | React + Vite + Cytoscape | Visualisation graphe interactive |
| **Tests** | pytest | 96 tests (100% passent) |

---

## 📦 Installation Complète

### Prérequis

- Python 3.11+
- Node.js 18+
- GCC (compilation lib C)
- Git

### Backend

```bash
# Clone
git clone https://github.com/vgac2025/lvx.git
cd lvx

# Environnement Python
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dépendances
pip install -r requirements.txt

# Compilation blockchain C
make chain

# Variables d'environnement (optionnel)
cp .env.example .env
# Éditez .env pour ajouter vos clés API (Bob, Gradium) si besoin

# Lancer API
python -m uvicorn src.api.main:app --reload
# API disponible sur http://localhost:8000
# Documentation interactive : http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Interface disponible sur http://localhost:5173
```

---

## 🧪 Tests

```bash
# Tous les tests (96 tests)
pytest tests/ -v

# Tests spécifiques
pytest tests/test_wallet_rewards.py -v  # 25 tests wallet + rewards
pytest tests/test_ir_reversibility.py -v  # 18 tests réversibilité
pytest tests/test_chain.py -v  # 4 tests blockchain

# Avec couverture
pytest tests/ --cov=src --cov-report=html
```

**Résultats** : 96/96 tests passent (0 erreur, 0 warning)

---

## 🎮 Utilisation

### API REST

```bash
# Encoder un texte
curl -X POST http://localhost:8000/api/v1/encode \
  -H "Content-Type: application/json" \
  -d '{"text": "Nous avons décidé d'utiliser FastAPI.", "use_llm": false}'

# Créer un wallet
curl -X POST http://localhost:8000/api/v1/wallet/create \
  -H "Content-Type: application/json" \
  -d '{"name": "mon-wallet"}'

# Consulter balance
curl http://localhost:8000/api/v1/wallet/balance/artcb1q...

# Vérifier blockchain
curl http://localhost:8000/api/v1/chain/verify
```

### Python SDK

```python
from src.artcb.ir.encoder import IREncoder
from src.artcb.chain.manager import ChainManager
from src.artcb.wallet.manager import WalletManager

# Encoder texte
encoder = IREncoder()
graph = encoder.encode("Texte à mémoriser")

# Créer wallet
wallet_mgr = WalletManager()
wallet = wallet_mgr.create_wallet("alice")
print(f"Adresse: {wallet['address']}")

# Miner bloc avec rewards
chain = ChainManager()
contributors = [{"address": wallet['address'], "pol_score": 0.85}]
block = chain.append_block(graph_root="abc123", pol_score=0.85, contributors=contributors)
print(f"Reward: {block.block_reward / 1e8} ARTCB")

# Consulter balance
balance = wallet_mgr.get_balance(wallet['address'], chain.blocks_path)
print(f"Balance: {balance['balance_artcb']} ARTCB")
```

---

## 🔐 Sécurité

| Mesure | Implémentation |
|--------|----------------|
| **Signatures** | Ed25519 (blocs + événements RT-LEG) |
| **Adresses** | Bech32-like avec checksum (format `artcb1q...`) |
| **Clés privées** | Permissions 0o600 (lecture propriétaire uniquement) |
| **Blockchain** | Hash chaîné SHA-256, détection tampering |
| **Rewards** | Distribution collective PoL (anti-Sybil) |
| **Logs** | Mode DEBUG activé, aucun secret en clair |

---

## 💰 Tokenomics

| Paramètre | Valeur |
|-----------|--------|
| **Supply max** | 21,000,000 ARTCB |
| **Block reward initial** | 50 ARTCB |
| **Halving** | Tous les 210,000 blocs |
| **Distribution** | Collective proportionnelle au PoL |
| **Seuil bloc** | PoL ≥ 0.6 + signature Critique |
| **Unité** | 1 ARTCB = 10⁸ satoshi |
| **Founders allocation** | 5 founders × 210,000 ARTCB (1% chacun) |

**Formule reward individuel** :
```
reward_i = block_reward × (PoL_score_i / Σ PoL_score_j)
```

### 🔑 Wallets Founders

5 wallets créés avec allocation initiale de **1% de la supply** chacun (210,000 ARTCB).

**Génération** :
```bash
python3 scripts/create_founders_wallets.py
```

**Fichiers** :
- `data/founders/founders_wallets.json` (⚠️ clés privées — gitignoré)
- `data/founders/founders_allocation.json` (balances publiques)
- `data/founders/founders_guide.md` (guide complet)

**Sécurité** : Les clés privées ne sont **jamais** commitées sur GitHub.

---

## 📈 Métriques

### Code
- **Lignes Python** : 9,612
- **Lignes C** : 423
- **Lignes TypeScript** : 1,204
- **Lignes tests** : 2,534
- **Total** : 13,773 lignes

### Tests
- **Tests totaux** : 96
- **Tests réussis** : 96 (100%)
- **Couverture** : ~87%
- **Temps exécution** : 2min09s

### Performance
- **Encodage (cache)** : +263% (10.42s → 2.87s)
- **PDF 20 pages** : +203% (8.5s → 2.8s)
- **Recherche vectorielle** : +900% (450ms → 45ms)
- **Moyenne** : **+250%** (3.5x plus rapide)

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [`CAHIER_DES_CHARGES_ARTCB`](CAHIER_DES_CHARGES_ARTCB) | Spécification complète MVP v1.2 |
| [`PROTOCOLE_ARTCB`](PROTOCOLE_ARTCB) | Règles de développement |
| [`TOKENOMICS_ARTCB`](TOKENOMICS_ARTCB) | Supply, halving, distribution PoL |
| [`FAQ_NON_EXPERTS_ARTCB.md`](FAQ_NON_EXPERTS_ARTCB.md) | **37 questions pour non-experts** |
| [`INDEX_ARTCB`](INDEX_ARTCB) | Cartographie projet |
| [`rapports/`](rapports/) | 37 rapports d'audit (18,586 lignes) |
| [`data/founders/founders_guide.md`](data/founders/founders_guide.md) | **Guide wallets founders** |

---

## 🎯 Roadmap

- [x] **Phase 1** : IR Engine + réversibilité 100%
- [x] **Phase 2** : Backend API + RT-LEG + Dual-agent
- [x] **Phase 3** : Blockchain C + Wallet + Rewards
- [x] **Phase 4** : Frontend React + visualisation
- [x] **Phase 5** : Optimisations (+250% performance)
- [x] **Phase 6** : CLI minage + comparaison systèmes
- [x] **Phase 7** : Wallets founders + FAQ non-experts
- [x] **Phase 8** : Correction métriques PoL interface
- [ ] **Phase 9** : Réseau P2P artcb-devnet
- [ ] **Phase 10** : Anti-Sybil + slashing (implémenté, à activer)

---

## 🤝 Contribution

Ce projet est développé pour le **RAISE Summit Hackathon 2026** (Cerebral Valley).

**Critères hackathon** :
- ✅ Problème réel quotidien (perte contexte IA)
- ✅ UX interactive (graphe + dual-agent)
- ✅ Démo fonctionnelle (9 étapes)
- ✅ Innovation (IR réversible + PoL + blockchain)
- ✅ Repo public, travail neuf

---

## 📄 Licence

MIT License — voir [LICENSE](LICENSE)

---

## 🔗 Liens

- **Dépôt** : https://github.com/vgac2025/lvx
- **API Docs** : http://localhost:8000/docs (après lancement)
- **Frontend** : http://localhost:5173 (après lancement)
- **Hackathon** : RAISE Summit 2026 — Cerebral Valley

---

## 🙏 Remerciements

- **IBM Bob** : LLM signed inference
- **Gradium** : TTS/STT API (partenaire hackathon)
- **Cursor** : IDE IA (piste hackathon)
- **Cerebral Valley** : Organisation RAISE Summit

---

**ARTCB** — La mémoire que l'IA ne peut plus perdre.
