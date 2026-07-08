# Rapport 056 — Sécurité post-quantique complète + gouvernance vote API

**Horodatage :** 2026-07-08T22:56:00Z  
**Branche :** `cursor/security-pqc-complete-1fce`  
**Titulaire :** VGACTech — vgacofficiel@gmail.com  
**Progression :** **100 %** (implémentation demandée terminée)

---

## 1. Résumé exécutif

Implémentation **complète** de la couche sécurité post-quantique et gouvernance :

| Composant | Avant | Après |
|-----------|-------|-------|
| Signatures wallet | Ed25519 seul | **Ed25519 + ML-DSA-65** (hybride) |
| Clés PQC au repos | — | **AES-256-GCM** (fichier `.pqc`) |
| Adresse hybride | `artcb1` seul | **`artcb2`** (hash Ed25519+PQC) |
| Blocs chaîne | SHA-256 C + Ed25519 | **+ `hash_sha3`** + signature hybride |
| Groupes join-request | Ed25519 | **Hybride** (rétrocompatible) |
| API vote gouvernance | ❌ Absente | ✅ **`POST /api/v1/governance/vote`** |
| Tests pytest | 141 | **157** (tous passent) |

---

## 2. Métriques avant / après

| Métrique | Avant (post-AES, rapport 055) | Après (PQC complet) |
|----------|-------------------------------|---------------------|
| Tests pytest | 141 passed | **157 passed** |
| Wallet chiffré AES | ✅ | ✅ |
| Wallet hybride PQC | ❌ | ✅ |
| Fichier `.pqc` chiffré | ❌ | ✅ |
| Algorithme PQC | — | **ML-DSA-65** (NIST FIPS 204) |
| SHA-3 sur blocs | ❌ | ✅ champ `hash_sha3` |
| API gouvernance vote | ❌ | ✅ |
| Modules sécurité chargés | 4 | **7** |

Logs : `logs/metrics_post_aes.json` (réf. 055) → `logs/metrics_post_pqc.json`

---

## 3. Fichiers créés / modifiés

### Nouveaux modules
- `src/artcb/crypto/pqc.py` — ML-DSA-65 via liboqs-python
- `src/artcb/crypto/hybrid.py` — signatures hybrides Ed25519+ML-DSA
- `src/artcb/crypto/hashing.py` — SHA-256 + SHA-3-256
- `src/artcb/governance/manager.py` — propositions + votes majorité
- `src/api/governance_routes.py` — REST API gouvernance

### Intégrations
- `src/artcb/wallet/manager.py` — wallets hybrides, `.pqc` chiffré
- `src/artcb/wallet/address.py` — format `artcb2`
- `src/artcb/wallet/encryption.py` — `encrypt_secret_blob` (clés PQC)
- `src/artcb/chain/manager.py` — `hash_sha3`, signatures hybrides
- `src/artcb/groups/signing.py` — vérification hybride join-request
- `src/artcb/groups/join_requests.py` — champ `pqc_public_key_hex`
- `tests/test_pqc_crypto.py` — 11 tests PQC
- `tests/test_governance.py` — 4 tests vote API

### Dépendance
- `pyproject.toml` : `liboqs-python>=0.14.0`

---

## 4. API gouvernance

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/v1/governance/proposals` | GET | Liste propositions + tally |
| `/api/v1/governance/proposals` | POST | Créer proposition (VGACTech) |
| `/api/v1/governance/proposals/{id}` | GET | Détail + votes |
| `/api/v1/governance/vote` | POST | **Voter** (1 wallet = 1 voix) |

Règles : majorité > 50 % des voix exprimées → `requires_rollback: true` si rejet.

---

## 5. Variables d'environnement

```env
ARTCB_WALLET_PASSPHRASE=phrase_min_12_caracteres   # obligatoire
ARTCB_PQC_ENABLED=true                            # défaut: true
```

---

## 6. Ce qui reste hors scope (honnêteté)

| Élément | Statut |
|---------|--------|
| P2P multi-nœuds | ❌ Non implémenté |
| ML-KEM (chiffrement PQC transport) | ❌ Non implémenté |
| UI dashboard « Voter » | ❌ API seule (frontend à brancher) |
| Vérification on-chain des votes | ❌ Stockage local JSONL |

---

## 7. Certification

```bash
cd ~/ARTCB/lvx
git pull origin main
export ARTCB_WALLET_PASSPHRASE="votre_phrase_12_car_min"
pip install -e ".[dev]"
python3 -m pytest tests/ -q   # attendu: 157 passed
```

**Statut : LIVRÉ COMPLET** — PQC intégré, gouvernance API codée, 157 tests verts.
