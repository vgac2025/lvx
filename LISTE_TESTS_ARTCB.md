# LISTE TESTS ARTCB — Registre cumulatif

**Horodatage création :** 2026-07-07T05:15:00Z  
**Branche dev :** `cursor/dashboard-dev-1fce`  
**Règle PROTOCOLE :** cette liste est **cumulative** — ne jamais supprimer un test, cocher `[x]` quand passé, ajouter horodatage.

**Avancement tests dashboard :** voir §4 tableau % en bas (mis à jour à chaque session).

---

## 1. Tests backend existants (baseline — toujours exécuter)

| ID | Commande | Attendu | Statut | Dernière exec |
|----|----------|---------|--------|---------------|
| T-B01 | `python3 -m pytest tests/ -q` | 96+ passed | [x] | 2026-07-07 (103) |
| T-B02 | `python3 -m pytest tests/test_wallet_rewards.py -q` | all pass, reward 1 ARTCB | [ ] | — |
| T-B03 | `python3 -m pytest tests/test_pol.py -q` | split 1.0 ARTCB | [ ] | — |
| T-B04 | `python3 -m pytest tests/test_api.py -q` | API OK | [ ] | — |
| T-B05 | `python3 -m pytest tests/test_chain.py -q` | C verify OK | [ ] | — |
| T-B06 | `python3 scripts/demo_live.py` | 9/9 steps OK | [ ] | — |
| T-B07 | `curl -s localhost:8000/api/v1/health \| jq .status` | `"ok"` | [ ] | — |

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

---

## 3. Tests frontend dashboard (nouveau)

| ID | Scénario | Attendu | Statut | Dernière exec |
|----|----------|---------|--------|---------------|
| T-F01 | `cd frontend && npm run build` | 0 errors | [x] | 2026-07-07 |
| T-F02 | Navigation sidebar V1→V10 | routes OK | [ ] | — |
| T-F03 | V2 Mémoriser → API réelle | graph_id retourné | [ ] | — |
| T-F04 | V3 Graphe Cytoscape | nodes affichés | [ ] | — |
| T-F05 | V4 Chaîne table blocs | GET /chain | [ ] | — |
| T-F06 | V5 Wallets list/create | API wallet | [ ] | — |
| T-F07 | V6 Minage affiche reward 1 ARTCB | label correct | [ ] | — |
| T-F08 | V7 SystemMetrics refresh | /metrics | [ ] | — |
| T-F09 | V8 Logs tail demo_live | fichier lu | [ ] | — |
| T-F10 | V9 Console affiche commandes | pas mock | [ ] | — |
| T-F11 | V10 Créer groupe + inviter | API groups | [ ] | — |
| T-F12 | Sélecteur réseau Privé/Groupe/Public | filtre UI | [ ] | — |
| T-F13 | Badge DEBUG visible | header | [ ] | — |
| T-F14 | Demo.tsx supprimé, Dashboard actif | App.tsx | [x] | 2026-07-07 |

---

## 4. Avancement % (mis à jour en temps réel)

| Phase | Tâche | % | Tests liés |
|-------|-------|---|------------|
| **0** | LISTE_TESTS + branche dev | 5 % | — |
| **1** | Backend GroupManager + API | **75 %** | T-G01–G08 |
| **2** | Shell layout + Router + tokens | 35 % | T-F01–F02 |
| **3** | Vues V1–V8 API réelle | 60 % | T-F03–F09 |
| **4** | V9 Console + V10 Groupes | 80 % | T-F10–F12 |
| **5** | Suppression Demo + tests + rapport | 100 % | T-B* + T-F14 |

**Avancement dashboard global : 62 %**

---

## 5. Journal d'exécution (cumulatif)

| Date UTC | Session | Tests passés | % | Notes |
|----------|---------|--------------|---|-------|
| 2026-07-07T05:15 | démarrage phase dashboard | — | 5 % | GO utilisateur, branche dev créée |
| 2026-07-07T06:00 | design rétro MC + shell V1–V10 | T-F01, T-F14 | 45 % | Press Start 2P, sidebar, pages |
| 2026-07-07T06:30 | API groupes + filtre chain + V10 | T-G01–G08, T-B01 | 62 % | rapport 047, 103 tests |

---

## 6. Règles de maintenance

1. **Ajouter** un nouveau test en fin de section — jamais supprimer.
2. Cocher `[x]` uniquement après exécution réelle + logs lus.
3. Mettre à jour §4 % après chaque phase.
4. Référencer `rapports/047_*.md` après chaque session test.
5. PROTOCOLE : pas de mock — tests API = serveur réel ou TestClient avec fichiers réels.

---

**Dernière mise à jour :** 2026-07-07T06:30:00Z
