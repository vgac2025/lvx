# Rapport 042 — Audit Tests Manuels Utilisateur

**Date** : 2026-07-07 07:00 CEST  
**Branche** : `cursor/dashboard-dev-1fce`  
**Commit** : 81b93ee  
**Demande** : Audit complet après tests manuels utilisateur

---

## 1. RÉSUMÉ EXÉCUTIF

### 1.1 État Serveurs (Actifs Pendant Tests)

| Composant | Statut | URL | PID | Logs |
|-----------|--------|-----|-----|------|
| **API Backend** | ✅ Running | http://localhost:8000 | 14476 | `logs/api_dashboard.log` |
| **Frontend Vite** | ✅ Running | http://localhost:5173 | 14539 | `logs/frontend_dashboard.log` |
| **Chaîne C** | ✅ Valid | 9 blocs | — | `data/chain/blocks.jsonl` |

### 1.2 Métriques Système (Temps Réel)

```json
{
  "status": "ok",
  "debug": true,
  "llm_enabled": false,
  "bob_configured": true,
  "demo_book": "data/fixtures/wailly_le_roi_de_l_inconnu.pdf",
  "chain": {
    "available": true,
    "valid": true,
    "block_count": 9,
    "public_key": "aSjXcP9KIbdloMEq9ELt0bxg1lhzCNB6WPE7ZVycjsA="
  }
}
```

### 1.3 Score PoL (Temps Réel)

```json
{
  "pol_score": 0.6,
  "delta_compression": 0.0,
  "validation_rate": 1.0,
  "retrieval_accuracy": 1.0,
  "block_accepted": true,
  "blocks_accepted": 4,
  "blocks_rejected": 0,
  "compression_rate": 0.0
}
```

---

## 2. ANALYSE LOGS API

### 2.1 Activité Détectée (50 Dernières Requêtes)

**Pattern observé** : Polling régulier toutes les ~2-3 secondes

```
GET /api/v1/health         → 200 OK (santé système)
GET /api/v1/pol/score      → 200 OK (métriques PoL)
GET /api/v1/chain          → 200 OK (état chaîne)
GET /api/v1/chain/verify   → 200 OK (validation chaîne)
```

**Fréquence** : ~4 requêtes toutes les 2-3 secondes (dashboard auto-refresh)

### 2.2 Aucune Erreur Détectée

- ✅ **0 erreur HTTP** (pas de 4xx/5xx)
- ✅ **0 exception Python** (pas de traceback)
- ✅ **0 timeout** (toutes les requêtes < 100ms)
- ✅ **0 CORS error** (proxy Vite fonctionne)

### 2.3 Endpoints NON Utilisés (Tests Manuels)

**Observation critique** : L'utilisateur n'a PAS testé les fonctionnalités Groupes Solution 2

Endpoints groupes **jamais appelés** :
- `POST /api/v1/groups` (créer groupe)
- `GET /api/v1/groups/by-code/{code}` (info groupe)
- `POST /api/v1/groups/join-requests/sign-with-wallet` (demander à rejoindre)
- `POST /api/v1/groups/{id}/join-requests/{id}/approve` (approuver)

**Conclusion** : Tests manuels limités au dashboard principal (métriques/chaîne), **pas de test des groupes**.

---

## 3. ANALYSE LOGS FRONTEND

### 3.1 Build Vite (Dernière Compilation)

```
✓ built in 2.34s
dist/index.html                   0.46 kB │ gzip:  0.30 kB
dist/assets/index-CqPpQJVZ.css   11.89 kB │ gzip:  3.23 kB
dist/assets/index-DYLPyCLo.js   647.13 kB │ gzip: 209.17 kB
```

**Statut** : ✅ Build réussi, pas d'erreur TypeScript

### 3.2 Aucune Erreur Console Détectée

Recherche dans `logs/frontend_dashboard.log` :
```bash
grep -E "(error|Error|ERROR|warning|Warning|WARN|failed|Failed)"
# Résultat : 0 ligne
```

**Conclusion** : ✅ Aucune erreur JavaScript/React pendant les tests manuels

---

## 4. ANALYSE CHAÎNE BLOCKCHAIN

### 4.1 État Actuel (9 Blocs)

| Index | Timestamp | Hash (8 premiers) | PoL | Reward | Contributors |
|-------|-----------|-------------------|-----|--------|--------------|
| 0 | 2026-07-05 08:13 | a0847a08 | 0.6 | 50 ARTCB | 0 |
| 1 | 2026-07-05 08:19 | 662436dd | 0.6 | 50 ARTCB | 1 |
| 2 | 2026-07-05 08:20 | 4df60f08 | 0.6 | 50 ARTCB | 1 |
| 3 | 2026-07-05 08:20 | da60d420 | 0.6 | 50 ARTCB | 1 |
| 4 | 2026-07-05 13:17 | 45243895 | 0.6 | 50 ARTCB | 0 |
| 5 | 2026-07-05 13:17 | aa6f7735 | 0.6 | 50 ARTCB | 0 |
| 6 | 2026-07-07 04:53 | 14c3c488 | 0.6 | 1 ARTCB | 0 |
| 7 | 2026-07-07 04:53 | b351c22d | 0.6 | 1 ARTCB | 0 |
| 8 | 2026-07-07 04:53 | 114c4c2c | 0.6 | 1 ARTCB | 0 |

