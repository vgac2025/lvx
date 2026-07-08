# Rapport 055 — AES-256-GCM wallets + métriques avant/après

**Horodatage :** 2026-07-08T22:35:00Z  
**Branche :** `cursor/wallet-aes-security-1fce`  
**Logs :** `logs/metrics_pre_aes.json`, `logs/metrics_post_aes.json`

---

## 1. C’est quoi le chiffrement AES des clés wallet ? (explication simple)

### Le problème AVANT

Quand vous créiez un wallet ARTCB, le programme écrivait un fichier `nom.key` sur le disque contenant **32 octets en clair** = votre **clé privée Ed25519**.

**Comparaison :** c’est comme écrire le code de votre carte bancaire sur un post-it collé sur l’écran.  
Si quelqu’un copie le fichier (virus, backup cloud, vol du PC), il **possède votre wallet**.

### La solution MAINTENANT : AES-256-GCM

**AES** = algorithme de **chiffrement** (coffre-fort numérique).  
**256** = taille de la clé (très forte).  
**GCM** = mode qui garantit aussi l’**intégrité** (détecte si le fichier a été modifié).

**Fonctionnement :**
1. Vous définissez une **phrase secrète** dans `.env` : `ARTCB_WALLET_PASSPHRASE` (min 12 caractères).
2. Le programme dérive une clé de chiffrement avec **scrypt** (résiste au brute-force).
3. La clé privée Ed25519 (32 octets) est **chiffrée** et sauvée ainsi :

```
ARTCBENC1 | sel(16) | nonce(12) | données_chiffrées+tag
```

4. Pour signer / charger le wallet, le programme **déchiffre** avec votre phrase.

### Où c’est utilisé ?

| Cas | Fichier | Comportement |
|-----|---------|--------------|
| Créer wallet | `data/wallets/{name}.key` | **Toujours chiffré** |
| Charger wallet | idem | Déchiffre avec `ARTCB_WALLET_PASSPHRASE` |
| Ancien wallet non chiffré (32 octets) | legacy | **Charge encore**, puis **migre auto** vers AES |
| Join-request sign-with-wallet | API | Charge wallet → déchiffre en mémoire → signe |
| Tests pytest | conftest | Phrase de test auto |

### Ce que AES ne fait PAS

| AES ne protège pas contre… | Pourquoi |
|---------------------------|----------|
| Ordinateur quantique sur Ed25519 | AES oui ; signatures Ed25519 = autre couche (PQC futur) |
| Phrase secrète faible | scrypt aide, mais mot de passe court = risque |
| Vol de phrase + fichier | L’attaquant a les deux = peut déchiffrer |
| Mémoire RAM pendant utilisation | La clé est déchiffrée en RAM pour signer (normal) |

---

## 2. Métriques AVANT / APRÈS (exécution réelle)

| Métrique | AVANT (`pre_aes`) | APRÈS (`post_aes`) |
|----------|-------------------|---------------------|
| **Tests pytest passés** | 133–134 | **141** (+7 tests encryption) |
| **Tests échoués** | 0–1 | **0** |
| **Durée pytest (s)** | ~19,5 | ~21,3 |
| **Taille fichier .key (octets)** | **32** (clair) | **85** (chiffré) |
| **Format ARTCBENC1** | ❌ false | ✅ true |
| **Clé en clair 32 octets** | ✅ true | ❌ false |
| **Chiffrement** | none | **AES-256-GCM** |
| **Permissions fichier** | 0o600 | 0o600 |
| **Signature fonctionne** | ✅ | ✅ |
| **Module `wallet.encryption`** | ❌ absent | ✅ présent |
| **ARTCB_WALLET_PASSPHRASE** | non requis | **requis** |

---

## 3. Fichiers ajoutés / modifiés

| Fichier | Rôle |
|---------|------|
| `src/artcb/wallet/encryption.py` | AES-256-GCM + scrypt + migration legacy |
| `src/artcb/wallet/manager.py` | create/load chiffrés |
| `tests/test_wallet_encryption.py` | 7 nouveaux tests |
| `tests/conftest.py` | passphrase test + fixture book PDF |
| `scripts/security_baseline_metrics.py` | capture métriques avant/après |
| `ENV_A_REMPLIR_ARTCB` | `ARTCB_WALLET_PASSPHRASE` documenté |
| `pyproject.toml` | dépendance `cryptography` |

---

## 4. Post-quantique (ML-DSA / Kyber) — NON implémenté cette session

| Couche | Statut |
|--------|--------|
| AES-256-GCM clés wallet | ✅ **Fait** |
| ML-DSA signatures | ⏳ Phase 2 |
| SHA-3 hash chaîne | ⏳ Phase 2 |
| ML-KEM P2P | ⏳ Phase 3 |

---

## 5. Configuration utilisateur obligatoire

Dans `.env` sur votre PC :

```bash
ARTCB_WALLET_PASSPHRASE=votre_phrase_secrete_min_12_caracteres
```

Sans cette variable, **création et chargement de wallets échouent** (volontaire — pas de retour au clair).

---

**Fin rapport 055**
