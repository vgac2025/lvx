# Rapport 043 — Audit frais (dépôt déjà à jour fce16ad)

**Horodatage :** 2026-07-05T13:24:51Z  
**Commit :** `fce16ad` — `git pull` → **Already up to date**  
**Machine :** Cloud Agent (`execution_env=CLOUD_AGENT`)

---

## 1. Avant / après sync

| | Avant | Après |
|---|-------|-------|
| Commit | `fce16ad` | `fce16ad` (aucun nouveau commit distant) |
| Nouveautés pull | — | Rien de plus depuis rapport 042 |

---

## 2. Tests réels exécutés (cette session)

| Test | Résultat | Log |
|------|----------|-----|
| `pytest` | **96/96 OK** (20s) | `logs/audit_tests_20260705_1323.log` |
| `demo_live.py` | **OK** | `logs/demo_live_20260705_132451.json` |
| `run_real_local.sh` | **OK** — 19 blocs | `logs/audit_run_real_20260705_1323.log` |
| `benchmark_performance.py` | NF-01, NF-02 OK | `logs/benchmark_20260705_1323.log` |
| `mine_learning_simple.py` | Wailly OK | `logs/mining_20260705_1323.log` |
| Chaîne C | valid=True, 19 blocs | — |
| `/health`, `/metrics`, `/wallet/list` | OK (après restart API) | — |

**Démo (`logs/demo_live_latest.txt`) :**
```
pol=0.6
reversible=True similarity=1.0
chain valid=True blocks=19
=== DEMO COMPLETE ===
```

---

## 3. Problèmes rencontrés

| # | Gravité | Problème |
|---|---------|----------|
| **P1** | **Moyenne** | **PDF Quintus absent** — minage livre 2 échoue |
| **P2** | **Moyenne** | **API instable** — 1er `demo_live` → `Connection refused` (API pas prête) ; OK après redémarrage |
| **P3** | Faible | Deux rapports `039_*` (numérotation dupliquée) |
| **P4** | Info | Compression négative (-533 %) |
| **P5** | Info | Exécution Cloud Agent, pas PC utilisateur |
| **P6** | Info | Pas de devnet P2P |

**0 test en échec. 0 warning pytest.**

---

## 4. Avancement MVP : **~96 %**

---

## 5. Note utilisateur

Le message citait le rapport **040** (`16f9051`) — obsolète.  
État actuel : **042** + ce rapport **043** sur commit **`fce16ad`**.
