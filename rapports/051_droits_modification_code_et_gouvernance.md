# Rapport 051 — Droits de modification du code, règles utilisateurs, et gouvernance ARTCB

**Horodatage :** 2026-07-08T21:30:00Z  
**Auteur :** Agent Cursor (audit lecture seule + analyse)  
**Branche lue (VM agent) :** `cursor/cahier-des-charges-mvp-1fce` — commit `dcb87c2`  
**Branche implémentation (votre PC / production dev) :** `cursor/dashboard-dev-1fce` — commit `81b93ee`  
**PROTOCOLE :** nouveau rapport, rien d’ancien écrasé, sources citées ci-dessous  
**Public visé :** personnes **sans** expertise blockchain ni juridique

---

## 0. Réponse directe à votre question principale

### Question : « Est-ce qu’on a le droit de modifier et mettre à jour le code, oui ou non ? »

**Réponse courte : OUI.**

**Vous** (les créateurs du projet, propriétaires du dépôt GitHub `vgac2025/lvx`) **avez le droit de modifier le code quand vous voulez**, que le projet soit à 50 %, à 100 %, ou déjà publié en ligne.

Personne sur la blockchain ne vous « interdit » de modifier le code source.  
Personne n’a besoin de voter pour que **vous** changiez **votre** logiciel sur GitHub.

---

### Question : « Est-ce possible seulement avec l’autorisation de la majorité des utilisateurs de la blockchain ? »

**Réponse courte : NON — pas aujourd’hui, et ce n’est pas prévu dans les documents actuels.**

Il n’existe **aucun mécanisme** dans ARTCB où :
- les utilisateurs votent à la majorité pour autoriser une mise à jour du code ;
- la blockchain « bloque » une nouvelle version du logiciel ;
- les mineurs ou les membres de groupes décident des changements du dépôt GitHub.

**Pourquoi ?** Parce que le **code** (fichiers sur GitHub) et la **blockchain** (journal des données déjà enregistrées) sont **deux choses différentes**. Nous expliquons cela en détail en section 2.

---

## 1. Vocabulaire simple (à lire avant le reste)

| Mot | Signification simple | Exemple concret |
|-----|---------------------|-----------------|
| **Code source** | Les fichiers du programme (Python, React, C) | `src/api/routes.py`, `frontend/src/pages/Groups.tsx` |
| **Dépôt GitHub** | L’endroit où le code est stocké et versionné | `github.com/vgac2025/lvx` |
| **Blockchain** | Un carnet numérique **immuable** : une fois une donnée écrite et signée, elle reste dans l’historique | Fichier `data/chain/blocks.jsonl` |
| **Wallet** | Une « identité » avec une adresse (`artcb1…`) et une clé secrète locale | Comme un compte, mais sans serveur central |
| **Minage ARTCB** | **Pas** du minage Bitcoin. C’est : « prouver qu’on a appris / validé quelque chose » (Proof-of-Learning) | Un bloc n’est accepté que si le score PoL ≥ 0,6 |
| **Licence** | Texte légal qui dit ce que **les autres personnes** ont le droit de faire avec **votre** code | MIT, Apache, GPL… |
| **Gouvernance** | Qui décide des **règles du réseau** | Aujourd’hui : vous / l’équipe, pas un vote utilisateurs |

---

## 2. Deux mondes séparés : le CODE et la BLOCKCHAIN

C’est le point le plus important pour comprendre vos droits.

### 2.1 Modifier le CODE (logiciel)

- C’est modifier les fichiers sur votre ordinateur et les pousser sur GitHub.
- **Qui décide ?** Vous et votre équipe (propriétaires du dépôt).
- **Besoin d’un vote des utilisateurs ?** **Non.**
- **Effet :** la prochaine version du programme se comporte différemment (nouveaux boutons, nouvelles règles, corrections de bugs).

**Analogie :** Vous êtes constructeur d’une voiture. Vous pouvez changer le moteur demain. Les conducteurs n’ont pas à voter pour que vous modifiiez l’usine.

### 2.2 Modifier la BLOCKCHAIN (données déjà enregistrées)

