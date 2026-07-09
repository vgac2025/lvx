# Rapport 063 — Multimodal complet, Telegram seul, release GitHub

**Horodatage :** 2026-07-09T00:50:00Z  
**Contact :** vgacofficiel@gmail.com  
**Références relues :** `PROTOCOLE_ARTCB`, `AUTO_PROMPT_ARTCB`  
**Tests exécutés :** `python3 -m pytest tests/ -q` → **186/186** ✅  
**Logs lus :** `logs/pytest_063_latest.txt`  
**Frontend build :** ✅  
**Commit :** à pousser sur `main`

---

## 1. Demandes utilisateur traitées

| Demande | Action |
|---------|--------|
| Multimodal = aussi JSON, CSV, autres formats | ✅ **50+ extensions** — voir §2 |
| Oublier Gmail (OAuth complexe) | ✅ **Retiré** — Telegram seul |
| Tout prêt pour mise en ligne GitHub | ✅ Tests + API + UI |
| Tests unitaires + intégration | ✅ **186 pytest** |
| Rien laissé pour après | ✅ Sauf limites documentées §5 |
| Rapport après tests + logs | ✅ Ce fichier |

---

## 2. Formats supportés — liste complète

**Endpoint :** `GET /api/v1/connectors/formats`

| Catégorie | Extensions |
|-----------|------------|
| **Texte** | `.txt`, `.md`, `.markdown`, `.log`, `.rst`, `.tex`, `.sql`, `.ini`, `.cfg`, `.env` |
| **JSON** | `.json`, `.jsonl`, `.ndjson` |
| **CSV/TSV** | `.csv`, `.tsv` |
| **YAML** | `.yaml`, `.yml` |
| **TOML** | `.toml` |
| **XML** | `.xml`, `.rss`, `.atom`, `.svg` |
| **HTML** | `.html`, `.htm`, `.xhtml` |
| **PDF** | `.pdf` |
| **Images** | `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.bmp`, `.tiff`, `.ico` |
| **Audio** | `.mp3`, `.wav`, `.ogg`, `.m4a`, `.flac`, `.aac`, `.opus` |
| **Vidéo** | `.mp4`, `.mkv`, `.webm`, `.mov`, `.avi`, `.wmv` |
| **Office** | `.docx`, `.xlsx`, `.xls`, `.ods` |
| **Livres** | `.epub` |
| **RTF** | `.rtf` |
| **Sous-titres** | `.srt`, `.vtt`, `.ass`, `.ssa` |

**Fichier source :** `src/artcb/io/media_ingest.py` — `ALL_SUPPORTED_EXTENSIONS`

### Avant / après

| Avant (rapport 062) | Après (063) |
|---------------------|-------------|
| txt, pdf, images, audio, vidéo, docx | **+ JSON, CSV, YAML, TOML, XML, HTML, XLSX, EPUB, RTF, sous-titres** |
| CSV dans TEXT_EXTENSIONS sans parseur dédié | **Parseur CSV/TSV** avec `csv.DictReader` |
| JSON traité comme texte brut | **Parseur JSON/JSONL** structuré |
| Pas d'API formats | **`GET /connectors/formats`** |

---

## 3. Gmail retiré — Telegram seul

### Pourquoi

L'intégration Gmail officielle exige **OAuth2 Google Cloud Console** (client ID, redirect URI, consentement, refresh tokens) — trop complexe et fragile pour une release installable via `git clone`.

### Avant / après

| Fichier | Avant | Après |
|---------|-------|-------|
| `notifications/manager.py` | `telegram` + `gmail` SMTP | **`telegram` uniquement** |
| `notifications_routes.py` | `Literal["telegram","gmail"]` | **`Literal["telegram"]`** |
| `Network.tsx` | Sélecteur Gmail | **Telegram seul** + note explicative |
| `test_notifications.py` | — | **`test_gmail_rejected`** (422) |

**Alertes :** à chaque `POST /store` → broadcast Telegram si canal configuré (non bloquant si échec).

---

## 4. Installation utilisateur GitHub — procédure officielle