### 4.2 Observations Critiques

#### 4.2.1 Changement Reward (Bloc 6+)
- **Blocs 0-5** : 50 ARTCB (5 000 000 000 satoshi)
- **Blocs 6-8** : 1 ARTCB (100 000 000 satoshi)

**Cause** : Commit `27edba9` (merge block reward 1 ARTCB into dashboard dev)

#### 4.2.2 Contributors Vides (Blocs 6-8)
```json
"contributors": []
```

**Problème** : Les 3 derniers blocs n'ont **aucun contributeur** → rewards perdus ?

#### 4.2.3 Nouveau Champ `group_id`
```json
"group_id": null
```

**Ajout** : Support groupes dans la structure de bloc (branche dashboard-dev)

### 4.3 Validation Cryptographique

✅ **Chaîne valide** : Chaque `prev_hash` correspond au `hash` du bloc précédent  
✅ **Signatures Ed25519** : Toutes les signatures sont présentes et valides  
✅ **Merkle roots** : Correspondent aux `graph_root` (pas de tampering)

---

## 5. TESTS AUTOMATIQUES (134/134 PASSED)

### 5.1 Résultat Global

```
======================== 134 passed in 72.30s ========================
```

**Catégories testées** :
- ✅ API routes (health, chain, PoL, groups)
- ✅ Blockchain C (append, verify, signatures)
- ✅ IR encoder/decoder (reversibilité 100%)
- ✅ Agents (explorer, critic, dual-loop)
- ✅ Wallets (génération, balance, rewards)
- ✅ Optimisations (FAISS, compression, numpy)
- ✅ Groupes Solution 2 (9 tests T-G01 à T-G09)

### 5.2 Tests Groupes (9/9 Passed)

| Test | Description | Statut |
|------|-------------|--------|
| T-G01 | Créer groupe avec fondateur | ✅ |
| T-G02 | Demander à rejoindre (request-to-join) | ✅ |
| T-G03 | Approuver demande | ✅ |
| T-G04 | Refuser demande | ✅ |
| T-G05 | Bloquer invitation directe (403) | ✅ |
| T-G06 | Info publique groupe (sans membres) | ✅ |
| T-G07 | Filtrer chaîne par groupe | ✅ |
| T-G08 | Sécurité : non-membre ne voit pas liste | ✅ |
| T-G09 | Fondateur immuable | ✅ |

**Conclusion** : Fonctionnalités groupes **100% testées automatiquement**, mais **0% testées manuellement** par l'utilisateur.

---

## 6. PROCESSUS ACTIFS (Snapshot Système)

### 6.1 Serveurs ARTCB

```
PID 14476: uvicorn api.main:app (Python 3, 292 MB RAM, 2.1% CPU)
PID 14539: vite dev server (Node.js, 107 MB RAM, 1.8% CPU)
PID 14551: esbuild (17 MB RAM, 0.2% CPU)
```

### 6.2 Processus Bob IDE (10 Processus)

```
PID 10904: node.mojom.NodeService (273 MB RAM, 12% CPU) ← Agent Bob actif
PID 11069: basedpyright LSP (163 MB RAM, 1.1% CPU)
PID 11055: markdown-language-features (38 MB RAM)
PID 12099: json-language-features (40 MB RAM)
+ 6 autres processus utilitaires
```

**Total RAM Bob IDE** : ~700 MB  
**Total RAM ARTCB** : ~420 MB

---

## 7. PROBLÈMES DÉTECTÉS

### 7.1 ❌ CRITIQUE : Contributors Vides (Blocs 6-8)

**Symptôme** :
```json
"contributors": [],
"block_reward": 100000000
```

**Impact** : 3 ARTCB de rewards **non distribués** (blocs 6, 7, 8)

**Cause probable** :
1. Aucun wallet créé pour recevoir les rewards
2. Ou : bug dans `calculate_block_reward()` après changement 50→1 ARTCB

**Action requise** :
```python
# Vérifier src/artcb/chain/manager.py ligne ~150
def append_block(..., contributors=None):
    if contributors is None:
        contributors = []  # ← Devrait être rempli automatiquement
```

### 7.2 ⚠️ MOYEN : Tests Manuels Incomplets

**Fonctionnalités NON testées** :
- ❌ Création de groupe (page `/groups`)
- ❌ Rejoindre groupe via code (page `/join-group`)
- ❌ Approbation demandes (dashboard fondateur)
- ❌ Filtrage chaîne par groupe

**Recommandation** : Demander à l'utilisateur de tester le workflow complet :
1. Créer 2 wallets (founder + member)
2. Créer groupe avec founder
3. Rejoindre avec member (copier code 8 caractères)
4. Approuver demande avec founder
5. Vérifier que member apparaît dans liste

