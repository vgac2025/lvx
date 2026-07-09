# Rapport 067 — Audit API/CLI complet bout en bout

**Date :** 2026-07-09T01:35:00Z  
**Branche :** `cursor/api-cli-audit-1fce` → `main`  
**Contact :** vgacofficiel@gmail.com  
**Avancement système : ~95 %**

---

## Objectif

Vérifier que l'API complète est utilisable via **CLI terminal** et **Console UI** sur tous les systèmes (Python 3.11+), conforme PROTOCOLE et AUTO_PROMPT.

---

## Avant / Après

| Aspect | Avant | Après |
|--------|-------|-------|
| CLI API | `ir_cli.py` (encode/decode seulement) | `artcb_cli.py` — 12 modules commande |
| Console UI | 12 commandes basiques | 25+ commandes (pool, p2p, connectors…) |
| Doc API | §8 CDC (12 routes) | `API_REFERENCE_ARTCB.md` (~70 routes) |
| Tests CLI | Aucun | `test_artcb_cli.py` (5 tests) |
| LISTE_TESTS | 134 pytest | 210 pytest |
| README | 96 tests | 210 tests + section CLI |

---

## Inventaire API (audit code source)

| Module routes | Fichier | Endpoints |
|---------------|---------|-----------|
| Core | `routes.py` | encode, decode, graph, store, chain, wallet, agents |
| Minage | `mining_routes.py` | pipeline, bulk |
| Pool E2E | `pool_routes.py` | run, jobs, incoming, preferences, finalize |
| P2P | `p2p_routes.py` | peers, sync, blocks |
| Groupes | `groups_routes.py` | CRUD, join-requests |
| Gouvernance | `governance_routes.py` | proposals, vote |
| Connecteurs | `connectors_routes.py` | multimodal, learn |
| Notifications | `notifications_routes.py` | Telegram |
| Dashboard | `dashboard_routes.py` | logs, mining status |

---

## CLI `scripts/artcb_cli.py`

```bash
python3 scripts/artcb_cli.py health
python3 scripts/artcb_cli.py pool run --text "..." --distributed --visibility group --group-id g_xxx
python3 scripts/artcb_cli.py mining pipeline --text "..." --visibility public
python3 scripts/artcb_cli.py p2p sync
```

Variable : `ARTCB_API_BASE` (défaut `http://127.0.0.1:8000`)

---

## Validation exécutée

```bash
python3 -m pytest tests/ -q                    # 210 passed
python3 scripts/validate_two_nodes.py --spawn   # 18/18 OK
python3 scripts/artcb_cli.py --help             # OK
```

Logs lus : `logs/validate_two_nodes_latest.json`

---

## Fichiers mis à jour (PROTOCOLE)

| Fichier | Action |
|---------|--------|
| `API_REFERENCE_ARTCB.md` | **Créé** |
| `scripts/artcb_cli.py` | **Créé** |
| `frontend/src/pages/Console.tsx` | Étendu |
| `frontend/src/console/commands.ts` | **Créé** |
| `CAHIER_DES_CHARGES_ARTCB` | v1.4 §8 |
| `ROADMAP_GENERAL_ARTCB` | Phase 8–9 ✅ |
| `LISTE_TESTS_ARTCB.md` | §7–8 pool/CLI |
| `AUTO_PROMPT_ARTCB` | Horodatage audit |
| `README.md` | CLI + 210 tests |

---

## Limites honnêtes (PROTOCOLE)

- libp2p natif : non — HTTP gossip
- CLI nécessite API démarrée (`uvicorn` ou `scripts/start_api.sh`)
- Faucet devnet : non implémenté
- Gradium TTS : P1

---

## Conclusion

L'API est **à jour et fonctionnelle** pour usage CLI/CMD et Console web. Choix utilisateur pool/local et visibilités private/public/group documentés et testés.
