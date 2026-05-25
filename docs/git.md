# Guide Complet des Commandes Git
<div align="right">

[← Retour à la documentation principale](../README.md)

</div>

## Configuration Initiale

```bash
# Configuration utilisateur
git config --global user.name "Votre Nom"
git config --global user.email "votre@email.com"
git config --global init.defaultBranch main

# Vérifier la configuration
git config --list
git config user.name

# Éditeur par défaut
git config --global core.editor "code --wait"  # VS Code
```

## Démarrer un Projet

```bash
# Cloner un dépôt existant
git clone <url-depot>
git clone <url-depot> nom-dossier

# Initialiser un nouveau dépôt
git init
git init nom-projet
```

## Inspection & Statut

```bash
# Vérifier l'état
git status
git status -s  # Format court

# Voir l'historique
git log
git log --oneline
git log --graph --all --decorate
git log -p  # Avec les modifications
git log --since="2024-01-01"

# Voir les modifications
git diff
git diff --staged
git diff HEAD~1 HEAD
```

## Gestion des Fichiers

```bash
# Ajouter des fichiers
git add fichier.txt
git add .                     # Tous les fichiers
git add *.js                 # Par pattern
git add -A                   # Tous les changements

# Retirer des fichiers
git reset fichier.txt
git rm fichier.txt           # Supprimer du dépôt
git rm --cached fichier.txt  # Garder en local

# Déplacer/renommer
git mv ancien-nom nouveau-nom
```

## Commit & Historique

```bash
# Créer un commit
git commit -m "Message clair et descriptif"
git commit -am "Message"     # Add + commit

# Modifier le dernier commit
git commit --amend
git commit --amend -m "Nouveau message"

# Voir un commit spécifique
git show <commit-hash>
git show HEAD
```

## Gestion des Branches

```bash
# Lister les branches
git branch
git branch -a               # Toutes les branches
git branch -v               # Avec dernier commit

# Créer et changer de branche
git branch nouvelle-branche
git checkout nouvelle-branche
git checkout -b nouvelle-branche  # Créer + changer

# Supprimer des branches
git branch -d branche       # Suppression sûre
git branch -D branche       # Suppression forcée

# Suivi des branches distantes
git branch -u origin/branche
```

## Synchronisation avec le Remote

```bash
# Voir les remotes
git remote -v
git remote show origin

# Ajouter un remote
git remote add origin <url>

# Télécharger les changements
git fetch
git fetch origin
git fetch --all

# Récupérer et fusionner
git pull
git pull origin main
git pull --rebase origin main

# Envoyer les changements
git push
git push origin branche
git push -u origin branche  # Premier push

# Supprimer branche distante
git push origin --delete branche
```

## Fusion & Conflits

```bash
# Fusionner une branche
git merge branche
git merge --no-ff branche   # Toujours créer un commit

# Annuler une fusion
git merge --abort

# Rebase interactif
git rebase -i HEAD~3
git rebase main

# Résoudre les conflits
# Éditer les fichiers → git add → git commit
```

## Annulations & Corrections

```bash
# Annuler modifications locales
git restore fichier.txt
git restore .

# Annuler l'indexation
git reset fichier.txt
git reset

# Annuler le dernier commit (garder changes)
git reset --soft HEAD~1

# Annuler le dernier commit (supprimer changes)
git reset --hard HEAD~1

# Revenir à un commit spécifique
git reset --hard <commit-hash>

# Annuler un commit publié
git revert <commit-hash>
```

## Tags & Versions

```bash
# Gérer les tags
git tag
git tag v1.0.0
git tag -a v1.0.0 -m "Version 1.0.0"

# Pusher les tags
git push --tags
git push origin v1.0.0

# Supprimer un tag
git tag -d v1.0.0
git push origin --delete v1.0.0
```

## Nettoyage & Maintenance

```bash
# Nettoyer les fichiers non trackés
git clean -n  # Simulation
git clean -f  # Vraie suppression
git clean -fd # + dossiers

# Optimiser le dépôt
git gc
git prune

# Vérifier l'intégrité
git fsck
```

## Workflow Typique

```bash
# Début de travail
git checkout main
git pull origin main
git checkout -b ma-feature

# Pendant le développement
git add .
git commit -m "Description des changements"
git push origin ma-feature

# Finalisation
git checkout main
git pull origin main
git merge ma-feature
git push origin main
git branch -d ma-feature
```

## Astuces Utiles

```bash
# Alias pratiques
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status

# Ignorer les permissions de fichiers
git config core.fileMode false

# Aide
git help <commande>
git <commande> --help
```

## Bonnes Pratiques

- **Messages de commit clairs** et descriptifs
- **Commits atomiques** (une fonctionnalité par commit)
- **Pull avant push**
- **Branches feature** pour les nouvelles fonctionnalités
- **Review du code** avant merge
-  **Ne pas commit les fichiers sensibles** (mots de passe, clés)
-  **Éviter --force** sur les branches partagées

---