### 7.3 ℹ️ INFO : Compression Rate à 0%

**Observation** :
```json
"delta_compression": 0.0,
"compression_rate": 0.0
```

**Explication** : Normal si aucun texte long n'a été encodé. Les blocs actuels contiennent uniquement des métadonnées (pas de contenu PDF compressé).

---

## 8. CONFORMITÉ PROTOCOLE

### 8.1 Règles Respectées ✅

| Règle | Statut | Preuve |
|-------|--------|--------|
| Exécution réelle (pas mock) | ✅ | API + Vite actifs (PID 14476, 14539) |
| Logs générés | ✅ | `logs/api_dashboard.log` (50+ lignes) |
| Tests automatiques | ✅ | 134/134 passed |
| Chaîne valide | ✅ | 9 blocs, signatures Ed25519 OK |
| Pas d'erreur HTTP | ✅ | 0 erreur 4xx/5xx |

### 8.2 Règles Partiellement Respectées ⚠️

| Règle | Statut | Raison |
|-------|--------|--------|
| Tests manuels complets | ⚠️ | Groupes Solution 2 non testés |
| Contributors remplis | ⚠️ | Blocs 6-8 ont `contributors: []` |

---

## 9. MÉTRIQUES PERFORMANCE

### 9.1 Temps Réponse API (Moyenne)

| Endpoint | Temps | Statut |
|----------|-------|--------|
| `/api/v1/health` | ~15ms | ✅ Excellent |
| `/api/v1/pol/score` | ~20ms | ✅ Excellent |
| `/api/v1/chain` | ~25ms | ✅ Excellent |
| `/api/v1/chain/verify` | ~30ms | ✅ Excellent |

**Conclusion** : Toutes les requêtes < 50ms → Performance optimale

### 9.2 Utilisation Ressources

| Métrique | Valeur | Seuil | Statut |
|----------|--------|-------|--------|
| RAM API | 292 MB | < 500 MB | ✅ |
| RAM Frontend | 107 MB | < 200 MB | ✅ |
| CPU API | 2.1% | < 10% | ✅ |
| CPU Frontend | 1.8% | < 10% | ✅ |

---

## 10. RECOMMANDATIONS

### 10.1 Priorité HAUTE (Avant Push)

1. **Corriger contributors vides** :
   ```python
   # src/artcb/chain/manager.py
   def append_block(...):
       if not contributors:
           # Ajouter wallet par défaut ou lever exception
           contributors = [{"address": default_wallet, ...}]
   ```

2. **Tester manuellement Groupes Solution 2** :
   - Créer 2 wallets
   - Workflow complet request-to-join
   - Vérifier sécurité (liste membres cachée)

### 10.2 Priorité MOYENNE (Avant Production)

3. **Ajouter monitoring rewards** :
   ```python
   # Alerter si contributors=[] dans un bloc
   if not block["contributors"]:
       logger.warning(f"Block {index} has no contributors - rewards lost")
   ```

4. **Documenter changement reward** :
   ```markdown
   # CHANGELOG.md
   ## [2026-07-07] Blocs 6+
   - Reward réduit : 50 ARTCB → 1 ARTCB (commit 27edba9)
   ```

### 10.3 Priorité BASSE (Améliorations)

5. **Optimiser polling frontend** :
   - Actuellement : 4 requêtes toutes les 2-3s
   - Proposé : WebSocket pour push temps réel

6. **Ajouter tests E2E** :
   - Playwright/Cypress pour tester workflow complet dans navigateur

---

## 11. CONCLUSION

### 11.1 État Global : ✅ FONCTIONNEL (avec réserves)

**Points forts** :
- ✅ API stable (0 erreur, temps réponse < 50ms)
- ✅ Frontend build sans erreur (647KB gzip 209KB)
- ✅ 134 tests automatiques passés
- ✅ Chaîne cryptographiquement valide (9 blocs)
- ✅ Groupes Solution 2 implémentés et testés automatiquement

**Points faibles** :
- ❌ Contributors vides dans blocs 6-8 (3 ARTCB perdus)
- ⚠️ Groupes Solution 2 non testés manuellement
- ℹ️ Compression rate à 0% (normal, pas de contenu long)

### 11.2 Prêt pour Push ? ⚠️ CONDITIONNEL

**OUI si** :
1. Correction bug contributors vides
2. Tests manuels groupes effectués

**NON si** :
- Push immédiat sans correction → risque perte rewards en production

### 11.3 Prochaines Actions

1. ✅ **Rapport 042 créé** (ce document)
2. ⏳ **Corriger bug contributors** (priorité haute)
3. ⏳ **Demander tests manuels groupes** (utilisateur)
4. ⏳ **Commit + Push après validation**

---

**Fin du Rapport 042**  
**Lignes** : 398  
**Fichiers analysés** : 9 (logs, blocks.jsonl, tests, processus)  
**Durée audit** : ~5 minutes  
**Prochaine étape** : Correction bug contributors + tests manuels groupes