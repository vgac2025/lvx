#!/usr/bin/env python3
"""Création des 5 wallets founders ARTCB avec allocation 1% (210,000 ARTCB chacun).

Génère:
- 5 paires de clés Ed25519 (signing + verify)
- Fichier founders_wallets.json avec adresses + clés privées
- Fichier founders_allocation.json avec balances initiales
- Guide d'utilisation founders_guide.md

SÉCURITÉ: Les clés privées sont générées localement et NE DOIVENT JAMAIS être commitées.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from nacl import encoding, signing

# Configuration
FOUNDERS_COUNT = 5
TOTAL_SUPPLY_ARTCB = 21_000_000
FOUNDERS_ALLOCATION_PCT = 0.01  # 1% par founder
FOUNDERS_ALLOCATION_ARTCB = int(TOTAL_SUPPLY_ARTCB * FOUNDERS_ALLOCATION_PCT)  # 210,000 ARTCB
FOUNDERS_ALLOCATION_SATOSHI = FOUNDERS_ALLOCATION_ARTCB * 100_000_000  # En satoshi

DATA_DIR = Path("data/founders")
DATA_DIR.mkdir(parents=True, exist_ok=True)

WALLETS_FILE = DATA_DIR / "founders_wallets.json"
ALLOCATION_FILE = DATA_DIR / "founders_allocation.json"
GUIDE_FILE = DATA_DIR / "founders_guide.md"


def generate_founder_wallet(founder_id: int) -> dict:
    """Génère une paire de clés Ed25519 pour un founder."""
    signing_key = signing.SigningKey.generate()
    verify_key = signing_key.verify_key
    
    # Adresse = verify_key en base64 (format ARTCB)
    address = verify_key.encode(encoder=encoding.Base64Encoder).decode("ascii")
    private_key = signing_key.encode(encoder=encoding.HexEncoder).decode("ascii")
    
    return {
        "founder_id": founder_id,
        "name": f"Founder {founder_id}",
        "address": address,
        "private_key": private_key,  # WARN SENSIBLE - Ne jamais committer
        "allocation_artcb": FOUNDERS_ALLOCATION_ARTCB,
        "allocation_satoshi": FOUNDERS_ALLOCATION_SATOSHI,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def create_founders_wallets() -> list[dict]:
    """Crée les 5 wallets founders."""
    wallets = []
    for i in range(1, FOUNDERS_COUNT + 1):
        wallet = generate_founder_wallet(i)
        wallets.append(wallet)
        print(f"OK Founder {i} créé")
        print(f"   Adresse: {wallet['address'][:32]}...")
        print(f"   Allocation: {wallet['allocation_artcb']:,} ARTCB")
    return wallets


def save_wallets(wallets: list[dict]) -> None:
    """Sauvegarde les wallets dans founders_wallets.json."""
    with WALLETS_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "version": "1.0",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "total_supply_artcb": TOTAL_SUPPLY_ARTCB,
                "founders_count": FOUNDERS_COUNT,
                "allocation_per_founder_artcb": FOUNDERS_ALLOCATION_ARTCB,
                "allocation_per_founder_satoshi": FOUNDERS_ALLOCATION_SATOSHI,
                "wallets": wallets,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    print(f"\n Wallets sauvegardés: {WALLETS_FILE}")


def save_allocation(wallets: list[dict]) -> None:
    """Sauvegarde l'allocation initiale dans founders_allocation.json."""
    allocation = {
        "version": "1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "total_supply_artcb": TOTAL_SUPPLY_ARTCB,
        "founders_total_artcb": FOUNDERS_ALLOCATION_ARTCB * FOUNDERS_COUNT,
        "founders_total_satoshi": FOUNDERS_ALLOCATION_SATOSHI * FOUNDERS_COUNT,
        "founders_percentage": FOUNDERS_ALLOCATION_PCT * FOUNDERS_COUNT * 100,
        "balances": [
            {
                "founder_id": w["founder_id"],
                "name": w["name"],
                "address": w["address"],
                "balance_artcb": w["allocation_artcb"],
                "balance_satoshi": w["allocation_satoshi"],
            }
            for w in wallets
        ],
    }
    with ALLOCATION_FILE.open("w", encoding="utf-8") as f:
        json.dump(allocation, f, indent=2, ensure_ascii=False)
    print(f" Allocation sauvegardée: {ALLOCATION_FILE}")


