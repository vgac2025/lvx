# Rapport 066 — Pool E2E complet : choix utilisateur, private/public/group, tests stress

**Date :** 2026-07-09  
**Branche :** `cursor/pool-e2e-crypto-1fce` → merge `main`  
**Contact :** vgacofficiel@gmail.com

## Objectif livré

Intégration **complète bout en bout** du pool distribué avec architecture crypto dédiée, sans code incomplet :

- Choix utilisateur : **calcul local** OU **pool distribué opt-in**
- Chiffrement **ML-KEM obligatoire** si distribué (refus explicite sinon)
- Visibilités **private / public / group** sur pool + minage
- UI + API + orchestrateur + politique sécurité
- Tests unitaires, intégration, stress

## Choix utilisateur (API + UI)

| Option | Comportement |
|--------|--------------|
| `use_distributed_pool=false` | Pipeline local classique — 100 % machine |
| `use_distributed_pool=true` | Pool E2E — chunks/résultats ML-KEM |
| `encrypt_transport=false` + distribué | **Refusé** (HTTP 400) |
| `visibility` | `private` \| `public` \| `group` |
| `group_id` | Obligatoire si `group` + vérif membre |

Endpoints :
- `POST /api/v1/pool/run` — point d'entrée unifié
- `POST /api/v1/mining/pipeline` — flag `use_distributed_pool`
- `GET/PUT /api/v1/pool/preferences` — préférences persistées

UI :
- `/memorize` — toggle « calcul distribué (pool E2E) »
- `/network` — pool + visibilité footer (PRIVÉ/GROUPE/PUBLIC)
- `DashboardContext` — `useDistributedPool`, `encryptTransport`

## Architecture crypto (inchangée, renforcée)

- `artcb-pool-chunk-v1` — morceaux vers workers
- `artcb-pool-result-v1` — résultats vers owner
- Callback local optimisé (même nœud = pas de HTTP loopback)

## Fichiers ajoutés / modifiés

- `src/artcb/pool/policy.py` — règles sécurité
- `src/artcb/pool/preferences.py` — préférences
- `src/artcb/pool/orchestrator.py` — cycle local/distribué
- `src/artcb/pool/discovery.py` — workers P2P
- `tests/test_pool_policy.py`
- `tests/test_pool_integration.py` — private/public/group
- `tests/test_pool_stress.py` — volume + concurrence

## Validation

```bash
python3 -m pytest tests/ -q          # 205 passed
python3 scripts/validate_two_nodes.py --spawn  # 18/18 OK
```

## Règle PROTOCOLE respectée

- **Par défaut** : calcul privé local
- **Pool** : opt-in explicite, jamais texte clair réseau
- **Raisonnement** : toujours local par worker après déchiffrement
