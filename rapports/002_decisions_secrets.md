# Rapport 002 — Décisions utilisateur et symboles originaux IA

**Horodatage :** 2026-07-04T21:00:00Z  
**Phase :** Post Phase 1 — intégration réponses Q-002→Q-010

---

## Réponses utilisateur intégrées

| ID | Décision |
|----|----------|
| Q-002 | **A prioritaire** (rule-based validé 23/23 tests) + **B Bob LLM** en option |
| Q-004 | **Gradium TTS oui** — clé stockée `.env` local |
| Q-006 | Texte démo **exemple CDC** (anglais) |
| Q-009 | Clés **Bob + Gradium + GitHub** → `.env` uniquement |
| Q-010 | Crédits Cursor **actifs** (agent cloud) |
| D-012 | **Symboles originaux IA** — `SymbolRegistry` ajouté |

---

## Avant / Après — symboles IA

**Avant :** USP fixes (O1, M1) + macros (Ω1, Φ1) seulement.

**Après :** `src/artcb/ir/symbols.py` — mint symboles originaux `α1`, `β2`, `∇3` pour concepts inconnus.

**Fichier :** `src/artcb/ir/models.py` — champ `orig_symbols` dans IRGraph.

---

## Sécurité secrets

- `.env` créé localement — **gitignoré, non commité**
- `.env.example` mis à jour **sans secrets**
- ⚠️ Clés transmises en chat — **rotation recommandée**

---

## Tests

```
23 passed in 0.12s
```

+3 tests symboles originaux.

---

## Prochaine étape

Phase 2 : FastAPI + RT-LEG + Agents + PoL (sur ordre « Lance Phase 2 »).
