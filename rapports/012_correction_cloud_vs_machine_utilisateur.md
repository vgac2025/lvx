# Rapport 012 — Correction : Cloud Agent ≠ machine utilisateur

**Horodatage :** 2026-07-04T23:42:00Z  
**Retour utilisateur :** « Tu es sur la machine [cloud] — exécute en local chez moi, pas sur cloud »

---

## 1. Avant (erreur rapport 011)

**Fichier :** `rapports/011_execution_reelle_locale_20260704.md` §4

```
Machine : /workspace — Linux cursor 6.12.58+ x86_64
Sur votre machine : git pull … bash scripts/run_real_local.sh
```

**Problème :** le rapport mélangeait exécution **VM Cloud Agent** (`hostname=cursor`, `/workspace`) et instructions « votre machine ». L’utilisateur n’a **jamais vu** l’exécution sur **son PC**.

---

## 2. Après (correction honnête)

| Environnement | Qui exécute | Preuve |
|---------------|-------------|--------|
| Cloud Agent Cursor | Agent IA | `hostname=cursor`, `execution_env=CLOUD_AGENT` |
| Machine utilisateur | **Vous** (humain) | `execution_env=USER_MACHINE`, hostname ≠ cursor |

**Limite technique :** l’agent Cloud **ne peut pas** lancer de commandes sur le disque de l’utilisateur. Seul un terminal **ouvert par vous** sur votre clone git peut produire une preuve « local utilisateur ».

**Fichiers ajoutés :**
- `EXECUTION_MACHINE_UTILISATEUR.md` — guide pour **votre PC**
- `scripts/setup_machine_locale.sh` — install deps + build C
- `scripts/run_real_local.sh` — écrit `logs/machine_fingerprint.txt` avec `execution_env`

---

## 3. Ce que VOUS devez faire (une fois)

Dans **votre** terminal (pas le chat) :

```bash
git clone https://github.com/vgac2025/lvx.git
cd lvx
bash scripts/setup_machine_locale.sh
bash scripts/run_real_local.sh
```

Puis ouvrir `logs/machine_fingerprint.txt` — doit contenir :

```
execution_env=USER_MACHINE
hostname=<votre-pc>
```

Coller la sortie terminal ici si erreur.

---

## 4. Checklist PROTOCOLE

| Règle | Statut |
|-------|--------|
| Ne pas mentir sur véracité | ✅ cloud ≠ local utilisateur clarifié |
| Notifier ce qu’on ne sait pas / ne peut pas | ✅ agent ne contrôle pas le PC utilisateur |
| Rapport après correction | ✅ ce fichier |
| Avant / après | ✅ §1–2 |

---

## 5. Avancement MVP code : **~92 %** (inchangé)

L’exécution sur **votre** machine reste **à faire par vous** — l’agent fournit scripts et docs, pas accès à votre disque.
