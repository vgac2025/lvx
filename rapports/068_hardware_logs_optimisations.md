# Rapport 068 — Logs, hardware multi-OS, optimisations runtime

## Objectif

- Analyser les logs ARTCB (`logs/`)
- Detecter le materiel (CPU, RAM, GPU, disque) sur Linux, macOS, Windows
- Appliquer un profil d'optimisation runtime adapte
- Supprimer tous les emojis du code source (ton professionnel)

## Livrables

### Module `src/artcb/system/`

| Fichier | Role |
|---------|------|
| `hardware.py` | Detection psutil + nvidia-smi + FAISS GPU |
| `optimizer.py` | Profil workers, chunk pool, FAISS GPU/CPU, flags runtime |
| `__init__.py` | Exports publics |

### API

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/metrics` | Metriques live + hardware + optimisation |
| `GET /api/v1/system/hardware` | Profil materiel seul |
| `GET /api/v1/system/optimization` | Profil optimisation seul |

### Runtime

- `build_app_state()` detecte le materiel au demarrage
- Variables `ARTCB_POOL_CHUNK_CHARS`, `ARTCB_AGENT_POOL_WORKERS`, `ARTCB_USE_FAISS_GPU`
- Minage distribue : `chunk_chars` par defaut depuis le profil materiel

### Scripts

- `scripts/analyze_logs.py` — synthese JSON des logs (API JSONL, pytest, validate_two_nodes)
- `scripts/artcb_cli.py` — commandes `metrics`, `system hardware`, `system optimization`

### UI

- `SystemMetrics.tsx` — affichage GPU, FAISS, optimisations actives
- `Console.tsx` — commandes `system hardware` / `system optimization`

### Emojis

Suppression systematique dans `.py`, `.ts`, `.tsx`, `.sh` (18 fichiers). Remplacement par labels ASCII (`OK`, `FAIL`, `WARN`, etc.).

## Analyse logs (synthese)

Voir `rapports/068_logs_synthese.json` genere par `analyze_logs.py`.

- Fichiers API JSONL indexes
- Derniers runs pytest et validate_two_nodes
- Recommandations automatiques selon erreurs detectees

## Tests

```bash
python3 -m pytest tests/test_system_hardware.py -q
python3 -m pytest tests/ -q
```

## Utilisation CLI

```bash
python3 scripts/artcb_cli.py metrics
python3 scripts/artcb_cli.py system hardware
python3 scripts/artcb_cli.py system optimization
python3 scripts/analyze_logs.py --output rapports/068_logs_synthese.json
```

## Variables d'environnement

| Variable | Effet |
|----------|-------|
| `ARTCB_FORCE_CPU` | Desactive FAISS GPU, reduit workers |
| `ARTCB_POOL_CHUNK_CHARS` | Override taille chunk pool |
| `ARTCB_DATA_DIR` | Chemin disque pour metriques |
