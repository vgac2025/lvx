# Rapport 046 — Audit code source total + spec groupes fondateur/admin

**Horodatage :** 2026-07-07T05:00:00Z  
**Branche spec :** `cursor/dashboard-spec-1fce`  
**Périmètre :** 73 fichiers · **~8 497 lignes** (src + tests + scripts + frontend)  
**PROTOCOLE :** pas de mock · rapport avant/après · pas d’écrasement rapports antérieurs

---

## 1. Réponse — gestion admin + sécurité créateur

| Demande | Statut code actuel | Spec v1.1 |
|---------|-------------------|-----------|
| Nommer un membre **admin** | ❌ absent | ✅ **fondateur seul** peut promouvoir |
| Admin gère le groupe | ❌ absent | ✅ invite/retire (sauf fondateur) |
| Créateur d’origine **non supprimable** | ❌ absent | ✅ `founder_address` immuable |
| Seul le fondateur peut se retirer | ❌ absent | ✅ dissolve ou leave après transfert |
| Audit ligne par ligne | ✅ ce rapport | — |

**Document détaillé :** `GROUPES_RESEAUX_ARTCB.md` **v1.1** §4.6–4.8

---

## 2. Inventaire exhaustif fichiers source

### 2.1 `src/artcb/` — cœur Python (2 847 lignes)

| Fichier | Lignes | Rôle | Groupes | L1→Lfin audit |
|---------|--------|------|---------|---------------|
| `chain/manager.py` | 241 | Chaîne JSONL, rewards, visibility | **Partiel** | L22-52 `ChainBlock` a `visibility`+`contributors` sans `group_id`. L113-205 `append_block` anti-sybil si contributors. L207-228 reward 1 ARTCB (branche séparée). **Gap:** pas ACL lecture |
| `chain/ffi.py` | 107 | ctypes C hash | Aucun | L65-91 hash ignore visibility/contributors |
| `chain/__init__.py` | 6 | exports | — | — |
| `wallet/manager.py` | 184 | wallets locaux | **Partiel** | L52-89 create sans auth. L128-182 balance scan contributors. **Gap:** pas signature requêtes API |
| `wallet/address.py` | 138 | adresses artcb1 | **Partiel** | Identité future groupes |
| `wallet/__init__.py` | 8 | exports | — | — |
| `security/anti_sybil.py` | 229 | anti-Sybil | **Partiel** | L88-156 validate_block. **Non branché** API store |
| `security/slashing.py` | 341 | pénalités | **Partiel** | L138-211 slash. Pas lié balance API |
| `security/rate_limiter.py` | 263 | rate limit | **Partiel** | **Jamais importé** dans FastAPI |
| `security/__init__.py` | 10 | exports | — | — |
| `pol/scorer.py` | 97 | PoL + split_reward | **Partiel** | L88-96 split collectif — clé groupes |
| `pol/scorer_numpy.py` | 172 | batch PoL | Partiel | split_reward_batch |
| `pol/__init__.py` | 6 | exports | — | — |
| `ir/models.py` | 102 | IRGraph | Aucun | Pas owner/group_id sur graphe |
| `ir/encoder.py` | 239 | encode texte | Aucun | — |
| `ir/decoder.py` | 108 | reconstruct | Aucun | — |
| `ir/llm_encoder.py` | 54 | LLM layer | Aucun | — |
| `ir/bob_client.py` | 126 | Bob API | Aucun | — |
| `ir/compression.py` | 101 | gzip graphs | Aucun | — |
| `ir/symbols.py` | 60 | symboles | Aucun | — |
| `ir/grammar.py` | 91 | types nœuds | Aucun | — |
| `ir/macros.py` | 89 | macros | Aucun | — |
| `ir/__init__.py` | 8 | exports | — | — |
| `agents/critic.py` | 92 | validation PoL | Aucun | — |
| `agents/explorer.py` | 25 | décomposition | Aucun | — |
| `agents/pool_manager.py` | 174 | pools parallèles | Aucun | — |
| `agents/__init__.py` | 7 | exports | — | — |
| `memory/graph_store.py` | 93 | disque graphs | Aucun | Flat dir, pas `data/groups/` |
| `memory/vector_store.py` | 57 | search keyword | Aucun | — |
| `memory/vector_store_faiss.py` | 186 | FAISS | Aucun | Non utilisé AppState |
| `memory/node_index.py` | 174 | index nœuds | Aucun | — |
| `memory/__init__.py` | 7 | exports | — | — |
| `rtleg/events.py` | 25 | événements | Aucun | session_id ≠ group_id |
| `rtleg/timeline.py` | 43 | timeline | Aucun | — |
| `rtleg/__init__.py` | 7 | exports | — | — |
| `config.py` | 67 | settings .env | Aucun | Pas knobs groupes |
| `io/pdf_loader.py` | 84 | PDF sync | Aucun | — |
| `io/pdf_loader_async.py` | 100 | PDF async | Aucun | — |
| `io/__init__.py` | 1 | marker | — | — |
| `logging_config.py` | 55 | logs JSON | Aucun | — |
| `__init__.py` | 4 | version | — | — |
| `tokenomics.py` | — | *branche block-reward* | — | INITIAL 1 ARTCB |

