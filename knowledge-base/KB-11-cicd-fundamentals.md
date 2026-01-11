# CI/CD Fundamentals

## 📝 Définition

**CI/CD** signifie **Continuous Integration / Continuous Deployment** (ou Delivery). C'est un ensemble de pratiques DevOps qui automatisent le cycle de vie du logiciel : du commit de code jusqu'au déploiement en production.

**CI (Continuous Integration) :** Intégrer fréquemment le code dans la branche principale (main/master), avec validation automatique (tests, linting).

**CD (Continuous Deployment) :** Déployer automatiquement chaque changement validé en production.

**CD (Continuous Delivery) :** Avoir le code toujours prêt à être déployé, mais avec déploiement manuel.

---

## 🎯 Concepts Clés

### 1. Les 3 Piliers du CI/CD

```
┌─────────────────────────────────────────────────────────────┐
│                    CONTINUOUS INTEGRATION                   │
│                                                             │
│  Developer → Commit → Build → Test → Lint → Merge         │
│                           ↓                                 │
│                    [Pipeline CI]                            │
│                                                             │
│  Objectif: Détecter les bugs tôt (shift-left testing)      │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    CONTINUOUS DELIVERY                      │
│                                                             │
│  Merged Code → Package → Deploy to Staging → Tests E2E     │
│                           ↓                                 │
│                   [Manual Approval]                         │
│                           ↓                                 │
│                    Deploy to Prod                           │
│                                                             │
│  Objectif: Code toujours prêt à être déployé               │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   CONTINUOUS DEPLOYMENT                     │
│                                                             │
│  Merged Code → Package → Deploy to Staging → Tests E2E     │
│                                         ↓                   │
│                               [Auto Deploy to Prod]         │
│                                                             │
│  Objectif: Livraison instantanée en production              │
└─────────────────────────────────────────────────────────────┘
```

### 2. Composants d'un Pipeline CI/CD

#### Pipeline CI Typique
```yaml
stages:
  - build      # Compilation du code
  - test       # Tests unitaires, intégration
  - lint       # Vérification qualité (black, pylint)
  - scan       # Scan sécurité (secrets, vulnérabilités)
  - package    # Build Docker image
```

#### Pipeline CD Typique
```yaml
stages:
  - deploy-staging     # Déploiement environnement de test
  - smoke-tests        # Tests basiques (app démarre ?)
  - deploy-prod        # Déploiement production
  - health-check       # Vérification post-déploiement
  - rollback           # Si échec, retour version précédente
```

### 3. Pratiques Clés

| Pratique | Description | Bénéfice |
|----------|-------------|----------|
| **Small Commits** | Commiter fréquemment (plusieurs fois/jour) | Moins de conflits, bugs détectés tôt |
| **Automated Tests** | Tests exécutés à chaque commit | Confiance dans le code |
| **Fast Feedback** | Pipeline < 10 minutes | Développeurs pas bloqués |
| **Trunk-Based Dev** | Tout le monde pousse sur main | Pas de branches longues |
| **Feature Flags** | Activer/désactiver features sans deploy | Déploiement sans risque |
| **Rollback Strategy** | Retour version précédente en < 5 min | Résilience |

---

## 💡 Exemple Concret (SkillOps)

### Pipeline CI - GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest --cov=lms --cov-report=xml

      - name: Check coverage
        run: coverage report --fail-under=70

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Format check
        run: black --check .

      - name: Lint
        run: pylint lms/

      - name: Type check
        run: mypy lms/

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Scan secrets
        run: gitleaks detect --verbose
```

### Workflow Développeur

```bash
# 1. Développeur code localement
git checkout -b feature/wakatime-integration

# 2. Commit avec message conventionnel
git commit -m "feat(api): add WakaTime client with retry logic"

# 3. Push déclenche automatiquement le pipeline CI
git push origin feature/wakatime-integration

# 4. GitHub Actions exécute:
#    - Tests unitaires (pytest)
#    - Linting (black, pylint, mypy)
#    - Scan sécurité (gitleaks)

