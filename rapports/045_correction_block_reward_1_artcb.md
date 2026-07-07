# Rapport 045 — Correction block reward 50 → 1 ARTCB

**Horodatage :** 2026-07-07T04:25:00Z  
**Branche :** `cursor/block-reward-1artcb-1fce`  
**Demande utilisateur :** 50 ARTCB trop élevé pour supply 21M + consommation IA massive

---

## Avant / Après

| Fichier | Avant | Après |
|---------|-------|-------|
| `src/artcb/chain/manager.py` | `INITIAL_REWARD = 50 * 100_000_000` | Import `INITIAL_BLOCK_REWARD_SATOSHI` (= 1 ARTCB) |
| `src/artcb/tokenomics.py` | — | **Nouveau** — source unique |
| `scripts/mine_learning_simple.py` | `50_00000000 >> halving` | `INITIAL_BLOCK_REWARD_SATOSHI >> halving` |
| `TOKENOMICS_ARTCB` §4 | 50 ARTCB | **1 ARTCB** |
| `README.md` | 50 ARTCB | 1 ARTCB |
| `FAQ_NON_EXPERTS_ARTCB.md` | 50 ARTCB | 1 ARTCB |
| `tests/test_wallet_rewards.py` | assertions 50 | assertions 1 / 0.5 / 0.25 |
| `tests/test_pol.py` | split sur 50 | split sur 1 |

**Halving inchangé :** tous les 210 000 blocs. Séquence : **1 → 0,5 → 0,25 → …**

---

## Justification

- Supply plafond **21 000 000 ARTCB** (style Bitcoin)
- 50 ARTCB/bloc × forte activité IA = émission trop rapide
- 1 ARTCB/bloc aligne mieux durée d'émission ~130 ans (même logique halving)

---

## Tests

```
pytest : 96/96 passed
```

---

## Non modifié (PROTOCOLE — rapports historiques intacts)

Rapports 030–039, présentations hackathon — conservés tels quels (archive).