def create_guide() -> None:
    """Crée le guide d'utilisation founders_guide.md."""
    guide = f"""# Guide d'Utilisation — Wallets Founders ARTCB

**Date de création :** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Version :** 1.0  
**Statut :** Allocation initiale 1% par founder (5 founders)

---

## 1. Vue d'Ensemble

### Allocation Founders

| Paramètre | Valeur |
|-----------|--------|
| **Supply totale ARTCB** | {TOTAL_SUPPLY_ARTCB:,} ARTCB |
| **Nombre de founders** | {FOUNDERS_COUNT} |
| **Allocation par founder** | {FOUNDERS_ALLOCATION_ARTCB:,} ARTCB (1%) |
| **Allocation totale founders** | {FOUNDERS_ALLOCATION_ARTCB * FOUNDERS_COUNT:,} ARTCB (5%) |
| **En satoshi (par founder)** | {FOUNDERS_ALLOCATION_SATOSHI:,} satoshi |

### Fichiers Générés

1. **`founders_wallets.json`** — Clés privées + adresses (WARN SENSIBLE)
2. **`founders_allocation.json`** — Balances initiales (public)
3. **`founders_guide.md`** — Ce guide (public)

---

## 2. Structure Wallet Founder

Chaque wallet contient :

```json
{{
  "founder_id": 1,
  "name": "Founder 1",
  "address": "Base64EncodedEd25519VerifyKey...",
  "private_key": "HexEncodedEd25519SigningKey...",
  "allocation_artcb": {FOUNDERS_ALLOCATION_ARTCB:,},
  "allocation_satoshi": {FOUNDERS_ALLOCATION_SATOSHI:,}
}}
```

**WARN SÉCURITÉ CRITIQUE :**
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
  {{
    "founder_id": 1,
    "name": "Founder 1",
    "address": "...",
    "balance_artcb": {FOUNDERS_ALLOCATION_ARTCB:,},
    "balance_satoshi": {FOUNDERS_ALLOCATION_SATOSHI:,}
  }},
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

print(f"Signature: {{signature_hex}}")
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
    print("OK Signature valide")
except Exception:
    print("FAIL Signature invalide")
```

### 3.4 Transférer des ARTCB (CLI)

```bash
# Exemple : Founder 1 transfère 1000 ARTCB à un mineur
python3 scripts/transfer_artcb.py \\
  --from-founder 1 \\
  --to-address "Base64AddressOfMiner..." \\
  --amount 1000 \\
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
    print(f"OK Founder {{founder['founder_id']}} signature VALIDE")
    print(f"   Adresse: {{founder['address'][:32]}}...")
    print(f"   Balance: {{founder['allocation_artcb']:,}} ARTCB")
except Exception as e:
    print(f"FAIL Erreur: {{e}}")
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
Balance: {FOUNDERS_ALLOCATION_ARTCB:,} ARTCB ({FOUNDERS_ALLOCATION_SATOSHI:,} satoshi)
Blocks mined: 0
Last activity: Genesis
```

---

## 5. Sécurité et Bonnes Pratiques

### 5.1 Protection des Clés Privées

OK **À FAIRE :**
- Stocker `founders_wallets.json` dans un coffre-fort chiffré (1Password, Bitwarden, etc.)
- Utiliser un HSM (Hardware Security Module) pour la production
- Sauvegarder les clés sur support physique déconnecté (USB chiffré)
- Limiter l'accès aux clés privées (principe du moindre privilège)

FAIL **À NE JAMAIS FAIRE :**
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
   python3 scripts/transfer_artcb.py \\
     --from-founder 1 \\
     --to-address "NewFounder1Address..." \\
     --amount {FOUNDERS_ALLOCATION_ARTCB:,} \\
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
jq '.wallets[] | {{id: .founder_id, name: .name, balance: .allocation_artcb}}' \\
  data/founders/founders_allocation.json

# Vérifier la signature d'un founder
python3 scripts/verify_founder_signature.py \\
  --founder-id 1 \\
  --message "Test" \\
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

**WARN RAPPEL SÉCURITÉ :**
- `founders_wallets.json` contient les clés privées → **NE JAMAIS COMMITTER**
- `founders_allocation.json` est public → OK pour commit
- Ce guide est public → OK pour commit

**Dernière mise à jour :** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
    
    with GUIDE_FILE.open("w", encoding="utf-8") as f:
        f.write(guide)
    print(f" Guide créé: {GUIDE_FILE}")


def main() -> None:
    print("=" * 60)
    print("CRÉATION DES WALLETS FOUNDERS ARTCB")
    print("=" * 60)
    print(f"Supply totale: {TOTAL_SUPPLY_ARTCB:,} ARTCB")
    print(f"Founders: {FOUNDERS_COUNT}")
    print(f"Allocation par founder: {FOUNDERS_ALLOCATION_ARTCB:,} ARTCB (1%)")
    print(f"Allocation totale: {FOUNDERS_ALLOCATION_ARTCB * FOUNDERS_COUNT:,} ARTCB (5%)")
    print("=" * 60)
    print()
    
    # Créer les wallets
    wallets = create_founders_wallets()
    
    # Sauvegarder
    save_wallets(wallets)
    save_allocation(wallets)
    create_guide()
    
    print()
    print("=" * 60)
    print("OK CRÉATION TERMINÉE")
    print("=" * 60)
    print()
    print(" Fichiers créés:")
    print(f"   1. {WALLETS_FILE} (WARN SENSIBLE - Ne pas committer)")
    print(f"   2. {ALLOCATION_FILE} (Public - OK pour commit)")
    print(f"   3. {GUIDE_FILE} (Public - OK pour commit)")
    print()
    print(" SÉCURITÉ:")
    print("   - Sauvegarder founders_wallets.json dans un coffre-fort chiffré")
    print("   - Vérifier que data/founders/founders_wallets.json est dans .gitignore")
    print("   - Ne JAMAIS partager les clés privées")
    print()
    print(" Lire le guide: cat data/founders/founders_guide.md")
    print()


if __name__ == "__main__":
    main()

