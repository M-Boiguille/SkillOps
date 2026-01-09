# Git Best Practices

## Commits

### ✅ Do
- **Commits atomiques** : 1 commit = 1 changement logique
- **Messages descriptifs** : Conventional Commits (`feat:`, `fix:`, `docs:`)
- **Commiter souvent** : 2-3 commits/jour minimum (intégration continue)
- **Relire avant commit** : `git diff --staged`

### ❌ Don't
- Commits "WIP" sans contexte
- Mélanger plusieurs changements non liés
- Messages vagues : "fix bug", "update code"
- Commiter des secrets ou credentials

## Branches

### ✅ Do
- **Trunk-based dev** : Branches courtes (< 2 jours)
- **Nommage clair** : `feature/issue-42-wakatime`, `fix/coverage-error`
- **Merge fréquent** : Éviter divergence avec main
- **Delete après merge** : Pas de branches zombies

### ❌ Don't
- Branches longues (> 1 semaine)
- Nommage vague : `test`, `my-branch`, `new-feature`
- Oublier de pull avant push
- Garder 50 branches locales

## .gitignore

### ✅ Do
- **Ignore dès le début** : logs/, cache/, __pycache__/
- **Exceptions explicites** : `!storage/.gitkeep`
- **Secrets** : .env, *.key, credentials.json
- **Build artifacts** : dist/, build/, *.pyc

### ❌ Don't
- Commiter node_modules/ ou venv/
- Commiter .env avec secrets
- Ignorer trop large (*.py ignorerait tout !)

## Pull Requests

### ✅ Do
- **Description claire** : Quoi, Pourquoi, Comment
- **Petites PR** : < 400 lignes (revue plus facile)
- **Tests passent** : CI vert avant review
- **Self-review** : Relire sa propre PR d'abord

### ❌ Don't
- PR de 2000 lignes
- Forcer le merge si CI rouge
- Ignorer les commentaires de review

## Historique Git

### ✅ Do
- **Historique propre** : `git rebase -i` pour nettoyer avant merge
- **Messages cohérents** : Suivre convention équipe
- **Référencer issues** : "Closes #42" dans commit message

### ❌ Don't
- `git push --force` sur main
- Réécrire l'historique public
- Commits de merge inutiles

---

**Ressources :**
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Pro Git Book](https://git-scm.com/book/en/v2)
- [Atlassian Git Tutorials](https://www.atlassian.com/git/tutorials)
