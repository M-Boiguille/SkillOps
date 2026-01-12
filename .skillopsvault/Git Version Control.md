# Git Version Control

#git #versioncontrol #collaboration #devops

## Concepts de base

**Git** est un système de contrôle de version distribué qui permet de suivre les modifications du code source.

## Configuration initiale

```bash
git config --global user.name "Votre Nom"
git config --global user.email "email@example.com"
git config --global init.defaultBranch main
git config --global core.editor "vim"

# Vérifier la config
git config --list
```

## Commandes essentielles

### Initialiser un repo
```bash
git init
git clone https://github.com/user/repo.git
```

### Workflow de base
```bash
# Vérifier le status
git status

# Ajouter des fichiers au staging
git add file.txt
git add .
git add -p  # Ajout interactif

# Commiter
git commit -m "Message de commit"
git commit -am "Add et commit en une fois"

# Historique
git log
git log --oneline
git log --graph --all
git show <commit-hash>
```

### Branches

```bash
# Créer et changer de branche
git branch feature-login
git checkout feature-login
# OU
git checkout -b feature-login

# Lister les branches
git branch
git branch -a  # Inclure remote

# Supprimer une branche
git branch -d feature-login
git branch -D feature-login  # Force

# Renommer
git branch -m old-name new-name
```

### Merge et Rebase

```bash
# Merge
git checkout main
git merge feature-login

# Rebase
git checkout feature-login
git rebase main

# Rebase interactif (modifier historique)
git rebase -i HEAD~3
```

### Remote

```bash
# Ajouter un remote
git remote add origin https://github.com/user/repo.git

# Lister les remotes
git remote -v

# Push
git push origin main
git push -u origin feature-login

# Pull
git pull origin main
git pull --rebase origin main

# Fetch
git fetch origin
git fetch --all
```

### Undoing Changes

```bash
# Annuler modifications non-staged
git restore file.txt
git checkout -- file.txt

# Unstage
git restore --staged file.txt
git reset HEAD file.txt

# Annuler dernier commit (garder les changements)
git reset --soft HEAD~1

# Annuler dernier commit (supprimer les changements)
git reset --hard HEAD~1

# Revert (créer un nouveau commit qui annule)
git revert <commit-hash>
```

### Stash

```bash
# Sauvegarder le travail en cours
git stash
git stash save "Message descriptif"

# Lister les stash
git stash list

# Appliquer un stash
git stash apply
git stash apply stash@{0}

# Appliquer et supprimer
git stash pop

# Supprimer un stash
git stash drop stash@{0}
git stash clear  # Tout supprimer
```

### Tags

```bash
# Créer un tag
git tag v1.0.0
git tag -a v1.0.0 -m "Version 1.0.0"

# Lister les tags
git tag

# Push tags
git push origin v1.0.0
git push origin --tags

# Supprimer un tag
git tag -d v1.0.0
git push origin --delete v1.0.0
```

## Workflows

### Feature Branch Workflow
```bash
# 1. Créer une branche depuis main
git checkout main
git pull origin main
git checkout -b feature/nouvelle-fonctionnalite

# 2. Travailler et commiter
git add .
git commit -m "Add nouvelle fonctionnalité"

# 3. Push et créer PR
git push -u origin feature/nouvelle-fonctionnalite

# 4. Après review, merge dans main
git checkout main
git pull origin main
git merge feature/nouvelle-fonctionnalite

# 5. Nettoyer
git branch -d feature/nouvelle-fonctionnalite
git push origin --delete feature/nouvelle-fonctionnalite
```

### Gitflow

Branches principales:
- **main**: Code en production
- **develop**: Branche de développement

Branches support:
- **feature/**: Nouvelles fonctionnalités
- **release/**: Préparation release
- **hotfix/**: Corrections urgentes

## Résolution de conflits

```bash
# Lors d'un merge avec conflits
git merge feature-branch
# CONFLICT: fichier.txt

# 1. Éditer le fichier pour résoudre
<<<<<<< HEAD
Code de la branche actuelle
=======
Code de la branche à merger
>>>>>>> feature-branch

# 2. Marquer comme résolu
git add fichier.txt

# 3. Finaliser le merge
git commit
```

## .gitignore

```gitignore
# Node
node_modules/
npm-debug.log

# Python
__pycache__/
*.py[cod]
venv/
.env

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Build
dist/
build/
*.log
```

## Best Practices

- ✅ Commits atomiques et fréquents
- ✅ Messages de commit descriptifs
- ✅ Utiliser des branches feature
- ✅ Pull avant push
- ✅ Ne jamais rebase des branches publiques
- ✅ Utiliser .gitignore dès le début
- ✅ Faire des PR avec code review
- ✅ Protéger la branche main

## Commandes avancées

```bash
# Cherry-pick (appliquer un commit spécifique)
git cherry-pick <commit-hash>

# Bisect (trouver le commit qui a introduit un bug)
git bisect start
git bisect bad
git bisect good <commit-hash>

# Reflog (historique complet)
git reflog

# Blame (voir qui a modifié chaque ligne)
git blame file.txt

# Submodules
git submodule add https://github.com/user/repo.git
git submodule update --init --recursive
```

## Liens

- [[GitHub Actions]]
- [[GitLab CI]]
- [[Git Hooks]]
- [[Code Review Best Practices]]

## Notes perso

Date: 2026-01-12
- Maîtrise du workflow feature branch
- Utilisation de rebase interactif pour nettoyer l'historique
- TODO: Apprendre les hooks pre-commit