- C’est le journal des blocs déjà signés et chaînés par hash.
- **Règle fondamentale :** on **n’efface pas** un bloc validé ; on **ajoute** de nouveaux blocs (append-only).
- **Qui décide d’écrire un nouveau bloc ?** L’utilisateur qui mémorise, s’il respecte les règles (PoL, membership groupe, etc.).
- **Besoin d’un vote majoritaire pour écrire un bloc ?** **Non** — chaque utilisateur écrit ses propres blocs s’il respecte les règles techniques.

**Analogie :** Le carnet de comptes d’une association : on n’efface pas une page déjà signée ; on ajoute une nouvelle page.

### 2.3 Ce qui N’EXISTE PAS encore

| Mécanisme | Existe ? | Conséquence |
|-----------|----------|-------------|
| Vote utilisateurs pour mise à jour du code | ❌ Non | Vous gardez la main sur le dépôt |
| Gouvernance on-chain (DAO) | ❌ Non | Pas de « démocratie blockchain » sur le code |
| Réseau P2P décentralisé à 100 % | ❌ Non (MVP single-node) | Un seul nœud local contrôle la chaîne aujourd’hui |
| Fichier `LICENSE` officiel | ❌ Non | Droits des **tiers** flous (voir section 6) |

**Note PROTOCOLE :** le texte dit « blockchain décentralisée à 100 % » — c’est un **objectif**, pas la réalité technique actuelle (CDC §19 : « Blockchain MVP single-node »).

---

## 3. Règles des utilisateurs sur la blockchain (état actuel)

*Sources : `CAHIER_DES_CHARGES_ARTCB` §3.2.4–3.2.5, §10 ; branche `dashboard-dev` : `tokenomics.py`, `pol/scorer.py`, `groups/manager.py`, `GROUPES_RESEAUX_ARTCB.md`, `TOKENOMICS_ARTCB`, `RESEAU_DEVNET_ARTCB`*

### 3.1 Il n’y a pas de « type compte » classique

Pas de login email/mot de passe. **Votre wallet = votre identité.**

Toute personne avec un wallet peut, selon les règles :
- encoder du texte en graphe ;
- tenter de mémoriser sur la chaîne ;
- rejoindre un groupe (via demande signée).

### 3.2 Types d’acteurs sur le réseau ARTCB

| Type | Qui c’est | Ce qu’il peut faire | Ce qu’il ne peut pas faire |
|------|-----------|---------------------|----------------------------|
| **Utilisateur simple** | Quelqu’un avec un wallet | Mémoriser en privé, lire ses données, signer | Modifier le code du projet ; effacer un bloc passé |
| **Contributeur PoL** (« mineur d’apprentissage ») | Celui dont le travail améliore le score PoL | Recevoir une part du reward si son bloc est accepté | Gagner sans PoL suffisant ; tricher sans risque (anti-Sybil/slashing sur branche dev) |
| **Membre de groupe** | Wallet accepté dans un groupe | Voir/mémoriser en `visibility=group` | Accéder aux données d’un autre groupe |
| **Admin de groupe** | Nommé par le fondateur | Approuver des adhésions, retirer des membres (sauf fondateur) | Promouvoir un admin ; dissoudre le groupe ; toucher au fondateur |
| **Fondateur de groupe** | Créateur du groupe | Tout ce que l’admin fait + promouvoir admins + dissoudre | Être retiré par un admin ; perdre son rôle sans dissoudre |

### 3.3 Règles pour « miner » (mémoriser un bloc)

Ce ne sont **pas** les règles du minage Bitcoin.

| Règle | Valeur actuelle | Explication simple |
|-------|-----------------|-------------------|
| Score PoL minimum | **≥ 0,6** | Le système mesure si l’encodage est « utile » (compression, validation, retrieval) |
| Bloc refusé si | PoL < 0,6 | Le bloc n’est pas ajouté ; pas de reward |
| Reward par bloc | **1 ARTCB** au départ | Récompense interne du projet (pas du Bitcoin) |
| Halving | Tous les 210 000 blocs | La récompense diminue avec le temps (comme Bitcoin, mais pour PoL) |
| Répartition | **Collective** | Plusieurs contributeurs peuvent partager le reward d’un même bloc |
| Supply max | 21 000 000 ARTCB | Limite totale d’unités |

### 3.4 Trois « réseaux » de visibilité des données

| Réseau | Qui voit les données ? | Règle d’écriture |
|--------|------------------------|------------------|
| **Privé** | Vous seul | Libre, avec votre wallet |
| **Groupe** | Membres du groupe seulement | Il faut être membre + `actor_address` valide |
| **Public** | Tout le monde (en lecture) | Prévu ; filtre chain en place sur branche dev |

