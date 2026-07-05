# Instructions Configuration SSH GitHub — ARTCB MVP

**Date :** 2026-07-05T00:17 UTC  
**Objectif :** Permettre push sur `github.com/vgac2025/lvx`

---

## 1. CLÉ SSH GÉNÉRÉE

**Clé publique à ajouter sur GitHub :**

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDwzvfSpiRH3Otytq6i7UNg4MIrHftmFsK42HOi7A+m4 artcb-mvp@hackathon.raise2026
```

**Fichiers créés :**
- Clé privée : `~/.ssh/github_artcb_lvx`
- Clé publique : `~/.ssh/github_artcb_lvx.pub`

---

## 2. ÉTAPES CONFIGURATION (À FAIRE PAR L'UTILISATEUR)

### Étape 1 : Ajouter la clé sur GitHub

1. Copiez la clé publique ci-dessus (ligne `ssh-ed25519 AAAA...`)
2. Allez sur : https://github.com/settings/keys
3. Cliquez sur **"New SSH key"**
4. Remplissez :
   - **Title :** `ARTCB MVP Hackathon RAISE 2026`
   - **Key type :** `Authentication Key`
   - **Key :** Collez la clé publique
5. Cliquez **"Add SSH key"**

---

### Étape 2 : Configurer Git local

```bash
cd /home/lvx/ARTCB/lvx

# Configurer identité Git
git config user.name "vgac2025"
git config user.email "votre-email@example.com"  # Remplacez par votre email GitHub

# Configurer SSH pour ce dépôt
git config core.sshCommand "ssh -i ~/.ssh/github_artcb_lvx -F /dev/null"

# Vérifier remote (doit être SSH, pas HTTPS)
git remote -v
# Si HTTPS (https://github.com/...), changer en SSH :
git remote set-url origin git@github.com:vgac2025/lvx.git
```

---

### Étape 3 : Tester la connexion SSH

```bash
ssh -T -i ~/.ssh/github_artcb_lvx git@github.com
```

**Sortie attendue :**
```
Hi vgac2025! You've successfully authenticated, but GitHub does not provide shell access.
```

Si vous voyez ce message, la configuration SSH est **réussie** ✅

---

### Étape 4 : Push sur main

```bash
cd /home/lvx/ARTCB/lvx

# Vérifier statut
git status

# Ajouter tous les fichiers
git add .

# Commit
git commit -m "feat: audit technique complet expert + benchmark performance + clés SSH"

# Push
git push origin main
```

---

## 3. FICHIERS À COMMITTER

**Nouveaux fichiers créés :**
- `rapports/014_audit_complet_agent_suivant.md` (audit initial)
- `rapports/015_audit_technique_complet_expert.md` (audit expert détaillé)
- `scripts/benchmark_performance.py` (benchmark temps réel)
- `logs/benchmark_performance_20260705_001228.log` (résultats benchmark)
- `logs/tests_detailed_20260705_001245.log` (pytest verbose)
- `INSTRUCTIONS_SSH_GITHUB.md` (ce fichier)

**Fichiers modifiés :**
- `.env` (secrets locaux — **NE PAS COMMITTER**)
- `.venv/` (environnement virtuel — **NE PAS COMMITTER**)

---

## 4. VÉRIFICATION AVANT PUSH

```bash
# Vérifier que .env n'est PAS dans le commit
git status | grep .env
# Doit retourner vide (fichier ignoré)

# Vérifier les fichiers à committer
git diff --cached --name-only

# Vérifier .gitignore
cat .gitignore | grep -E "\.env|\.venv"
# Doit contenir .env et .venv
```

---

## 5. DÉPANNAGE

### Erreur : "Permission denied (publickey)"

**Cause :** Clé SSH non ajoutée sur GitHub ou mauvaise configuration

**Solution :**
1. Vérifiez que la clé est bien sur https://github.com/settings/keys
2. Testez : `ssh -T -i ~/.ssh/github_artcb_lvx git@github.com`
3. Vérifiez remote : `git remote -v` (doit être `git@github.com:...`)

---

### Erreur : "fatal: Could not read from remote repository"

**Cause :** Remote HTTPS au lieu de SSH

**Solution :**
```bash
git remote set-url origin git@github.com:vgac2025/lvx.git
```

---

### Erreur : "Host key verification failed"

**Cause :** Première connexion SSH à GitHub

**Solution :**
```bash
ssh-keyscan github.com >> ~/.ssh/known_hosts
```

---

## 6. SÉCURITÉ

⚠️ **IMPORTANT :**
- La clé privée (`~/.ssh/github_artcb_lvx`) ne doit **JAMAIS** être commitée
- La clé privée ne doit **JAMAIS** être partagée
- Seule la clé publique (`.pub`) peut être partagée

✅ **Bonnes pratiques :**
- Clé dédiée au projet ARTCB (pas de réutilisation)
- Passphrase vide OK pour MVP (mais recommandée en production)
- Rotation clés tous les 6 mois en production

---

## 7. APRÈS LE PUSH

Une fois le push réussi, vérifiez sur GitHub :
- https://github.com/vgac2025/lvx/commits/main
- Dernier commit doit contenir les nouveaux rapports

**Tag recommandé :**
```bash
git tag -a v1.0.0-mvp -m "MVP ARTCB Hackathon RAISE 2026 - Audit complet validé"
git push origin v1.0.0-mvp
```

---

**Document créé par :** Bob Advanced Mode  
**Date :** 2026-07-05T00:17 UTC