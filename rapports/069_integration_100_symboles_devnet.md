# Rapport 069 — Integration 100% LANGAGE_SYMBOLES + devnet complet

## Livrables

### Symboles IA (LANGAGE_SYMBOLES_ARTCB — 100%)

| Composant | Fichier |
|-----------|---------|
| Registre persistant | `src/artcb/ir/symbol_store.py` -> `data/symbols/registry.json` |
| Explorateur propositions | `src/artcb/agents/explorer.py` `propose_symbols()` |
| Blocs publics symboles | `public_symbols` dans `ChainBlock` |
| Archive P2P | `src/artcb/p2p/symbol_archive.py` |
| Sync symboles | `src/artcb/p2p/symbol_sync.py` |
| Gossip devnet | `src/artcb/p2p/gossip.py` port 18444 |
| API | `/api/v1/symbols/*`, `/api/v1/p2p/symbols/*`, `/api/v1/p2p/gossip/*` |

### Devnet (RESEAU_DEVNET_ARTCB)

| Composant | Fichier / endpoint |
|-----------|-------------------|
| Faucet tARTCB | `src/artcb/devnet/faucet.py`, `POST /api/v1/devnet/faucet` |
| Script CLI | `scripts/devnet_faucet.py` |
| Chain explorer | `GET /api/v1/chain/explorer` |
| Chain params C | `src/c/chain_params.h` |
| Balance + faucet | `wallet get_balance_with_faucet()` |

### Gradium TTS (Q-004 / D-009)

| Composant | Fichier |
|-----------|---------|
| Client API | `src/artcb/integrations/gradium.py` |
| Endpoint | `POST /api/v1/integrations/gradium/tts` |
| UI Graphe | `GraphPage.tsx` — Gradium puis fallback speechSynthesis |

## Tests

- `test_symbol_store.py` — persistance registre
- `test_explorer_symbols.py` — propositions Explorateur + API
- `test_symbol_p2p_integration.py` — blocs publics + P2P + gossip
- `test_devnet_faucet.py` — faucet + explorer + Gradium fallback

```bash
python3 -m pytest tests/ -q
```

## CLI

```bash
python3 scripts/artcb_cli.py symbols registry
python3 scripts/artcb_cli.py faucet --address artcb1...
python3 scripts/devnet_faucet.py --status
```