### 2.2 `src/api/` — FastAPI (664 lignes)

| Fichier | Lignes | Rôle | Groupes | Audit critique |
|---------|--------|------|---------|----------------|
| `routes.py` | 431 | REST | **Partiel** | L36-39 `StoreRequest.visibility` seul. **L178-225 store** sans auth/contributors/group_id. L228-232 chain_list **non filtré**. L321-373 wallet **ouvert** |
| `deps.py` | 71 | AppState | Aucun | Graph store global, pas partition groupe |
| `main.py` | 40 | factory | Aucun | Pas middleware auth/rate-limit |
| `websocket.py` | 122 | WS encode | Aucun | session_id ouvert |

### 2.3 `src/c/` — blockchain C (260 lignes)

| Fichier | Lignes | Groupes | Audit |
|---------|--------|---------|-------|
| `libartcb_chain.c` | 194 | Aucun | L43-68 canonical 7 champs — **ignore** visibility, contributors, group_id |
| `libartcb_chain.h` | 41 | Aucun | Struct sans champs groupe |
| `test_chain.c` | 25 | Aucun | Tests hash basiques |

### 2.4 `frontend/src/` — React (789 lignes)

| Fichier | Lignes | Groupes | Audit |
|---------|--------|---------|-------|
| `pages/Demo.tsx` | 278 | Aucun | L19 SESSION_ID fixe. L124-147 store sans visibility |
| `api/client.ts` | 70 | Aucun | storeGraph sans visibility/group_id |
| `types.ts` | 44 | Aucun | ChainBlock sans visibility |
| Composants | 421 | Aucun | Pas UI groupe/admin |

### 2.5 `tests/` — 1 357 lignes · **0 test groupes**

### 2.6 `scripts/` — 1 580 lignes

| Script | Groupes | Note |
|--------|---------|------|
| `mine_learning_simple.py` | Partiel | contributors L186-190, security off L95 |
| `mine_learning.py` | Cassé | imports invalides |
| `demo_live.py` | Aucun | pas visibility |
| `create_founders_wallets.py` | Partiel | founders ≠ groupes |

---

## 3. Synthèse module par module — % prêt groupes

```mermaid
flowchart LR
    subgraph OK["Prêt partiel"]
        CH[chain visibility]
        PO[pol split_reward]
        WA[wallet address]
        SE[security modules]
    end
    subgraph NO["Absent"]
        GR[GroupManager]
        API[/groups API]
        ACL[ACL filtrage]
        AUTH[auth signature]
        UI[V10 dashboard]
    end
    OK --> GR
    GR --> API --> ACL --> AUTH --> UI
```

| Module | Lignes | % groupes |
|--------|--------|-----------|
| chain | 354 | 15 % |
| wallet | 330 | 20 % |
| security | 843 | 10 % (non branché API) |
| api | 664 | 5 % |
| ir/memory/agents | 1 800 | 0 % |
| frontend | 789 | 0 % |
| **Total** | **~8 497** | **~8 %** |

---

## 4. Règles fondateur/admin (spec validée en attente)

Voir `GROUPES_RESEAUX_ARTCB.md` v1.1 §4.6 — résumé :

| Action | Fondateur | Admin | Contributor |
|--------|-----------|-------|-------------|
| Promouvoir → admin | ✅ seul | ❌ | ❌ |
| Rétrograder admin | ✅ seul | ❌ | ❌ |
| Retirer membre | ✅ | ✅ sauf fondateur | ❌ |
| Retirer/dégrader fondateur | ❌ **INTERDIT** | ❌ | ❌ |
| Quitter le groupe | ✅ dissolve ou transfert | ✅ | ✅ |
| Dissoudre groupe | ✅ seul | ❌ | ❌ |

**Invariant code (à implémenter) :**
```python
if target == group.founder_address:
    raise Forbidden("FOUNDER_IMMUTABLE")  # sauf self_leave/dissolve
```

---

## 5. Plan implémentation (ordre PROTOCOLE)

| Phase | Fichiers à créer/modifier | Gate |
|-------|---------------------------|------|
| G1 | `src/artcb/groups/manager.py`, tests | fondateur immuable |
| G2 | `api/routes.py` + middleware signature | pytest ACL |
| G3 | `chain/manager.py` + `group_id`, filtres GET | pas mock |
| G4 | `libartcb_chain.c` hash étendu | C tests |
| G5 | frontend V10 + wireframes | GO dashboard |

---

## 6. Avancement global

| Composant | % |
|-----------|---|
| Audit code total | **100 %** (ce rapport) |
| Spec groupes fondateur/admin | **100 %** (doc) |
| Code groupes | **0 %** |
| Dashboard | **50 %** spec |

---

**Prochaine étape :** votre validation spec §7 `GROUPES_RESEAUX_ARTCB.md` + **GO groupes backend**.
