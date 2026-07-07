# Push captures dashboard — guide corrigé (2026-07-07)

## Ce qui s'est passé

Vous avez exécuté les commandes **depuis `main`**, alors que :

1. La branche `cursor/dashboard-captures-1fce` **existe déjà** (commit `8edfa3b`, 50 PNG).
2. Le dossier `dash model` a **déjà été renommé** sur cette branche → `captures_dashboard_reference/`.
3. Sur `main`, il n'y a rien à committer (`working tree clean`).
4. Le push échoue car SSH utilise le compte **`vgacgit00`** au lieu de **`vgac2025`**.

**Ne recréez pas la branche. Ne renommez pas à nouveau le dossier.**

---

## Étape A — Retrouver vos captures (sur votre machine)

```bash
cd ~/ARTCB/lvx

# Basculer sur la branche qui contient le commit
git checkout cursor/dashboard-captures-1fce

# Vérifier que les 50 captures sont là
ls captures_dashboard_reference/ | wc -l
# Attendu : 50 (ou 48+)

# Vérifier le commit
git log -1 --oneline
# Attendu : 8edfa3b docs: 48 captures dashboard reference
```

Si `ls` renvoie 0 fichier, dites-le — les captures ne sont pas sur cette branche.

---

## Étape B — Corriger SSH (obligatoire avant push)

### B1. Diagnostic

```bash
ssh -T git@github.com
```

| Résultat | Action |
|----------|--------|
| `Hi vgac2025!` | Passez à l'étape C |
| `Hi vgacgit00!` ou `Permission denied` | Continuez B2 |

### B2. Lister vos clés

```bash
ls -la ~/.ssh/
ssh-add -l
```

Repérez la clé ajoutée sur le compte GitHub **vgac2025** (ARTCB3, `id_ed25519`, etc.).

### B3. Forcer la bonne clé

**Remplacez** `/chemin/vers/VOTRE_CLE` par le vrai fichier (ex. `~/.ssh/id_ed25519` ou `~/.ssh/ARTCB3`).

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Éditez ou créez ~/.ssh/config (une seule entrée Host github.com)
nano ~/.ssh/config
```

Contenu minimal :

```
Host github.com
    HostName github.com
    User git
    IdentityFile /chemin/vers/VOTRE_CLE
    IdentitiesOnly yes
```

```bash
chmod 600 ~/.ssh/config
ssh -T git@github.com
# DOIT afficher : Hi vgac2025!
```

### B4. Si ça bloque encore — push en une ligne avec la clé explicite

```bash
GIT_SSH_COMMAND='ssh -i /chemin/vers/VOTRE_CLE -o IdentitiesOnly=yes' \
  git push -u origin cursor/dashboard-captures-1fce
```

---

## Étape C — Push (branche captures uniquement)

```bash
cd ~/ARTCB/lvx
git checkout cursor/dashboard-captures-1fce
git push -u origin cursor/dashboard-captures-1fce
```

**Ne poussez pas `main`.** Seule la branche `cursor/dashboard-captures-1fce` contient les PNG.

---

## Récapitulatif des erreurs vues

| Message | Signification |
|---------|----------------|
| `branch named 'cursor/dashboard-captures-1fce' already exists` | Normal — utilisez `git checkout cursor/dashboard-captures-1fce` |
| `cannot stat 'dash model'` | Déjà renommé sur la branche captures |
| `pathspec 'captures_dashboard_reference/' did not match` | Vous étiez sur `main`, pas sur la branche captures |
| `denied to vgacgit00` | Mauvaise clé SSH — étape B |

---

## Après push réussi

Écrivez **« captures envoyées »** — l'agent Cloud fera :

```bash
git fetch origin
git checkout cursor/dashboard-captures-1fce
# analyse des 50 PNG → CDC v1.2
```
