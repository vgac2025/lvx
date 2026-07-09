# Référence API ARTCB — v0.4 (juillet 2026)

**Base URL :** `http://127.0.0.1:8000/api/v1`  
**CLI :** `python3 scripts/artcb_cli.py <commande>`  
**Console UI :** `/console` (mêmes commandes)  
**OpenAPI :** `http://127.0.0.1:8000/docs`

Variable d'environnement CLI : `ARTCB_API_BASE=http://host:port`

---

## Core

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/health` | Santé API |
| GET | `/metrics` | Métriques système |
| POST | `/encode` | Encoder texte → IR |
| POST | `/decode` | Décoder graphe |
| GET | `/graph/{graph_id}` | Graphe IR |
| GET | `/node/{node_id}` | Nœud IR |
| POST | `/search` | Recherche sémantique |
| POST | `/store` | Gravure bloc (private/public/group) |
| POST | `/agents/run` | Dual-agent Explorateur + Critique |
| GET | `/rtleg/events` | Timeline RT-LEG |

## Chaîne & PoL

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/chain` | Liste blocs (`?visibility=&group_id=`) |
| GET | `/chain/block/{index}` | Détail bloc |
| GET | `/chain/verify` | Vérification intégrité |
| GET | `/pol/score` | Score PoL courant |

## Wallets

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/wallet/create` | Créer wallet |
| GET | `/wallet/list` | Lister wallets |
| POST | `/wallet/balance` | Balance par adresse |
| GET | `/wallet/balance/{address}` | Balance |

## Minage

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/mining/pipeline` | Pipeline local OU pool (`use_distributed_pool`) |
| POST | `/mining/bulk` | Minage par lots connecteur |

Corps `mining/pipeline` clés :
- `use_distributed_pool` (bool, défaut false) — calcul local
- `encrypt_transport` (bool, true) — **obligatoire** si distribué
- `visibility` : `private` \| `public` \| `group`
- `group_id`, `actor_address`, `wallet_name`, `auto_finalize`, `chunk_chars`

## Pool E2E (ML-KEM)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/pool/status` | État pool + crypto |
| GET/PUT | `/pool/preferences` | Préférences utilisateur |
| POST | `/pool/run` | **Entrée unifiée** local / distribué |
| GET | `/pool/jobs` | Liste jobs |
| GET | `/pool/jobs/{id}` | Détail job |
| POST | `/pool/jobs` | Créer job chiffré |
| POST | `/pool/jobs/{id}/dispatch` | Dispatch workers |
| POST | `/pool/incoming` | Recevoir chunk (worker) |
| GET | `/pool/incoming` | Chunks en attente |
| POST | `/pool/incoming/process-all` | Traiter localement |
| POST | `/pool/jobs/{id}/results` | Callback résultat chiffré |
| POST | `/pool/jobs/{id}/finalize` | Finalize + bloc PoL |

Contextes KEM : `artcb-pool-chunk-v1`, `artcb-pool-result-v1`

## P2P devnet

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/p2p/status` | Identité nœud + ML-KEM |
| GET/POST/DELETE | `/p2p/peers` | Gestion pairs |
| GET | `/p2p/blocks/public` | Blocs publics pull |
| GET | `/p2p/blocks/incoming` | Archive entrante |
| POST | `/p2p/blocks/receive` | Réception chiffrée |
| POST | `/p2p/sync` | Sync tous pairs |

## Groupes

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST/GET | `/groups` | CRUD groupes |
| GET | `/groups/by-code/{code}` | Par join code |
| POST | `/groups/join-requests` | Demande adhésion |
| POST | `/groups/join-requests/sign-with-wallet` | Signature wallet |
| GET/POST | `/groups/{id}/...` | Membres, approve, dissolve |

## Gouvernance

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/governance/proposals` | Propositions |
| POST | `/governance/proposals` | Créer |
| POST | `/governance/vote` | Voter |

## Connecteurs & multimodal

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/connectors/formats` | 50+ extensions |
| GET/POST/DELETE | `/connectors` | Gestion connecteurs |
| POST | `/connectors/{id}/test` | Test connexion |
| POST | `/connectors/{id}/learn` | Ingestion apprentissage |

## Notifications

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET/POST/DELETE | `/notifications/channels` | Telegram |
| POST | `/notifications/send` | Envoi |
| POST | `/notifications/broadcast` | Broadcast |

## Dashboard

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/dashboard/logs/demo-live` | Log démo |
| GET | `/dashboard/logs/mining-latest` | Dernier minage |
| GET | `/dashboard/founders/allocation` | Founders |
| GET | `/dashboard/mining/status` | Statut minage |
| GET | `/dashboard/wallet/{address}/rewards` | Rewards |

## WebSocket

| Endpoint | Description |
|----------|-------------|
| `/ws/graph/{session_id}` | Encodage temps réel |

---

## Exemples CLI

```bash
# Santé
python3 scripts/artcb_cli.py health

# Wallet + agents + store private
python3 scripts/artcb_cli.py wallet create --name demo
python3 scripts/artcb_cli.py agents --text "Décision importante pour ARTCB."
python3 scripts/artcb_cli.py store --graph-id g_xxx --visibility private

# Minage local public
python3 scripts/artcb_cli.py mining pipeline --text "..." --visibility public --wallet demo --actor artcb1...

# Pool distribué chiffré (private / public / group)
python3 scripts/artcb_cli.py pool run --text "..." --distributed --visibility group --group-id g_abc --auto-finalize

# P2P
python3 scripts/artcb_cli.py p2p status
python3 scripts/artcb_cli.py p2p add-peer --host 192.168.1.2 --port 8000 --kem <hex>
python3 scripts/artcb_cli.py p2p sync
```

## Règles sécurité

1. **Par défaut** : calcul 100 % local (`use_distributed_pool=false`)
2. **Pool distribué** : chiffrement ML-KEM **obligatoire** — refus API sinon
3. **Blocs private** : jamais sync P2P
4. **Groupe** : `group_id` + membre `actor_address` requis

---

**Dernière mise à jour :** 2026-07-09 — audit API/CLI complet (rapport 067)
