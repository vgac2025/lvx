# Rapport 062 — Implémentation Phase 8 : P2P, ML-KEM, multimodal, alertes, gouvernance UI

**Horodatage :** 2026-07-09T00:30:00Z  
**Contact :** vgacofficiel@gmail.com  
**Ordre utilisateur :** GO explicite — implémentation bout en bout  
**Références relues :** `PROTOCOLE_ARTCB`, `AUTO_PROMPT_ARTCB`, `RESEAU_DEVNET_ARTCB`, `rapports/061`  
**Tests :** **175/175 pytest** ✅  
**Progression globale :**

| Composant | Avant | Après |
|-----------|-------|-------|
| P2P artcb-devnet | 0 % | **~70 %** (HTTP gossip, pas libp2p) |
| Transport ML-KEM | 0 % | **~85 %** |
| Multimodal ingestion | ~15 % | **~75 %** |
| OpenRouter / Ollama | 0 % | **100 %** connecteurs |
| Alertes Telegram/Gmail | 0 % | **~90 %** |
| UI Gouvernance | 0 % | **100 %** |
| UI Réseau P2P | 0 % | **100 %** |

---

## 1. Ce qui a été implémenté (réel, testé)

### A) P2P multi-nœuds — `artcb-devnet-1`

| Fichier | Rôle |
|---------|------|
| `src/artcb/p2p/node_identity.py` | Identité nœud + clé ML-KEM persistante |
| `src/artcb/p2p/peers.py` | Registre pairs |
| `src/artcb/p2p/sync.py` | Sync pull/push blocs **publics** |
| `src/artcb/p2p/public_archive.py` | Archive blocs distants reçus |
| `src/api/p2p_routes.py` | API REST `/api/v1/p2p/*` |
| `frontend/src/pages/Network.tsx` | UI Réseau P2P + alertes |

**Endpoints :**
- `GET /api/v1/p2p/status`
- `GET/POST/DELETE /api/v1/p2p/peers`
- `GET /api/v1/p2p/blocks/public` — blocs publics locaux
- `GET /api/v1/p2p/blocks/incoming` — blocs reçus des pairs
- `POST /api/v1/p2p/blocks/receive` — réception chiffrée ML-KEM
- `POST /api/v1/p2p/sync` — sync tous les pairs

**Règle sécurité appliquée :** blocs `private` **jamais** synchronisés (`private_never_synced: true`).

### B) Transport ML-KEM-768

| Fichier | Rôle |
|---------|------|
| `src/artcb/crypto/kem.py` | ML-KEM-768 encapsulation + AES-256-GCM |

Push chiffré vers pairs via `encrypt_payload` / `decrypt_payload`.  
Tests : `tests/test_kem_p2p.py`

### C) Sources multimodales

| Fichier | Rôle |
|---------|------|
| `src/artcb/io/media_ingest.py` | texte, PDF, images (OCR/vision), audio (Whisper), vidéo (ffmpeg), DOCX |
| `src/artcb/connectors/sources.py` | connecteurs `local_folder`, `pdf_file` |
| `frontend/src/pages/Integrations.tsx` | UI dossier + PDF + disclaimer |

**Formats supportés :**

| Format | Méthode | Dépendance |
|--------|---------|------------|
| txt, md, csv, json, html | lecture directe | — |
| PDF | pypdf | incluse |
| Images | Tesseract OCR **ou** OpenAI Vision | optionnel `pytesseract pillow` ou clé OpenAI |
| Audio | OpenAI Whisper API **ou** whisper CLI | clé OpenAI ou `openai-whisper` |
| Vidéo | ffmpeg → audio → transcript | `ffmpeg` système |
| DOCX | python-docx | optionnel `[media]` |

### D) OpenRouter + Ollama

| Provider | Fichier |
|----------|---------|
| `openrouter` | `src/artcb/connectors/llm_router.py` `_openrouter_chat` |
| `ollama` | `src/artcb/connectors/llm_router.py` `_ollama_chat` |

UI Intégrations + tests `test_save_openrouter_connector`

### E) Alertes Telegram / Gmail

| Fichier | Rôle |
|---------|------|
| `src/artcb/notifications/manager.py` | stockage chiffré local |
| `src/api/notifications_routes.py` | CRUD + send + broadcast |
| `src/api/routes.py` | broadcast auto à chaque `POST /store` |

- **Telegram :** bot token + `chat_id` → API `sendMessage`
- **Gmail :** SMTP TLS + mot de passe application

### F) UI Gouvernance

| Fichier | Route |
|---------|-------|
| `frontend/src/pages/Governance.tsx` | `/governance` |
| `frontend/src/api/client.ts` | fonctions governance |

Liste propositions, vote oui/non avec wallet, création proposition VGACTech.

---

## 2. Ce qui N'EST PAS possible / limites honnêtes

