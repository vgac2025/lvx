# LISTE TESTS ARTCB — Registre cumulatif

**Horodatage création :** 2026-07-07T05:15:00Z  
**Branche dev :** `cursor/dashboard-dev-1fce`  
**Règle PROTOCOLE :** cette liste est **cumulative** — ne jamais supprimer un test, cocher `[x]` quand passé, ajouter horodatage.

**Avancement tests dashboard : 100 %** (UI) — **sécurité invitations Solution 2 : 100 %** (T-G09–G12)

---

## 1. Tests backend existants (baseline — toujours exécuter)

| ID | Commande | Attendu | Statut | Dernière exec |
|----|----------|---------|--------|---------------|
| T-B01 | `python3 -m pytest tests/ -q` | 96+ passed | [x] | 2026-07-07 (134) |
| T-B02 | `python3 -m pytest tests/test_wallet_rewards.py -q` | all pass, reward 1 ARTCB | [x] | 2026-07-07 |
| T-B03 | `python3 -m pytest tests/test_pol.py -q` | split 1.0 ARTCB | [x] | 2026-07-07 |
| T-B04 | `python3 -m pytest tests/test_api.py -q` | API OK | [x] | 2026-07-07 |
| T-B05 | `python3 -m pytest tests/test_chain.py -q` | C verify OK | [x] | 2026-07-07 |
| T-B06 | `python3 scripts/demo_live.py` | 9/9 steps OK | [x] | 2026-07-07 |
| T-B07 | `curl -s localhost:8000/api/v1/health \| jq .status` | `"ok"` | [x] | 2026-07-07 |

---

## 2. Tests groupes (nouveau — dashboard phase)

| ID | Commande / scénario | Attendu | Statut | Dernière exec |
|----|---------------------|---------|--------|---------------|
| T-G01 | `pytest tests/test_groups.py::test_create_group` | founder immuable | [x] | 2026-07-07 |
| T-G02 | `test_founder_cannot_be_removed_by_admin` | 403 FOUNDER_IMMUTABLE | [x] | 2026-07-07 |
| T-G03 | `test_only_founder_promotes_admin` | admin role set | [x] | 2026-07-07 |
| T-G04 | `test_admin_cannot_promote_admin` | 403 | [x] | 2026-07-07 |
| T-G05 | `test_dissolve_group_founder_only` | groupe archivé | [x] | 2026-07-07 |
| T-G06 | `POST /groups` + `GET /groups` API | données réelles JSON | [x] | 2026-07-07 |
| T-G07 | `POST /store` visibility=group + group_id | bloc scoped | [x] | 2026-07-07 |
| T-G08 | `GET /chain?group_id=` filtre | membres only | [x] | 2026-07-07 |
| T-G09 | `test_create_group_has_join_code` | join_code 8 car. | [x] | 2026-07-07 |
| T-G10 | `test_direct_invite_blocked_by_default` | 403 join-request | [x] | 2026-07-07 |
| T-G11 | `test_join_request_flow` | sign + approve + member | [x] | 2026-07-07 |
| T-G12 | `test_reject_join_request` | rejected, pas membre | [x] | 2026-07-07 |

---

## 3. Tests frontend dashboard (nouveau)

| ID | Scénario | Attendu | Statut | Dernière exec |
|----|----------|---------|--------|---------------|
| T-F01 | `cd frontend && npm run build` | 0 errors | [x] | 2026-07-07 |
| T-F02 | Navigation sidebar V1→V10 | routes OK | [x] | 2026-07-07 |
| T-F03 | V2 Mémoriser → API réelle | graph_id retourné | [x] | 2026-07-07 |
| T-F04 | V3 Graphe Cytoscape | nodes affichés | [x] | 2026-07-07 |
| T-F05 | V4 Chaîne table blocs | GET /chain | [x] | 2026-07-07 |
| T-F06 | V5 Wallets list/create | API wallet | [x] | 2026-07-07 |
| T-F07 | V6 Minage affiche reward 1 ARTCB | label correct | [x] | 2026-07-07 |
| T-F08 | V7 SystemMetrics refresh | /metrics | [x] | 2026-07-07 |
| T-F09 | V8 Logs tail demo_live | fichier lu | [x] | 2026-07-07 |
| T-F10 | V9 Console affiche commandes | pas mock | [x] | 2026-07-07 |
| T-F11 | V10 Créer groupe + join_code + approve | API groups Solution 2 | [x] | 2026-07-07 |
| T-F15 | Page `/groups/join` demande signée | JoinGroup.tsx | [x] | 2026-07-07 |
| T-F12 | Sélecteur réseau Privé/Groupe/Public | filtre UI | [x] | 2026-07-07 |
| T-F13 | Badge DEBUG visible | header | [x] | 2026-07-07 |
| T-F14 | Demo.tsx supprimé, Dashboard actif | App.tsx | [x] | 2026-07-07 |

---

## 4. Avancement % (mis à jour en temps réel)

| Phase | Tâche | % | Tests liés |
|-------|-------|---|------------|
| **0** | LISTE_TESTS + branche dev | **100 %** | — |
| **1** | Backend GroupManager + API | **100 %** | T-G01–G12 |
| **2** | Shell layout + Router + tokens MC | **100 %** | T-F01–F02 |
| **3** | Vues V1–V8 API réelle | **100 %** | T-F03–F09 |
| **4** | V9 Console + V10 Groupes | **100 %** | T-F10–F12, T-F15 |
| **5** | Tests + rapports + suppression Demo | **100 %** | T-B* + T-F14 |

**Avancement dashboard global : 100 %**

---

## 5. Journal d'exécution (cumulatif)

| Date UTC | Session | Tests passés | % | Notes |
|----------|---------|--------------|---|-------|
| 2026-07-07T05:15 | démarrage phase dashboard | — | 5 % | GO utilisateur, branche dev créée |
| 2026-07-07T06:00 | design rétro MC + shell V1–V10 | T-F01, T-F14 | 45 % | Press Start 2P, sidebar, pages |
| 2026-07-07T06:30 | API groupes + filtre chain + V10 | T-G01–G08, T-B01 | 62 % | rapport 047 |
| 2026-07-07T07:00 | CDC 100 % + tous tests | 29/29 + 132 pytest | **100 %** | rapport 048 |
| 2026-07-07T08:00 | Solution 2 request-to-join sécurisé | T-G09–G12, T-F15 | **100 %** | rapport 049 |

---

## 6. Règles de maintenance

1. **Ajouter** un nouveau test en fin de section — jamais supprimer.
2. Cocher `[x]` uniquement après exécution réelle + logs lus.
3. Mettre à jour §4 % après chaque phase.
4. Référencer `rapports/049_*.md` après session join-request.
5. PROTOCOLE : pas de mock — tests API = serveur réel ou TestClient avec fichiers réels.

---

**Dernière mise à jour :** 2026-07-07T08:00:00Z