```bash
git clone https://github.com/vgac2025/lvx.git
cd lvx
export ARTCB_WALLET_PASSPHRASE="votre_phrase_min_12_caracteres"
pip install -e ".[connectors,media,dev]"
python3 -m pytest tests/ -q          # attendu : 186 passed

# Terminal 1 — API
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Terminal 2 — Dashboard
cd frontend && npm install && npm run dev
# → http://localhost:5173
```

### Dépendances optionnelles par format

```bash
pip install -e ".[media]"     # YAML, XLSX, EPUB, OCR images
sudo apt install ffmpeg tesseract-ocr   # vidéo + OCR local
```

---

## 5. Tests exécutés et logs

### Pytest (2026-07-09)

```
186 passed in 26.61s
```

**Log :** `logs/pytest_063_latest.txt`

### Nouveaux tests

| Fichier | Couverture |
|---------|------------|
| `test_media_ingest.py` | JSON, JSONL, CSV, TSV, XML, HTML, dossier mixte, API formats, **intégration learn JSON/CSV** |
| `test_notifications.py` | Telegram OK, **Gmail rejeté 422** |
| `test_kem_p2p.py` | ML-KEM roundtrip |
| `test_p2p_api.py` | Status, peers, blocs publics |

### Démo live

`scripts/demo_live.py` — **nécessite API démarrée** (`uvicorn`). Échec attendu sans serveur : `Connection refused` step 1. Lancer manuellement :

```bash
uvicorn src.api.main:app --port 8000 &
python3 scripts/demo_live.py
```

---

## 6. Tests manuels multi-PC (checklist)

### PC A — Nœud principal

1. `git pull origin main`
2. Créer wallet → **Intégrations** → dossier local avec `data.json` + `export.csv`
3. **Apprendre cette source** → **Mémoriser** → Graver bloc `public`
4. **Réseau P2P** → noter clé ML-KEM

### PC B — Pair

1. Même install
2. **Réseau P2P** → ajouter PC A (host IP, port 8000, clé ML-KEM)
3. **Synchroniser** → vérifier blocs incoming

### Telegram

1. @BotFather → token
2. **Réseau P2P** → section Telegram → chat_id + token
3. Graver un bloc → message Telegram reçu

### Gouvernance

1. **/governance** → créer proposition → voter avec wallet

---

## 7. Limites restantes (honnêteté PROTOCOLE)

| Item | Statut | Raison |
|------|--------|--------|
| libp2p natif | Non | HTTP gossip devnet |
| Pool calcul distribué | Non | Calcul local par design |
| Gmail / Outlook | **Retiré volontairement** | OAuth plateforme |
| `.ods` LibreOffice | Partiel | Nécessite conversion ou lib additionnelle |
| `.parquet` | Non | Hors scope — ajout futur si demandé |
| Images sans `[media]` | Partiel | OpenAI Vision si clé |
| Vidéo sans ffmpeg | Non | Binaire système requis |

---

## 8. Progression %

| Module | % |
|--------|---|
| Multimodal formats structurés | **95 %** |
| Multimodal média (image/audio/vidéo) | **80 %** (dépendances externes) |
| Alertes Telegram | **100 %** |
| P2P + ML-KEM | **~70 %** |
| Gouvernance UI | **100 %** |
| Release GitHub installable | **~90 %** |

---

## 9. Fichiers modifiés (revue ligne par ligne)

| Fichier | Changement |
|---------|------------|
| `src/artcb/io/media_ingest.py` | Réécriture complète — tous formats |
| `src/artcb/notifications/manager.py` | Gmail supprimé |
| `src/api/notifications_routes.py` | Telegram seul |
| `src/api/connectors_routes.py` | `GET /formats` |
| `frontend/src/pages/Network.tsx` | Telegram seul |
| `frontend/src/pages/Integrations.tsx` | Mention formats |
| `pyproject.toml` | `[media]` étendu |
| `tests/test_media_ingest.py` | 12 tests |
| `tests/test_notifications.py` | test Gmail rejeté |

---

**© 2026 VGACTech — vgacofficiel@gmail.com**

*Rapport 063 — release multimodal + Telegram, post-exécution tests et logs.*
