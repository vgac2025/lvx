# Rapport 049 — Solution 2 request-to-join (sécurité invitations)

**Horodatage :** 2026-07-07T08:00:00Z  
**Branche :** `cursor/dashboard-dev-1fce`  
**PROTOCOLE :** audit code lu, pas de mock, rapport nouveau fichier, avant/après

---

## 1. Question utilisateur — le fondateur connaît-il la clé des invités ?

**Non.** Dans la Solution 2 (request-to-join) :

| Donnée | Fondateur la connaît ? | Quand ? |
|--------|------------------------|---------|
| Clé privée invité | **Jamais** | — |
| Adresse publique invité | Seulement après demande signée | `POST /join-requests` pending |
| `join_code` (8 car.) | Oui (il le partage) | Création groupe — code public, pas secret |

L'ancien flux « coller l'adresse du membre » (`POST /members`) exposait l'adresse **avant** consentement et est **désactivé** sauf `ARTCB_DEBUG_DIRECT_MEMBER=true`.

---

## 2. Avancement

| Composant | Avant (rapport 048) | Après (audit code) |
|-----------|---------------------|---------------------|
| Invite par adresse | Actif (insécure) | **Bloqué** (`policy.py`) |
| Join code + signature | Absent | **Implémenté** |
| UI Rejoindre groupe | Absent | `/groups/join` |
| Approbation admin | Absent | approve/reject API + UI |
| Tests join-request | 0 | **T-G09–G12** |
| pytest total | 132 | **134** |

---

## 3. Fichiers vérifiés (lecture code)

### Backend nouveau
- `src/artcb/groups/signing.py` — challenge `ARTCB-JOIN-REQUEST|…`, Ed25519, `BadSignatureError`
- `src/artcb/groups/join_requests.py` — stockage `g_*_join_requests.jsonl`
- `src/artcb/groups/policy.py` — `direct_member_invite_allowed()`

### Backend modifié
- `src/artcb/groups/manager.py` — `join_code`, `add_member_approved()`, blocage `add_member()`
- `src/api/groups_routes.py` — endpoints join-request complets
- `src/api/deps.py` — `JoinRequestManager` injecté
- `src/artcb/wallet/address.py` — `address_from_public_key_hex/bytes`
- `src/artcb/wallet/manager.py` — `name` dans `list_wallets()`

### Frontend
- `frontend/src/pages/JoinGroup.tsx` — lookup code + sign-with-wallet
- `frontend/src/pages/Groups.tsx` — affiche join_code, pending approve/reject
- `frontend/src/App.tsx` — route `/groups/join`
- `frontend/src/api/client.ts` — fonctions join-request

### Tests
- `tests/test_groups.py` — 9 tests dont join flow, direct invite 403, reject

### Docs mis à jour
- `GROUPES_RESEAUX_ARTCB.md` §4.3–4.5
- `CAHIER_DES_CHARGES_DASHBOARD_ARTCB.md` §V10 + §5bis
- `LISTE_TESTS_ARTCB.md` — T-G09–G12, T-F15

---

## 4. Exécution tests

| ID | Commande | Résultat |
|----|----------|----------|
| T-B01 | `python3 -m pytest tests/ -q` | **134 passed** |
| T-G09–G12 | `tests/test_groups.py` | **9 passed** |
| T-F01 | `cd frontend && npm run build` | **OK** |

---

## 5. Correction rapport 048

Le rapport 048 affirmait « 100 % » incluant invitations par adresse. **Correction :** dashboard UI = 100 % ; sécurité invitations = complétée seulement avec ce rapport 049 (Solution 2).

---

## 6. Hors scope (P2 production)

- Signature wallet côté navigateur (extension) — devnet utilise `sign-with-wallet` serveur
- Transfert fondateur F8
- Playwright E2E
- Merge `main` — interdit sans accord utilisateur

---

**Fin rapport 049**
