# ARTCB — AI Reasoning Trace & Cognitive Blockchain

**Mémoire persistante pour agents IA — sans perte, sans résumés destructeurs.**

[![Hackathon](https://img.shields.io/badge/RAISE%20Summit-2026-blue)](https://cerebralvalley.ai/e/raise-summit-hackathon)
[![Piste](https://img.shields.io/badge/Piste-Cursor-purple)](https://github.com/vgac2025/lvx)
[![Statut](https://img.shields.io/badge/Statut-Spec%20complète-green)]()

---

## Le problème

Quand tu travailles longtemps avec une IA, elle **oublie** ce que vous vous êtes dit. Chaque résumé détruit des nuances. Impossible de retrouver un raisonnement précis d'il y a 3 semaines.

## La solution ARTCB

Chaque pensée devient un **nœud signé** dans un graphe de connaissances :

- **Encodage IR** — compression sémantique réversible à 100 %
- **RT-LEG** — graphe d'exécution temporel (traçabilité complète)
- **Blockchain Light** — intégrité cryptographique publique/privée
- **Proof-of-Learning** — apprentissage mesurable et vérifiable
- **Dual Agents** — Explorateur (génère) + Critique (valide/compresse)

## Statut actuel

| Phase | Statut |
|-------|--------|
| Spécification | ✅ Complète (CDC v1.1) |
| Phase 1 — IR Engine | ✅ Terminée (20 tests, 100 % réversibilité) |
| Phase 2 — Backend API | ⏳ En attente d'ordre |

## Documentation

| Document | Description |
|----------|-------------|
| [CAHIER_DES_CHARGES_ARTCB](./CAHIER_DES_CHARGES_ARTCB) | Spécification MVP Avancé complète |
| [INDEX_ARTCB](./INDEX_ARTCB) | Cartographie et ordre de lecture |
| [IDÉE_ARTCB](./IDÉE_ARTCB) | Vision projet et analyse RT-LEG |
| [ROADMAP_GENERAL_ARTCB](./ROADMAP_GENERAL_ARTCB) | Phases d'implémentation |
| [CONFIGURATION_ARTCB](./CONFIGURATION_ARTCB) | Config, dépendances, clés API |
| [CHECKLIST_PRE_DEV_ARTCB](./CHECKLIST_PRE_DEV_ARTCB) | Gate avant développement |

## Installation

```bash
git clone git@github.com:vgac2025/lvx.git
cd lvx
pip install -e ".[dev]"
python3 -m pytest tests/ -v
```

### CLI IR Engine (Phase 1)

```bash
# Encoder
python3 scripts/ir_cli.py encode "Observer le monde pour apprendre."

# Décoder (depuis fichier JSON)
python3 scripts/ir_cli.py decode graph.json
```

## Hackathon RAISE Summit 2026 — Piste Cursor

- **Soumission :** 5 juillet 2026, 12h00 CEST
- **Repo :** https://github.com/vgac2025/lvx
- **Discord :** https://discord.com/invite/N26eKqmR42

## Licence

Open source — repo public (exigence hackathon).
