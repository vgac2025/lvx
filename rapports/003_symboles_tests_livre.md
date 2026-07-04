# Rapport 003 — Symboles IA, tests livre, clés dev

**Horodatage :** 2026-07-04T21:30:00Z

---

## Symboles originaux IA — OUI, inclus ✅

| Couche | Fichier | Statut |
|--------|---------|--------|
| USP fixes O1, M1… | `grammar.py` | ✅ |
| Macros Ω1, Φ1… | `macros.py` | ✅ |
| **Originaux α1, ∇n…** | **`symbols.py`** | ✅ Phase 1+ |

Voir `LANGAGE_SYMBOLES_ARTCB` pour détails.

---

## Bob CLI = OpenRouter (même rôle)

| OpenRouter (ancien plan) | Bob CLI/IDE (retenu) |
|--------------------------|----------------------|
| Clé API cloud | `BOB_API_KEY` dans `.env` |
| Envoie texte à un LLM | Inférence IBM Bob |
| Enrichit l'encodage IR | Path B optionnel (`ARTCB_LLM_ENABLED`) |

**Priorité A** rule-based reste le défaut validé (23 tests).

---

## Clés en phase dev

- `.env` local **conservé** entre sessions — pas de rotation demandée
- **Jamais** commité sur git
- **Jamais** sur la blockchain

---

## Livre Wailly — tests réels

**Fichier attendu :** `data/fixtures/wailly_le_roi_de_l_inconnu.pdf`

**Statut VM :** PDF absent → 5 tests **skipped**

**Action utilisateur :** copier le PDF vers `data/fixtures/` puis :
```bash
python3 -m pytest tests/test_book_wailly.py -v
```

Guide complet : `GUIDE_TESTS_ARTCB`

---

## Résultats tests

```
23 passed, 5 skipped
```
