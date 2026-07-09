# Rapport 065 — Pool calcul distribué E2E (architecture crypto ML-KEM)

**Date :** 2026-07-09  
**Branche :** `cursor/pool-e2e-crypto-1fce`  
**Contact :** vgacofficiel@gmail.com

## Objectif

Réconcilier le **pool de calcul distribué opt-in** avec la règle **« calcul privé local »** : le texte d'apprentissage ne transite **jamais en clair** sur le réseau. Chaque worker exécute le raisonnement dual-agent **localement** après déchiffrement ML-KEM.

## Architecture crypto dédiée

```
Owner (coordinateur)                    Worker (pair opt-in)
─────────────────────                   ─────────────────────
split_text_chunks(text)
encrypt_chunk_payload → ML-KEM-768
  context: artcb-pool-chunk-v1
POST /pool/incoming (envelope) ────────► receive_incoming_chunk
                                        decrypt_chunk_payload (local)
                                        dual-agent run (local)
encrypt_result_payload
  context: artcb-pool-result-v1
◄──── POST /pool/jobs/{id}/results ────
decrypt_result_payload
finalize_job → MiningPipeline + contributors pool_worker
```

### Séparation des contextes KEM

| Contexte | Usage |
|----------|--------|
| `artcb-p2p-v1` | Sync blocs publics P2P |
| `artcb-pool-chunk-v1` | Morceaux texte vers workers |
| `artcb-pool-result-v1` | Résultats PoL vers owner |

Fichiers : `src/artcb/crypto/kem.py`, `src/artcb/pool/e2e.py`, `src/artcb/pool/service.py`

## API REST

Préfixe `/api/v1/pool` :

- `GET /status` — crypto, jobs, règle E2E
- `POST /jobs` — création + dispatch auto (workers = pairs découverts)
- `POST /incoming` — réception chunk chiffré (worker)
- `POST /incoming/process-all` — traitement local
- `POST /jobs/{id}/results` — callback résultat chiffré
- `POST /jobs/{id}/finalize` — bloc PoL + `contributors[]` avec rôle `pool_worker`

## Avant / Après

| Aspect | Avant | Après |
|--------|-------|-------|
| Pool réseau | Absent (pool_manager = PDF local) | Pool E2E ML-KEM opt-in |
| Texte sur réseau | N/A | **Jamais en clair** |
| Raisonnement | 100 % local par défaut | Local par worker ; distribution = chunks chiffrés |
| PoL collectif | reasoner seul | + `pool_worker` dans contributors |

## Validation 2 nœuds (VM)

Script : `python3 scripts/validate_two_nodes.py --spawn`

Nouvelles étapes : job pool chiffré A→B, process local B, finalize A avec `pool_worker`.

Log : `logs/validate_two_nodes_latest.json`

**Résultat VM (2026-07-09) :** 18/18 étapes OK — `pool_e2e_encrypted_opt_in: true`, `pool_plaintext_on_network: false`, `pool_workers_contribute_pol: true`.

## UI

Page `/network` — section **Pool calcul distribué (E2E ML-KEM)** : créer job, traiter incoming, finalize.

## Tests

```bash
python3 -m pytest tests/test_pool_e2e.py -q
python3 -m pytest tests/ -q
```

## Limites honnêtes

- Pas libp2p natif — HTTP entre API FastAPI
- Pas de fusion graphes IR entre nœuds — chaque worker garde son graphe local
- Pool = **opt-in** explicite ; hors pool, comportement inchangé (calcul 100 % local)
