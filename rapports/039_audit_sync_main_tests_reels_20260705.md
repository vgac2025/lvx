# Rapport 039 — Audit + tests réels après sync main (2026-07-05)

**Horodatage :** 2026-07-05T09:33:09Z  
**Commit audité :** `3bdd350` (pull `7ba3d37..3bdd350`, 107 fichiers)  
**Machine :** Cloud Agent (`hostname=cursor`, `execution_env=CLOUD_AGENT`)

---

## 1. Avant (état local obsolète)

| Élément | Avant pull |
|---------|------------|
| Commit local | `7ba3d37` |
| Tests connus | 42 |
| Rapports | 000→013 |
| Wallet / minage / sécurité | absents localement |

---

## 2. Sync dépôt distant

```bash
git pull origin main   # Fast-forward 107 files, +24709 lignes
```

**Nouveautés majeures intégrées :**
- Wallet + rewards collectifs (`src/artcb/wallet/`, `chain/manager.py`)
- Sécurité : anti-Sybil, rate limiter, slashing
- 10 optimisations (FAISS, async PDF, pool agents, etc.)
- Scripts : `mine_learning_simple.py`, `benchmark_performance.py`, `create_founders_wallets.py`
- **96 tests** (vs 42 avant)
- Rapports 014→038, FAQ, benchmark concurrents, hackathon docs

---

## 3. Tests réels exécutés (après pull)

### 3.1 Build + pytest

**Commande :** `make chain && python3 -m pytest tests/ -v`  
**Log :** `logs/audit_tests_20260705_agent_refresh.log`

```
96 passed, 8 warnings in 18.10s
```

### 3.2 Démo live API (9 étapes)

**Commande :** `python3 scripts/demo_live.py`  
**Log :** `logs/demo_live_latest.txt`

```
graph_id=g_b634a1e7f852 pol=0.6
reversible=True similarity=1.0
chain valid=True blocks=10
=== DEMO COMPLETE ===
```

**JSON :** `logs/demo_live_20260705_093309.json` — `"ok": true`

### 3.3 Script complet

**Commande :** `bash scripts/run_real_local.sh`  
**Log :** `logs/audit_run_real_20260705.log` — OK

### 3.4 Minage apprentissage

**Commande :** `python3 scripts/mine_learning_simple.py`  
**Log :** `logs/mining_agent_refresh_20260705.log`

- Wailly : ✅ bloc #8, 50 ARTCB, réversibilité 100 %
- Quintus : ❌ `data/fixtures/quintus_de_smyrne_la_fin_de_l_iliade.pdf` **introuvable**

### 3.5 Benchmark performance

**Commande :** `python3 scripts/benchmark_performance.py`  
**Log :** `logs/benchmark_agent_refresh_20260705.log`

```
✅ NF-01: Encodage 500 mots < 2s
✅ NF-02: Reconstruction < 1s
```

### 3.6 Chaîne C

```
verify_chain_file → valid=True, 10 blocs (après run_real_local)
```

### 3.7 Health API

```json
{"status":"ok","debug":true,"chain":{"valid":true,"block_count":10}}
```

---

## 4. Problèmes détectés (à notifier)

| # | Gravité | Problème | Détail |
|---|---------|----------|--------|
| P1 | **Moyenne** | PDF Quintus absent | INDEX/rapports 037 disent « livre 2 ajouté » — fichier **pas dans le repo** (`data/fixtures/` = Wailly seul). `.gitignore` bloque `*.pdf` sauf Wailly. |
| P2 | **Moyenne** | `pyproject.toml` incomplet | `faiss-cpu`, `numpy`, `aiofiles`, `psutil`, `pytest-asyncio` dans `requirements.txt` mais **pas** dans `pyproject.toml` → `pip install -e ".[dev]"` seul **échoue** sur 19 tests (ImportError aiofiles). |
| P3 | Faible | 8 DeprecationWarning | `anti_sybil.py` utilise `datetime.utcnow()` (lignes 118, 172) |
| P4 | Info | Compression négative | Benchmark : `-1062%` — IR JSON > texte brut (attendu MVP, pas bug crash) |
| P5 | Info | `miner_address` incorrect | `mining_results_*.json` : champ = chemin PDF, pas adresse wallet Bech32 |
| P6 | Info | INDEX désynchronisé | INDEX cite commit `c7fca71` ; réel = `3bdd350` |
| P7 | **Rappel user** | Exécution cloud ≠ PC user | `machine_fingerprint.txt` → `execution_env=CLOUD_AGENT` |
| P8 | Info | Pas de réseau P2P | `artcb-devnet` toujours non déployé (local JSONL seulement) |

**Aucun test en échec.** **Aucun crash API.** Démo 9 étapes **OK**.

---

## 5. État d'avancement (%)

| Phase | % | Note |
|-------|---|------|
| 0 Spec | 100 % | |
| 1 IR | 100 % | réversibilité 1.0 |
| 2 Backend | 100 % | API + WS + wallet routes |
| 3 Blockchain C | **92 %** | rewards + contributors OK ; devnet P2P manquant |
| 4 Frontend | 100 % | optionnel |
| Tests auto | **100 %** | 96/96 |
| Démo API | **100 %** | |
| Exécution PC utilisateur | **0 %** | à faire chez vous |
| **Global MVP** | **~96 %** | |

---

## 6. Commandes pour reproduire (votre PC)

```bash
git pull origin main
pip install -r requirements.txt    # pas seulement pyproject
bash scripts/setup_machine_locale.sh
bash scripts/run_real_local.sh
```

Secrets : `cp ENV_A_REMPLIR_ARTCB .env`

---

## 7. Checklist PROTOCOLE

| Règle | Statut |
|-------|--------|
| Pull dernière version | ✅ |
| Tests réels exécutés | ✅ 96/96 |
| Logs lus après exécution | ✅ |
| Rapport .md nouveau | ✅ (ce fichier) |
| Avant / après | ✅ §1–3 |
| Problèmes notifiés | ✅ §4 |
| Pas de mensonge sur local | ✅ cloud explicité |