### 3.5 Règles de sécurité pour rejoindre un groupe (Solution 2)

| Règle | Détail |
|-------|--------|
| Le fondateur partage | Un **code** de 8 caractères (`join_code`) |
| Le fondateur ne reçoit jamais | La **clé privée** de l’invité |
| L’invité | Signe une demande avec son wallet |
| L’admin approuve ou refuse | L’adresse n’apparaît qu’après la demande signée |
| Invite directe par adresse | **Bloquée** sauf mode debug (`ARTCB_DEBUG_DIRECT_MEMBER=true`) |

---

## 4. Qui a le droit de modifier QUOI ? (tableau clair)

| Objet | Qui peut le modifier ? | Vote majorité nécessaire ? | Remarque |
|-------|------------------------|----------------------------|----------|
| **Code sur GitHub** | Propriétaires du dépôt (vous) | **Non** | Toujours, même repo public |
| **Règles PoL (seuil 0,6, etc.)** | Qui déploie le serveur / met à jour le code | **Non** | Changement = nouvelle version logicielle |
| **Données déjà sur la chaîne** | Personne (immuable) | **Non** | On ajoute, on n’efface pas |
| **Nouveaux blocs** | Utilisateur respectant les règles | **Non** | Pas un vote collectif |
| **Membres d’un groupe** | Fondateur / admin du groupe | **Non** | Règles internes au groupe |
| **Rôle fondateur d’un groupe** | Personne (immuable) | **Non** | Invariant F1–F7 |
| **Licence open source** | Vous (en ajoutant un fichier LICENSE) | **Non** | Décision fondateur projet |
| **Règles du réseau mondial** | N/A aujourd’hui | N/A | Pas de réseau mondial décentralisé encore |

---

## 5. État actuel vs 100 % opérationnel — est-ce que vos droits changent ?

### 5.1 Aujourd’hui (dépôt public, pas de licence formelle)

| Situation | Votre droit de modifier le code |
|-----------|-------------------------------|
| Repo public sur GitHub | **OUI**, vous êtes propriétaire/auteur |
| Pas de fichier LICENSE | **Vous** gardez tous les droits d’auteur par défaut (droit français / international) |
| Hackathon exige repo public | Ça oblige la **visibilité**, pas à abandonner vos droits de modification |
| Utilisateurs qui ont cloné le repo | Ils **ne devraient pas** modifier et republier sans licence claire |

**En clair :** publier ≠ perdre le contrôle. Publier sans LICENSE = les **autres** ne savent pas ce qu’ils ont le droit de faire ; **vous**, vous gardez la main.

### 5.2 À 100 % opérationnel (futur)

| Si vous faites… | Effet sur VOS droits de modifier |
|-----------------|-----------------------------------|
| Ajouter une licence MIT/Apache | **Vous pouvez toujours modifier votre code.** La licence autorise surtout **les autres** à utiliser/copier sous conditions |
| Ajouter une licence GPL | **Vous pouvez toujours modifier.** Les autres doivent partager leurs modifications si ils redistribuent |
| Créer un réseau P2P décentralisé | Les **nœuds** pourraient refuser d’exécuter votre nouvelle version — mais c’est technique, pas un vote blockchain intégré aujourd’hui |
| Mettre une gouvernance DAO (non prévu) | Là seulement, certaines règles pourraient exiger un vote — **pas dans le projet actuel** |

---

## 6. Qu’avez-vous « libéré » comme droits ? Qu’avez-vous gardé ?

### 6.1 Ce que vous avez « libéré » (donné aux autres) — très peu, formellement

| Élément | Libéré ? | Preuve |
|---------|----------|--------|
| Voir le code (lecture) | ✅ Oui (repo public) | GitHub public |
| Copier / modifier / revendre le code | ⚠️ **Flou** | Pas de fichier LICENSE |
| Utiliser la marque « ARTCB » | ❌ Non documenté | Pas de politique de marque |
| Modifier la blockchain d’autrui | ❌ Non | Données signées par chaque wallet |
| Décider des mises à jour du logiciel officiel | ❌ Non | Pas de gouvernance communautaire |
| Recevoir des ARTCB (rewards) | ✅ Oui si PoL valide | TOKENOMICS / code |