# 5. Si vert ✅ → Pull Request + Code Review
# 6. Après approval → Merge dans main
# 7. Pipeline CD déploie automatiquement (si configuré)
```

---

## ✅ Bonnes Pratiques

### Do ✅

**CI (Continuous Integration) :**
- **Commiter au moins 1×/jour** : Intégration continue signifie intégration fréquente
- **Garder le pipeline rapide** : < 10 minutes idéalement
- **Faire échouer le build si tests échouent** : Pas de compromis sur la qualité
- **Automatiser TOUT** : Tests, linting, sécurité, build
- **Fixer immédiatement un build cassé** : Priorité absolue

**CD (Continuous Deployment) :**
- **Automatiser le déploiement** : Zero-downtime deployments
- **Déployer en environnements** : Dev → Staging → Prod
- **Smoke tests après déploiement** : Vérifier que l'app démarre
- **Stratégie de rollback** : Retour arrière en < 5 minutes
- **Feature flags** : Déployer code désactivé, activer progressivement

### Don't ❌

- **Ne pas commiter sur main sans CI** : Toujours passer par le pipeline
- **Ne pas ignorer les tests flaky** : Les fixer ou les supprimer
- **Ne pas avoir de pipeline > 30 min** : Personne n'attendra, ils skipperont les tests
- **Ne pas déployer le vendredi soir** : Si ça casse, c'est votre weekend qui saute
- **Ne pas avoir de secrets en dur** : Utiliser secrets management (GitHub Secrets, Vault)

---

## 📚 Ressources pour Approfondir

### Livres 📖

1. **"Continuous Delivery"** - Jez Humble & David Farley
   → La bible du CD, patterns de déploiement
   → [Amazon](https://www.amazon.com/Continuous-Delivery-Deployment-Automation-Addison-Wesley/dp/0321601912)

2. **"Accelerate"** - Nicole Forsgren, Jez Humble, Gene Kim
   → Métriques DevOps (DORA), corrélation CI/CD et performance
   → [Amazon](https://www.amazon.com/Accelerate-Software-Performing-Technology-Organizations/dp/1942788339)

3. **"The Phoenix Project"** - Gene Kim
   → Roman sur la transformation DevOps
   → Illustre l'importance du CI/CD

### Articles & Guides 📝

- [Martin Fowler - Continuous Integration](https://martinfowler.com/articles/continuousIntegration.html)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [CircleCI Best Practices](https://circleci.com/docs/2.0/best-practices/)

### Métriques DORA 📊

Les 4 métriques clés pour mesurer la performance CI/CD :

| Métrique | Élite | High | Medium | Low |
|----------|-------|------|--------|-----|
| **Deployment Frequency** | Multiple/day | Weekly-Monthly | Monthly-Semi-annually | < Semi-annually |
| **Lead Time for Changes** | < 1 hour | 1 day-1 week | 1 week-1 month | > 1 month |
| **Time to Restore Service** | < 1 hour | < 1 day | 1 day-1 week | > 1 week |
| **Change Failure Rate** | 0-15% | 16-30% | 16-30% | 16-30% |

Source : [DORA State of DevOps Report](https://dora.dev/)

### Outils CI/CD 🛠️

| Outil | Type | Pour/Contre |
|-------|------|-------------|
| **GitHub Actions** | Cloud | ✅ Intégré GitHub, gratuit (2000 min) |
| **GitLab CI** | Cloud/Self-hosted | ✅ Pipeline YAML puissant, runners gratuits |
| **Jenkins** | Self-hosted | ✅ Très flexible ❌ Complexe à maintenir |
| **CircleCI** | Cloud | ✅ Rapide ❌ Payant au-delà free tier |
| **Travis CI** | Cloud | ✅ Simple ❌ Moins populaire qu'avant |
| **Azure Pipelines** | Cloud | ✅ Intégré Azure, généreux free tier |

---

## 🔗 Voir Aussi

- [KB-12: Testing Strategies](KB-12-testing-strategies.md) - Tests automatisés dans le pipeline
- [KB-13: Code Quality](KB-13-code-quality.md) - Linting et formatting dans CI
- [KB-14: Secrets Management](KB-14-secrets-management.md) - Gérer secrets dans CI/CD
- [KB-16: Conventional Commits](KB-16-conventional-commits.md) - Format commits pour changelog auto

---

## 🎯 Application dans SkillOps

### Pipeline CI Configuré

Dans [04-sprint-planning-sprint-1.md](../project-lifecycle/04-sprint-planning-sprint-1.md), task **T-CI-1** :

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov=lms --cov-report=xml
      - run: coverage report --fail-under=70

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install black pylint mypy
      - run: black --check .
      - run: pylint lms/
      - run: mypy lms/
```

### Métriques SkillOps (Objectifs)

| Métrique DORA | Objectif | Justification |
|---------------|----------|---------------|
| **Deployment Frequency** | Plusieurs/jour | Trunk-based dev, merge fréquent |
| **Lead Time** | < 1h | Pipeline CI < 10 min, review rapide |
| **MTTR** | < 30 min | Rollback Git simple (git revert) |
| **Change Failure Rate** | < 15% | Tests coverage > 70% |

---

## 📊 Checklist CI/CD

### CI (Continuous Integration)
- [ ] Pipeline s'exécute à chaque commit/PR
- [ ] Tests unitaires passent (coverage > 70%)
- [ ] Linting valide le code (black, pylint)
- [ ] Type checking valide les types (mypy)
- [ ] Scan sécurité détecte secrets (gitleaks)
- [ ] Build réussit (package, Docker)
- [ ] Feedback < 10 minutes
- [ ] Build cassé bloque le merge

### CD (Continuous Deployment) - Futur
- [ ] Déploiement automatique après merge
- [ ] Environnements séparés (staging/prod)
- [ ] Smoke tests post-déploiement
- [ ] Rollback automatique si échec health check
- [ ] Zero-downtime deployment
- [ ] Monitoring post-déploiement (métriques, logs)

---

## 🧪 Exemple : Impact du CI/CD

**Avant CI/CD (développement classique) :**
```
Développeur code pendant 2 semaines
→ Merge dans main (250 commits d'un coup)
→ Tests manuels (1 journée)
→ 15 bugs découverts
→ 3 jours pour fixer
→ Déploiement manuel (erreurs possibles)
→ Total: 3 semaines pour livrer
```

**Avec CI/CD :**
```
Développeur commit 2×/jour
→ Pipeline CI valide automatiquement (5 min)
→ Bugs détectés immédiatement
→ Fix en 10 minutes (contexte frais)
→ Merge quotidien
→ Déploiement automatique
→ Total: Livraison continue, pas d'attente
```

**Gains :**
- ✅ Bugs détectés 10× plus tôt (shift-left)
- ✅ Feedback instantané (< 10 min vs 3 semaines)
- ✅ Réduction risque (petits changements vs gros batch)
- ✅ Moral équipe (pas de "merge hell")

---

**Dernière mise à jour :** 9 janvier 2026
**Statut :** 🚧 En cours d'implémentation dans SkillOps (Sprint 1, Jour 7)
