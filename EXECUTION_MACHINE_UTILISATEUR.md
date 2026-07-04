# Exécution sur VOTRE machine (pas le Cloud Agent)

**Horodatage :** 2026-07-04T23:42:00Z

---

## Limite importante (honnêteté PROTOCOLE)

L’**agent Cursor Cloud** tourne sur une **VM distante** (`/workspace`, hostname `cursor`).
Il **ne peut pas** ouvrir un terminal sur **votre PC** (Windows, Mac, Linux perso).

Les rapports 009–011 ont été exécutés sur **cette VM cloud**, pas sur votre ordinateur.
Ce n’est **pas** « votre local » — c’est le sandbox de l’agent.

**Seul vous** pouvez prouver une exécution sur **votre** machine en lançant les commandes ci-dessous **dans votre terminal**.

---

## Prérequis (une fois)

### Linux / macOS

```bash
# Debian/Ubuntu
sudo apt update
sudo apt install -y python3 python3-pip python3-venv build-essential libssl-dev curl git

git clone https://github.com/vgac2025/lvx.git
cd lvx
cp ENV_A_REMPLIR_ARTCB .env   # éditez .env — collez BOB/GRADIUM si besoin
bash scripts/setup_machine_locale.sh
```

### Windows (PowerShell)

```powershell
git clone https://github.com/vgac2025/lvx.git
cd lvx
# Installer Python 3.11+ depuis python.org, puis :
python -m pip install -e ".[dev]"
# Build C : installer Visual Studio Build Tools ou WSL + apt ci-dessus
```

---

## Exécution réelle (votre terminal, pas de navigateur)

```bash
cd lvx          # ou le chemin où vous avez cloné
git pull origin main
bash scripts/run_real_local.sh
```

Le script affiche :
- **hostname** et **utilisateur** de VOTRE machine
- **Avertissement** si détecté environnement Cloud Agent
- Résultat des 9 étapes dans le terminal
- Fichiers : `logs/demo_live_latest.txt`, `logs/machine_fingerprint.txt`

---

## Vérifier que c’est bien VOTRE machine

Ouvrez `logs/machine_fingerprint.txt` après exécution :

```
hostname=votre-nom-pc        ← doit être VOTRE PC, pas "cursor"
user=votre_login
execution_env=USER_MACHINE   ← doit être USER_MACHINE, pas CLOUD_AGENT
```

Si `execution_env=CLOUD_AGENT` → c’est encore l’agent cloud, pas chez vous.

---

## Copier l’erreur si ça échoue

Collez **toute** la sortie terminal (depuis `bash scripts/run_real_local.sh`) dans le chat.
On corrige sur preuve réelle de **votre** environnement.