**Document CDC NF-09 :** « Open source, repo public » — c’est une **intention**, pas un contrat juridique complet sans fichier LICENSE.

### 6.2 Ce que vous avez gardé (et garderez tant que vous ne signez pas autre chose)

| Droit | Explication simple |
|-------|-------------------|
| Modifier le code quand vous voulez | C’est votre logiciel |
| Choisir la licence plus tard | MIT, Apache, GPL, etc. |
| Déployer la version que vous voulez | Sur votre serveur / votre nœud |
| Refuser des contributions | Personne n’a droit automatique au merge sur `main` |
| Archiver / dissoudre un groupe | Règle fondateur (F7) |
| Contrôler vos données privées | Wallet local, visibility private |

### 6.3 Ce que les UTILISATEURS ont comme droits (pas les développeurs)

| Droit utilisateur | Détail |
|-------------------|--------|
| Posséder leur wallet et clé privée | Jamais demandée au fondateur de groupe |
| Mémoriser en privé | Sans permission d’un tiers |
| Demander à rejoindre un groupe | Via signature |
| Refuser une adhésion | Admin/fondateur |
| Quitter / être retiré (sauf fondateur) | Selon rôle |
| Vérifier l’intégrité des blocs | Hash + signatures |

Les utilisateurs **n’ont pas** le droit de :
- changer le code officiel sur votre GitHub ;
- effacer l’historique blockchain ;
- retirer le fondateur d’un groupe ;
- voter sur vos mises à jour logicielles (mécanisme absent).

---

## 7. Suggestions possibles (ce que vous POUVEZ encore implémenter)

### 7.1 Recommandé (clair pour tout le monde)

| Action | Pourquoi | Difficulté |
|--------|----------|------------|
| Ajouter un fichier `LICENSE` (MIT ou Apache-2.0) | Les autres sauront ce qu’ils peuvent faire ; vous gardez le contrôle | Facile |
| Documenter « Qui décide des mises à jour » dans un `GOUVERNANCE_ARTCB.md` | Évite la confusion vote vs propriétaire | Facile |
| Répondre aux QUESTIONS_OUVERTES Q-001 à Q-008 | Débloque décisions officielles | Moyen |

### 7.2 Optionnel (gouvernance avancée — pas obligatoire)

| Action | Effet | Vote majorité ? |
|--------|-------|-----------------|
| **DAO / gouvernance on-chain** | Les détenteurs de tokens votent sur certaines règles | Oui, si vous le concevez ainsi |
| **BIP / proposition d’amélioration** | Processus public type Bitcoin pour changer le protocole | Communauté + devs |
| **Multi-sig fondateurs** | Plusieurs personnes doivent signer pour déployer | Pas un vote utilisateurs, un vote interne équipe |
| **Hard fork** | Deux versions du réseau coexistent | Les nœuds « choisissent » en migrant ou non |

**Aujourd’hui, rien de cela n’est implémenté.** Si vous ne l’ajoutez pas, **vous restez seuls décideurs du code.**

### 7.3 Ce que vous ne devriez PAS promettre sans l’implémenter

- « Les utilisateurs votent les mises à jour » — **faux aujourd’hui**
- « Blockchain 100 % décentralisée » en production — **objectif**, pas fait (single-node)
- « Open source complet » sans LICENSE — **incomplet juridiquement**

---

## 8. Règles PROTOCOLE et AUTO_PROMPT (impact sur vos droits)

*Sources : `PROTOCOLE_ARTCB`, `AUTO_PROMPT_ARTCB`*

Ces fichiers régissent **comment l’équipe de développement travaille**, pas les droits des utilisateurs finaux.

| Règle | Signification pour vous |
|-------|-------------------------|
| Pas de mock / résultats réels | Qualité du code, pas un droit utilisateur |
| Mode DEBUG tant que vous ne dites pas stop | Vous contrôlez quand passer en production |
| Rapports dans `rapports/` sans écraser | Traçabilité interne |
| Blockchain décentralisée 100 % | Objectif technique — pas accompli entièrement |
| Pas de dev sans votre ordre | **Vous** gardez la décision de lancer le travail |
| Pas de merge `main` sans votre accord | **Vous** gardez la décision de publication officielle |

**Conclusion :** PROTOCOLE renforce que **vous** gardez la main sur le développement et les releases.

---

