# Rapport 004 — Intégration PDF Wailly

**Horodatage :** 2026-07-04T21:40:00Z

---

## Source

- Branche distante : `origin/add-wailly-pdf` (commit `153bf5b`)
- Intégration : cherry-pick fichier → `main` (`a022356`)

---

## Fichier

| Élément | Valeur |
|---------|--------|
| Chemin | `data/fixtures/wailly_le_roi_de_l_inconnu.pdf` |
| Taille | ~1.6 Mo |

---

## Tests exécutés

```bash
python3 -m pytest tests/test_book_wailly.py -v
# 5 passed in 4.89s

python3 -m pytest tests/ -v
# 28 passed in 4.78s
```

| Test | Résultat |
|------|----------|
| test_book_file_readable | ✅ |
| test_book_first_pages_reversibility | ✅ 100 % exact |
| test_book_chunk_reversibility | ✅ 5 chunks |
| test_book_orig_symbols_minted | ✅ |
| test_book_node_count_scales | ✅ |

---

## Suite globale

**28/28 tests passent** — dont 5 tests réels sur le livre Wailly.
