# Rapport 047 — API Groupes + filtre chaîne + tests T-G

**Horodatage :** 2026-07-07T06:30:00Z  
**Branche :** `cursor/dashboard-dev-1fce`  
**PROTOCOLE :** pas de mock, mode DEBUG, logs lus, rapport nouveau fichier  
**Expertise mobilisée :** backend FastAPI, ACL multi-tenant, blockchain JSONL, tests pytest

---

## 1. Objectif session

Poursuivre le développement dashboard en respectant PROTOCOLE_ARTCB et AUTO_PROMPT_ARTCB :
- API `/groups` bout en bout (fondateur immuable)
- Fix index chaîne (`last_hash` / `append_block` sur blocs non filtrés)
- Filtre `GET /chain?group_id=` et `POST /store` visibility=group
- Tests T-G01–G08 + frontend V10 branché API réelle

---

## 2. Avancement %

| Composant | Avant session | Après session |
|-----------|---------------|---------------|
| Backend groupes | ~15 % | **~75 %** |
| API store/chain groupe | 0 % | **~80 %** |
| Frontend V10 Groupes | ~20 % | **~65 %** |
| Tests groupes | 0/8 | **7/7 passés** (T-G06+G07+G08 combinés) |
| **Dashboard global** | **45 %** | **~62 %** |

---

## 3. Avant / Après — fichiers modifiés

### 3.1 `src/artcb/chain/manager.py`

**Avant :**
```python
def last_hash(self) -> str:
    blocks = self.list_blocks()  # filtré — risque hash incorrect

def append_block(...):
    index = len(self.list_blocks())  # idem
    # group_id absent sur ChainBlock créé
```

**Après :**
```python
def last_hash(self) -> str:
    blocks = self._read_all_blocks()  # toujours chaîne complète

def append_block(..., group_id: str | None = None, ...):
    all_blocks = self._read_all_blocks()
    index = len(all_blocks)
    ...
    group_id=group_id,  # sur ChainBlock
```

### 3.2 `src/api/deps.py`

**Avant :** pas de `GroupManager` dans `AppState`

**Après :**
```python
groups: GroupManager
...
groups=GroupManager(settings.data_dir / "groups"),
```

### 3.3 Nouveau `src/api/groups_routes.py`

Endpoints réels (fichiers JSON `data/groups/g_*.json` + audit `groups_audit.jsonl`) :
- `POST /api/v1/groups`
- `GET /api/v1/groups?address=`
- `GET /api/v1/groups/{id}`
- `POST /api/v1/groups/{id}/members`
- `POST /api/v1/groups/{id}/members/{addr}/role`
- `DELETE /api/v1/groups/{id}/members/{addr}`
- `POST /api/v1/groups/{id}/dissolve`

### 3.4 `src/api/routes.py`

**Avant :** `StoreRequest` sans `group_id` ; `GET /chain` sans filtre

**Après :**
```python
class StoreRequest(BaseModel):
    ...
    group_id: str | None = None
    actor_address: str | None = None

# validation visibility=group → membre requis
# GET /chain?visibility=&group_id=
```

### 3.5 `frontend/src/pages/Groups.tsx`

**Avant :** wireframe statique

**Après :** création groupe, liste, invite, promote admin (fondateur seul) via API réelle

---

## 4. Exécution tests + logs

| Commande | Résultat | Log |
|----------|----------|-----|
| `pytest tests/test_groups.py -v` | **7 passed** | `logs/tests_groups_20260707.log` |
| `pytest tests/ -q` | **103 passed** | `logs/tests_all_20260707.log` |
| `cd frontend && npm run build` | **OK** | build Vite |

**Note :** 96 → 103 tests (+7 groupes). T-B01 baseline toujours vert.

---

## 5. Tests LISTE_TESTS cochés

| ID | Statut |
|----|--------|
| T-G01 | [x] test_create_group |
| T-G02 | [x] founder immutable |
| T-G03 | [x] founder promotes admin |
| T-G04 | [x] admin cannot promote |
| T-G05 | [x] dissolve founder only |
| T-G06 | [x] POST/GET groups API |
| T-G07 | [x] store visibility=group |
| T-G08 | [x] chain filter group_id |
| T-B01 | [x] 103 passed |
| T-F01 | [x] npm build |

---

## 6. Reste à faire

- Tests manuels frontend T-F02–F13 (navigation live)
- Signature wallet sur actions groupe (P2 — actuellement `actor_address` en body)
- Transfert fondateur (F8 spec) — non implémenté
- Rapport dissolve utilisateur + merge `main` **interdit** sans accord explicite

---

## 7. Erreurs / incertitudes

- Aucune erreur bloquante en session.
- `actor_address` non signé cryptographiquement — acceptable MVP devnet, à durcir avant production.

---

**Fin rapport 047 — ne pas écraser.**