## 9. Questions que vous aviez oublié de préciser (à trancher officiellement)

| ID | Question | Pourquoi c’est important |
|----|----------|--------------------------|
| Q-LIC-01 | Quelle licence exacte ? (MIT, Apache, GPL, autre) | Définit ce que les **autres** peuvent faire avec votre code |
| Q-LIC-02 | Qui détient le copyright ? (personne, société) | En cas de litige ou partenariat |
| Q-GOV-01 | Qui peut merger sur `main` ? | Évite qu’un contributeur prenne le contrôle |
| Q-GOV-02 | Faut-il un vote utilisateurs un jour ? | Si oui, il faut le **concevoir** — ce n’est pas automatique |
| Q-GOV-03 | Quand désactiver DEBUG et `ARTCB_DEBUG_DIRECT_MEMBER` ? | Sécurité production |
| Q-GOV-04 | Qui contrôle le déploiement du nœud officiel ? | En single-node, c’est **vous** |
| Q-GOV-05 | Allocation founders ARTCB — qui reçoit quoi ? | Économie du token |
| Q-GOV-06 | P2P : à partir de quand les nœuds indépendants ? | Vraie décentralisation |
| Q-001 (existant) | Merger `dashboard-dev` → `main` ? | Version « officielle » publique |
| Q-005 (existant) | Taille et rôles de l’équipe ? | Responsabilités légales |

---

## 10. Branche connectée — récapitulatif

| Environnement | Branche | Contenu | Commit |
|---------------|---------|---------|--------|
| **VM agent (maintenant)** | `cursor/cahier-des-charges-mvp-1fce` | Documentation seulement, pas de code applicatif | `dcb87c2` |
| **Votre PC / implémentation** | `cursor/dashboard-dev-1fce` | Code complet, tests, dashboard, groupes | `81b93ee` |
| **`main` (GitHub)** | En retard par rapport au dev | Décision merge non actée (Q-001) | — |

**Ce rapport a été rédigé en lisant les deux contextes** : docs sur la branche agent, règles implémentées sur `dashboard-dev` via `git show`.

---

## 11. Sources consultées (traçabilité)

| Fichier | Branche / emplacement | Utilisé pour |
|---------|----------------------|--------------|
| `PROTOCOLE_ARTCB` | cahier-des-charges-mvp | Règles dev, objectif décentralisation |
| `AUTO_PROMPT_ARTCB` | cahier-des-charges-mvp | Gouvernance dev, merge main |
| `CAHIER_DES_CHARGES_ARTCB` §3.2.4–5, §10, NF-09 | cahier-des-charges-mvp | PoL, blockchain, licence intention |
| `QUESTIONS_OUVERTES_ARTCB` | cahier-des-charges-mvp | Q-001 merge, décisions en attente |
| `README.md` | cahier-des-charges-mvp | « Open source » sans LICENSE |
| `IDÉE_ARTCB` § mémoire privée | cahier-des-charges-mvp | Contrôle utilisateur sur ses données |
| `TOKENOMICS_ARTCB` | dashboard-dev (git show) | Rewards, mineurs PoL, supply |
| `RESEAU_DEVNET_ARTCB` | dashboard-dev (git show) | Pas Bitcoin testnet, artcb-devnet |
| `GROUPES_RESEAUX_ARTCB.md` | dashboard-dev (git show) | Rôles founder/admin/contributor/viewer |
| `src/artcb/groups/manager.py` | dashboard-dev (git show) | ACL groupes implémentée |
| `src/artcb/pol/scorer.py` | dashboard-dev (git show) | Seuil PoL 0,6 |
| `src/artcb/tokenomics.py` | dashboard-dev (git show) | 1 ARTCB, halving |
| `rapports/049_join_request_solution2.md` | dashboard-dev | Solution 2 adhésion |

**Fichier LICENSE :** recherché — **introuvable** sur les deux branches.

---

## 12. Conclusion en une phrase

**Vous pouvez toujours modifier et mettre à jour votre code ; personne sur la blockchain n’a aujourd’hui à voter pour vous l’autoriser — par contre, vous n’avez pas encore formalisé par une licence ce que les autres ont le droit de faire avec ce code publié, et la blockchain elle-même ne gouverne pas le dépôt GitHub.**

---

**Fin du rapport 051** — aucun autre fichier du projet n’a été modifié.