| Affirmation | Réalité |
|-------------|---------|
| « Blockchain 100 % décentralisée » | **Partiel** — P2P HTTP devnet, pas libp2p ni consensus global |
| « Pool de calcul distribué » | **Non** — calcul reste local ; P2P = sync blocs publics seulement |
| « Fusion chaîne unique mondiale » | **Non** — blocs distants archivés dans `incoming_public.jsonl`, pas re-chaînés |
| « Images sans dépendance » | **Non** — OCR/vision requiert libs ou API cloud |
| « Vidéo sans ffmpeg » | **Non** — ffmpeg obligatoire |
| « Gmail sans mot de passe app » | **Non** — OAuth2 complet non implémenté (SMTP app password seulement) |
| « libp2p natif port 18444 » | **Non** — port documenté ; transport actuel = HTTP sur port API (8000) |
| « Vérification signature bloc distant » | **Partiel** — hash structure vérifié ; signature = clé nœud émetteur (non locale) |

### Pourquoi pas libp2p complet ?

libp2p Python n'est pas une dépendance mature au niveau production pour ce stack. L'implémentation actuelle utilise **HTTP gossip** entre nœuds FastAPI — fonctionnel pour devnet 2+ machines, extensible vers libp2p en Phase 9.

### Pourquoi pas fusion de chaîne ?

Chaque nœud signe avec sa propre `chain.key`. Fusionner les blocs distants dans `blocks.jsonl` casserait la vérification de signature locale. Solution retenue : **archive séparée** `data/p2p/incoming_public.jsonl` + endpoint dédié.

---

## 3. Avant / après — fichiers clés

| Sujet | Avant | Après |
|-------|-------|-------|
| P2P | Spec seule | `src/artcb/p2p/*` + API + UI `/network` |
| ML-KEM | ML-DSA signatures seulement | `src/artcb/crypto/kem.py` transport P2P |
| Images/audio | Impossible | `media_ingest.py` + `local_folder` |
| OpenRouter | Absent | Connecteur + UI |
| Ollama | Absent | Connecteur IA 100 % local |
| Telegram/Gmail | Absent | `notifications/manager.py` + UI |
| Gouvernance UI | API seule | `/governance` |
| Tests | 165 | **175** |

---

## 4. Parcours utilisateur

### Multimodal
1. **Intégrations** → `Dossier local` → chemin + secret `local-folder-key`
2. Déposer txt/pdf/images dans le dossier
3. **Apprendre cette source** → conversion texte → IR → Mémoriser → Graver

### P2P
1. Lancer 2 nœuds (`ARTCB_DATA_DIR` différent, ports 8000 et 8001)
2. **Réseau P2P** → copier clé ML-KEM du pair → Ajouter
3. Miner un bloc `visibility: public` sur nœud A
4. **Synchroniser** sur nœud B → bloc dans `incoming_public`

### Alertes
1. **Réseau P2P** → section Alertes → Telegram bot token + chat_id
2. Chaque `POST /store` envoie notification (non bloquant si échec)

### Gouvernance
1. **Gouvernance** → sélectionner wallet → voter Oui/Non

---

## 5. Installation dépendances optionnelles

```bash
pip install -e ".[connectors,media,dev]"
# Système pour vidéo :
sudo apt install ffmpeg
# OCR local :
sudo apt install tesseract-ocr
```

---

## 6. Variables d'environnement

| Variable | Défaut | Rôle |
|----------|--------|------|
| `ARTCB_KEM_ENABLED` | `true` | Transport ML-KEM P2P |
| `ARTCB_P2P_PORT` | `18444` | Port documenté devnet |
| `ARTCB_DATA_DIR` | `data/` | Données nœud |

---

## 7. Éléments ajoutés (oubliés par l'utilisateur)

- Disclaimer UI « calcul local, pas de pool »
- Archive P2P séparée (pas de fuite blocs privés)
- Broadcast alertes non bloquant sur erreur SMTP/Telegram
- Support Ollama pour IA sans cloud
- Pagination dossier multimédia (banque de fichiers)
- Tests KEM roundtrip + P2P API + notifications mock

---

## 8. Prochaines étapes possibles (non codées)

| Item | Effort | Note |
|------|--------|------|
| libp2p natif | Élevé | Remplacer HTTP gossip |
| OAuth2 Gmail | Moyen | Sans mot de passe app |
| Fusion chaîne fédérée avec clé réseau | Élevé | Consensus multi-nœud |
| Pool calcul opt-in | Recherche | Hors scope actuel |
| Faucet tARTCB | Moyen | `RESEAU_DEVNET_ARTCB` §4 |

---

**© 2026 VGACTech — vgacofficiel@gmail.com**

*Rapport 062 — implémentation Phase 8 suite GO utilisateur.*
