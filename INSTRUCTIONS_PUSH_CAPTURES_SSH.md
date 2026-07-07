# Push captures dashboard — correction SSH

**Problème :** `Permission denied to vgacgit00`  
**Cause :** GitHub utilise la mauvaise clé SSH (compte `vgacgit00` au lieu de `vgac2025`).

## Commandes (sur votre machine)

```bash
cd ~/ARTCB/lvx

# 1. Vérifier quelle clé est utilisée
ssh -T git@github.com
# Doit afficher : Hi vgac2025!  (PAS vgacgit00)

# 2. Forcer la bonne clé (ARTCB3 ou celle ajoutée sur vgac2025)
mkdir -p ~/.ssh
cat >> ~/.ssh/config << 'EOF'
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
EOF
chmod 600 ~/.ssh/config

# Si votre clé ARTCB3 est ailleurs, remplacez le chemin IdentityFile

# 3. Retester
ssh -T git@github.com

# 4. Push la branche captures (déjà commitée localement)
git push -u origin cursor/dashboard-captures-1fce
```

**Commit local prêt :** `8edfa3b` — 50 fichiers dans `captures_dashboard_reference/`
