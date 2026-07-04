# Rapport 001 — IR Engine Phase 1

**Horodatage :** 2026-07-04T20:05:00Z  
**Phase :** 1 — Fondations (IR Engine)  
**Branche :** `cursor/phase1-ir-engine-1fce`  
**Mode :** DEBUG activé (PROTOCOLE)

---

## Objectif Phase 1

| Jalon | Critère | Statut |
|-------|---------|--------|
| 1.1 Structure `/src/` | Conforme STRUCTURE_ARTCB | ✅ |
| 1.2 IR Encoder v0.1 | Texte → JSON graphe | ✅ |
| 1.3 IR Decoder v0.1 | JSON graphe → texte original | ✅ |
| 1.4 Tests réversibilité | 10 textes, diff ≤ 1 % | ✅ (100 % exact) |
| 1.5 Rapport + logs | Ce fichier + logs JSON | ✅ |

---

## Fichiers créés

```
src/artcb/
├── __init__.py
├── logging_config.py
└── ir/
    ├── __init__.py
    ├── grammar.py      # NodeType, EdgeType, USP
    ├── models.py       # IRGraph, IRNode, IREdge, IRMacro
    ├── encoder.py      # IREncoder (rule-based)
    ├── decoder.py      # IRDecoder (réversibilité)
    └── macros.py       # Compression Ω, Φ, Ψ
scripts/ir_cli.py
tests/
├── test_ir_reversibility.py
└── test_grammar.py
pyproject.toml
requirements.txt
.env.example
.gitignore
```

---

## Avant / Après

### Avant — aucun code source

Le dépôt ne contenait que de la documentation (`CAHIER_DES_CHARGES_ARTCB`, etc.).

### Après — IR Engine fonctionnel

**Fichier :** `src/artcb/ir/encoder.py`

Encodage rule-based conforme CDC §21 :
- Découpage en phrases avec spans (offsets caractères)
- Classification heuristique → NodeType (F, D, H, R, G, P, E, C)
- Symboles USP (O1, P1, M3…)
- Liens temporels `→t` + causalité `→` si marqueurs détectés
- Checksums sha256 sur source et chaque nœud
- Macros auto si pattern répété ≥ 3 fois

**Fichier :** `src/artcb/ir/decoder.py`

Décodage avec garantie réversibilité :
- Vérification intégrité checksums
- Tri topologique via arêtes temporelles
- Reconstruction par spans → **100 % exact** sur 10 textes de test

---

## Exécution tests

**Commande :**
```bash
python3 -m pytest tests/ -v --tb=short
```

**Résultat :**
```
20 passed in 0.09s
```

**Textes testés (10) :** tous reconstruits à **100 %** (similarity = 1.0, exact = True).

---

## Bug corrigé en cours de Phase 1

| Bug | Cause | Fix |
|-----|-------|-----|
| Découpage 1 seule phrase | Espace inclus dans set de ponctuation fermante | Retirer espace de `\"'») '` dans `_find_sentence_end` |

**Fichier :** `src/artcb/ir/encoder.py` — ligne `_find_sentence_end`

**Avant :**
```python
while j < length and text[j] in '"\'») ':
```

**Après :**
```python
while j < length and text[j] in "\"'»)":
```

---

## Logs générés

| Fichier | Statut |
|---------|--------|
| `logs/20260704_artcb_ir_encoder.json` | ✅ 322 bytes |
| `logs/20260704_artcb_ir_decoder.json` | ✅ 158 bytes |

Logs JSON structurés activés via `ARTCB_DEBUG=true`.

---

## Métriques encodage (texte démo hackathon)

**Input :**
> Nous avons décidé d'utiliser FastAPI pour le backend. Le problème principal est la perte de contexte entre sessions. La solution ARTCB encode chaque raisonnement en graphe signé. Prochaine étape : implémenter l'IR Engine.

| Métrique | Valeur |
|----------|--------|
| Nœuds | 4 |
| Arêtes | 5 (3 temporelles + 2 causales) |
| Types | D, F, F, G |
| Réversibilité | 100 % |
| Compression ratio IR | ~négatif* |

\* Phase 1 : le JSON IR est plus grand que le texte court — la compression macro devient positive sur textes longs répétitifs.

---

## Critères CDC validés

| ID | Exigence | Statut |
|----|----------|--------|
| F-01 | Encodage texte → IR | ✅ |
| F-02 | Reconstruction ≥ 99 % | ✅ (100 %) |
| F-10 | Mode DEBUG | ✅ |
| NF-07 | Zéro mock/stub | ✅ |

---

## Prochaine étape — Phase 2 (sur ordre utilisateur)

- FastAPI 12 endpoints
- RT-LEG events
- Dual Agents Explorateur / Critique
- PoL Scorer
- Rapport `rapports/002_backend.md`

---

**Fin rapport 001 — Phase 1 IR Engine ✅**
