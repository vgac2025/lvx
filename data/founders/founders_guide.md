# Guide d'Utilisation — Wallets Founders ARTCB

**Date de création :** 2026-07-05 08:30:43 UTC  
**Version :** 1.0  
**Statut :** Allocation initiale 1% par founder (5 founders)

---

## 1. Vue d'Ensemble

### Allocation Founders

| Paramètre | Valeur |
|-----------|--------|
| **Supply totale ARTCB** | 21,000,000 ARTCB |
| **Nombre de founders** | 5 |
| **Allocation par founder** | 210,000 ARTCB (1%) |
| **Allocation totale founders** | 1,050,000 ARTCB (5%) |
| **En satoshi (par founder)** | 21,000,000,000,000 satoshi |

### Fichiers Générés

1. **`founders_wallets.json`** — Clés privées + adresses (⚠️ SENSIBLE)
2. **`founders_allocation.json`** — Balances initiales (public)
3. **`founders_guide.md`** — Ce guide (public)

---

## 2. Structure Wallet Founder

Chaque wallet contient :

```json
{
  "founder_id": 1,
  "name": "Founder 1",
  "address": "Base64EncodedEd25519VerifyKey...",
  "private_key": "HexEncodedEd25519SigningKey...",
  "allocation_artcb": 210,000,
  "allocation_satoshi": 21,000,000,000,000
}
```

**⚠️ SÉCURITÉ CRITIQUE :**
- `private_key` = clé de signature Ed25519 (64 caractères hex)
- **NE JAMAIS** committer `founders_wallets.json` sur GitHub
- **NE JAMAIS** partager les clés privées
- Fichier déjà dans `.gitignore` : `data/founders/founders_wallets.json`

---

## 3. Utilisation des Wallets

### 3.1 Vérifier l'Allocation

```bash
# Lire l'allocation publique (sans clés privées)
cat data/founders/founders_allocation.json | jq '.balances'
```

**Sortie attendue :**
```json
[
  {
    "founder_id": 1,
    "name": "Founder 1",
    "address": "...",
    "balance_artcb": 210,000,
    "balance_satoshi": 21,000,000,000,000
  },
  ...
]
```

### 3.2 Signer une Transaction (Python)

```python
import json
from pathlib import Path
from nacl import encoding, signing

# Charger le wallet Founder 1
wallets = json.loads(Path("data/founders/founders_wallets.json").read_text())
founder1 = wallets["wallets"][0]

# Reconstruire la clé de signature
private_key_hex = founder1["private_key"]
signing_key = signing.SigningKey(bytes.fromhex(private_key_hex))

# Signer un message
message = b"Transfer 100 ARTCB to address_xyz"
signed = signing_key.sign(message)
signature_hex = signed.signature.hex()

print(f"Signature: {signature_hex}")
```

### 3.3 Vérifier une Signature (Python)

```python
from nacl import encoding, signing

# Adresse publique du founder
address_b64 = founder1["address"]
verify_key = signing.VerifyKey(address_b64, encoder=encoding.Base64Encoder)

# Vérifier la signature
try:
    verify_key.verify(message, bytes.fromhex(signature_hex))
    print("✅ Signature valide")
except Exception:
    print("❌ Signature invalide")
```

### 3.4 Transférer des ARTCB (CLI)

```bash
# Exemple : Founder 1 transfère 1000 ARTCB à un mineur
python3 scripts/transfer_artcb.py \
  --from-founder 1 \
  --to-address "Base64AddressOfMiner..." \
  --amount 1000 \
  --private-key-file data/founders/founders_wallets.json
```

**Note :** Le script `transfer_artcb.py` doit être créé pour gérer les transactions.

---

## 4. Vérification de Fonctionnement

### 4.1 Test Signature Locale

```bash
# Créer un script de test
python3 scripts/test_founder_signature.py
```

**Contenu `test_founder_signature.py` :**
```python
import json
from pathlib import Path
from nacl import encoding, signing

# Charger Founder 1
wallets = json.loads(Path("data/founders/founders_wallets.json").read_text())
founder = wallets["wallets"][0]

# Signer + vérifier
signing_key = signing.SigningKey(bytes.fromhex(founder["private_key"]))
verify_key = signing.VerifyKey(founder["address"], encoder=encoding.Base64Encoder)

message = b"Test ARTCB Founder Signature"
signed = signing_key.sign(message)

try:
    verify_key.verify(message, signed.signature)
    print(f"✅ Founder {founder['founder_id']} signature VALIDE")
    print(f"   Adresse: {founder['address'][:32]}...")
    print(f"   Balance: {founder['allocation_artcb']:,} ARTCB")
except Exception as e:
    print(f"❌ Erreur: {e}")
```

