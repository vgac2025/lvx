# Rapport 070 — Zero dette technique (warnings, lint, build)

## Corrections appliquees

### Pytest — 0 warning
- **Cause** : `multiprocessing.Pool` (fork) dans `pdf_loader.py` sous processus multi-thread (pytest)
- **Fix** : `ThreadPoolExecutor` pour extraction PDF parallele (pas de fork)
- **Fix** : `ProcessPoolExecutor` avec contexte `spawn` dans `pool_manager.py`
- **Garde-fou** : `filterwarnings = ["error::DeprecationWarning"]` dans `pyproject.toml`

**Resultat** : `234 passed`, **0 warning** (avant : 6 DeprecationWarning)

### Ruff — 0 erreur
- 42 erreurs F401/F841/F541 corrigees automatiquement
- 753 corrections style (imports, whitespace, SIM, UP)
- 4 corrections manuelles : B904 (`raise ... from exc`), B017 (`InvalidTag`), SIM102 pipeline
- Configuration : `[tool.ruff.lint]` select E,F,W,I,UP,B,SIM — line-length 120

### Frontend TypeScript — build OK
- **commands.ts** : restaure en TypeScript (fichier avait ete corrompu en Python)
- **Memorize.tsx** : `PolMetrics` complet + variable inutilisee retiree
- **Build** : `tsc -b && vite build` OK

### Scripts
- Imports inutilises supprimes (`mine_learning.py`, `validate_two_nodes.py`, etc.)
- f-strings sans placeholder corriges

## Verification

```bash
python3 -m ruff check src tests scripts    # All checks passed
python3 -m pytest tests/ -q               # 234 passed, 0 warnings
cd frontend && npm run build              # OK
```

## Commit

Pousse directement sur `main`.
