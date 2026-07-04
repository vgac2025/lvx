# Rapport 005 — Tokenomics PoL collectif + artcb-devnet

**Horodatage :** 2026-07-04T22:55:00Z  
**Expertises mobilisées :** tokenomics, architecture blockchain, Proof-of-Learning, réseaux distribués

---

## 1. Demande utilisateur

1. Documenter dans le dépôt (pas seulement le chat) :
   - cible mineurs d'apprentissage ;
   - 21 000 000 coins style Bitcoin ;
   - minage PoL avec récompense **collective** (pas winner-takes-all) ;
   - correction de la réflexion sur le gaspillage Bitcoin ;
   - différences Bitcoin testnet3/4 vs blockchain ARTCB.

2. Conformité `PROTOCOLE_ARTCB` + `AUTO_PROMPT_ARTCB` : rapports FR, avant/après, logs, % avancement.

---

## 2. État d'avancement (%)

| Phase | Avant | Après | Δ |
|-------|-------|-------|---|
| Phase 0 Spec documentaire | 95 % | **100 %** | +5 % |
| Phase 1 IR Engine | 100 % | 100 % | — |
| Phase 2 Backend | 0 % | 0 % | — |
| Phase 3 Blockchain + tokenomics code | 0 % | 0 % | spec ✅ |
| Phase 4 Frontend | 0 % | 0 % | — |
| **Global MVP** | ~33 % | **~35 %** | +2 % |

---

## 3. Fichiers créés (après)

| Fichier | Rôle |
|---------|------|
| `TOKENOMICS_ARTCB` | Supply 21M, halving, split PoL collectif, wallet, anti-fraude |
| `RESEAU_DEVNET_ARTCB` | artcb-devnet vs Bitcoin testnet3/4 — **NON compatible** |
| `rapports/005_tokenomics_pol_collectif.md` | Ce rapport |

---

## 4. Fichiers modifiés — avant / après

### 4.1 `CAHIER_DES_CHARGES_ARTCB`

**Avant (v1.1, fin fichier) :**
```
**Fin du cahier des charges — ARTCB MVP Avancé v1.1**
```

**Après (v1.2) :**
- §0 : ajout unité ARTCB + répartition collective
- §1.1 : persona mineur PoL prioritaire
- §3.2.4 : formule `reward_i = block_reward × (PoL_i / Σ PoL_j)`
- §3.2.5 : champs `contributors[]`, `block_reward`, `pol_aggregate` (suppression `nonce` PoW)
- §17 : glossaire ARTCB, artcb-devnet
- §27-30 : tokenomics, réseau, audit v1.2

**Après (fin fichier) :**
```
**Fin du cahier des charges — ARTCB MVP Avancé v1.2**
```

### 4.2 `DECISIONS_UTILISATEUR_ARTCB`

**Avant :** D-001 → D-013  
**Après :** D-014 (21M), D-015 (split collectif), D-016 (halving), D-017 (artcb-devnet), D-018 (pas clone crypto PoW)

### 4.3 `QUESTIONS_OUVERTES_ARTCB`

**Avant :** Q-001 → Q-011  
**Après :** Q-012→Q-014 documentées ✅ ; Q-015/Q-016 ⏳ ; Q-017 testnet Bitcoin = NON ✅

### 4.4 Autres

| Fichier | Modification |
|---------|--------------|
| `INDEX_ARTCB` | v1.2, matrice tokenomics, ~35 % global |
| `AUTO_PROMPT_ARTCB` | Horodatage 2026-07-04T22:50:00Z + refs tokenomics |
| `ROADMAP_GENERAL_ARTCB` | Jalons 3.6 devnet, 3.7 rewards |
| `STRUCTURE_ARTCB` | Entrées TOKENOMICS + RESEAU_DEVNET |
| `LEÇONS_APPRISES_ARTCB` | L-015 tokenomics vs Bitcoin |
| `CONFIGURATION_ARTCB` | `ARTCB_NETWORK`, `ARTCB_BLOCK_REWARD`, halving, max supply |

---

## 5. Synthèse réflexion utilisateur (documentée)

### Correct

- Cible prioritaire pitch : **mineurs d'apprentissage PoL**.
- **21M supply** + émission via apprentissage (pas hash SHA-256).
- **Split collectif** meilleur alignement que winner-takes-all Bitcoin.
- Bitcoin testnet3/4 **inutilisable** pour ARTCB.

### Nuances ajoutées

| Affirmation | Correction documentée |
|-------------|-------------------------|
| 99 % perdent tout (Bitcoin) | Pools redistribuent en interne |
| 99 % calcul inutile (Bitcoin) | Modèle sécurité PoW volontaire |
| 100 % utilisé (ARTCB) | Conditionnel — éviter validations PoL dupliquées |
| ARTCB ≠ crypto | Coin = incentive PoL ; cœur = mémoire IA |

---

## 6. Tests exécutés

```bash
python3 -m pytest tests/ -v
# 28 passed in 4.82s
```

Log : `logs/20260704_tokenomics_docs.json`

| Suite | Résultat |
|-------|----------|
| test_ir_reversibility | ✅ 20/20 |
| test_book_wailly | ✅ 5/5 |
| test_symbols | ✅ 3/3 |
| **Total** | **28/28** |

Aucune régression code — session **documentation uniquement**.

---

## 7. Ce qui reste à implémenter (code)

| Élément | Phase | Spec |
|---------|-------|------|
| PoL Scorer | 2 | CDC §3.2.4 |
| Blockchain C + rewards | 3 | TOKENOMICS §7 |
| artcb-devnet + faucet | 3 | RESEAU_DEVNET §4 |
| Wallet + explorer | 4 | TOKENOMICS §8 |

---

## 8. Questions ouvertes (utilisateur)

| ID | Question |
|----|----------|
| Q-015 | Coin privé seul (A) ou aussi réseau public (B) ? |
| Q-016 | Mineur humain (A), IA (B), ou les deux (C) ? |

**Proposition agent MVP :** Q-015 = privé + devnet ; Q-016 = C (les deux).

---

## 9. Prochaine action recommandée

1. Répondre Q-015 / Q-016 (une ligne chacune).
2. Ordre : **« Lance Phase 2 »** (PoL scorer) puis Phase 3 (C + devnet + rewards).

---

**Fin rapport 005**