### 4.2 Vérifier Balance Blockchain

```bash
# Interroger la blockchain pour la balance d'un founder
python3 scripts/check_balance.py --address "Base64AddressFounder1..."
```

**Sortie attendue :**
```
Founder 1
Address: Base64EncodedKey...
Balance: 210,000 ARTCB (21,000,000,000,000 satoshi)
Blocks mined: 0
Last activity: Genesis
```

---

## 5. Sécurité et Bonnes Pratiques

### 5.1 Protection des Clés Privées

✅ **À FAIRE :**
- Stocker `founders_wallets.json` dans un coffre-fort chiffré (1Password, Bitwarden, etc.)
- Utiliser un HSM (Hardware Security Module) pour la production
- Sauvegarder les clés sur support physique déconnecté (USB chiffré)
- Limiter l'accès aux clés privées (principe du moindre privilège)

❌ **À NE JAMAIS FAIRE :**
- Committer `founders_wallets.json` sur GitHub
- Envoyer les clés privées par email/Slack/Discord
- Stocker les clés en clair sur un serveur cloud
- Partager les clés avec des tiers non autorisés

### 5.2 Rotation des Clés

Si une clé privée est compromise :

1. Générer un nouveau wallet :
   ```bash
   python3 scripts/create_founders_wallets.py --rotate-founder 1
   ```

2. Transférer la balance vers la nouvelle adresse :
   ```bash
   python3 scripts/transfer_artcb.py \
     --from-founder 1 \
     --to-address "NewFounder1Address..." \
     --amount 210,000 \
     --reason "Key rotation"
   ```

3. Révoquer l'ancienne clé dans la blockchain

### 5.3 Multi-Signature (Recommandé)

Pour la production, utiliser un schéma multi-sig 3-of-5 :
- Nécessite 3 signatures sur 5 founders pour valider une transaction
- Réduit le risque de compromission d'une seule clé
- Implémentation : voir `scripts/multisig_setup.py`

---

## 6. FAQ Founders

### Q1 : Pourquoi 1% par founder ?

**R :** Allocation équitable entre les 5 founders (5% total), laissant 95% pour :
- Minage PoL (block rewards) : ~89%
- Réserve protocole : ~5%
- Partenaires / communauté : ~1%

### Q2 : Les founders peuvent-ils miner ?

**R :** Oui, mais leur allocation 1% est **distincte** des rewards de minage. Ils peuvent :
- Miner comme tout contributeur PoL
- Recevoir des block rewards proportionnels à leur PoL score
- Leur allocation initiale reste intacte

### Q3 : Comment vérifier que les founders ne trichent pas ?

**R :** Transparence blockchain :
- Toutes les transactions founders sont publiques
- Balances vérifiables via `/api/v1/balance/<address>`
- Logs d'audit dans `data/chain/blocks.jsonl`
- Anti-Sybil + slashing empêchent les abus

### Q4 : Que se passe-t-il si un founder perd sa clé ?

**R :** Les ARTCB sont **perdus définitivement** (comme Bitcoin). Solutions :
- Backup sécurisé obligatoire (coffre-fort chiffré)
- Multi-sig 3-of-5 pour réduire le risque
- Procédure de récupération sociale (vote des 4 autres founders)

### Q5 : Les founders peuvent-ils vendre leurs ARTCB ?

**R :** Oui, mais :
- Période de vesting recommandée (ex: 4 ans avec cliff 1 an)
- Transparence obligatoire (annonce publique avant vente)
- Pas de vente massive (max 10% par trimestre)
- Respect du code de conduite founders

---

## 7. Commandes Utiles

```bash
# Lister tous les founders
jq '.wallets[] | {id: .founder_id, name: .name, balance: .allocation_artcb}' \
  data/founders/founders_allocation.json

# Vérifier la signature d'un founder
python3 scripts/verify_founder_signature.py \
  --founder-id 1 \
  --message "Test" \
  --signature "hex_signature"

# Exporter l'adresse publique d'un founder (sans clé privée)
jq '.wallets[0].address' data/founders/founders_wallets.json

# Calculer le total alloué aux founders
jq '.founders_total_artcb' data/founders/founders_allocation.json
```

---

## 8. Support et Contact

**Questions techniques :** Ouvrir une issue sur GitHub  
**Sécurité :** Contacter security@artcb.io (PGP requis)  
**Founders :** Canal privé Discord #founders-only

---

**⚠️ RAPPEL SÉCURITÉ :**
- `founders_wallets.json` contient les clés privées → **NE JAMAIS COMMITTER**
- `founders_allocation.json` est public → OK pour commit
- Ce guide est public → OK pour commit

**Dernière mise à jour :** 2026-07-05 08:30:43 UTC
