# ADR - Architecture Decision Records
## SkillOps Learning Management System

**Version:** 1.0  
**Date:** 9 janvier 2026  
**Tech Lead:** MB (DevOps Engineer)  
**Status:** Approved

---

## Introduction aux ADRs

Les Architecture Decision Records (ADRs) documentent **pourquoi** certaines décisions techniques ont été prises. Contrairement à une documentation technique classique qui décrit **comment** le système fonctionne, les ADRs expliquent le **raisonnement** derrière chaque choix majeur.

**Format standard d'un ADR :**
1. **Contexte** : Quel problème devons-nous résoudre ?
2. **Options considérées** : Quelles alternatives existaient ?
3. **Décision** : Quel choix avons-nous fait ?
4. **Conséquences** : Quels sont les impacts (positifs et négatifs) ?

---

## Table des Matières

- [ADR-001: Choix du Langage de Programmation](#adr-001-choix-du-langage-de-programmation)
- [ADR-002: Interface CLI vs Web Application](#adr-002-interface-cli-vs-web-application)
- [ADR-003: Framework CLI (Typer vs Click vs Argparse)](#adr-003-framework-cli-typer-vs-click-vs-argparse)
- [ADR-004: Persistence des Données (JSON vs SQLite vs PostgreSQL)](#adr-004-persistence-des-données-json-vs-sqlite-vs-postgresql)
- [ADR-005: Gestion des Secrets (dotenv vs Vault vs Cloud Secrets)](#adr-005-gestion-des-secrets-dotenv-vs-vault-vs-cloud-secrets)
- [ADR-006: Architecture Pattern (State Machine vs Event-Driven)](#adr-006-architecture-pattern-state-machine-vs-event-driven)
- [ADR-007: Testing Strategy (Pytest vs Unittest)](#adr-007-testing-strategy-pytest-vs-unittest)
- [ADR-008: CI/CD Platform (GitHub Actions vs GitLab CI vs Jenkins)](#adr-008-cicd-platform-github-actions-vs-gitlab-ci-vs-jenkins)

---

## ADR-001: Choix du Langage de Programmation

**Date:** 2026-01-09  
**Statut:** ✅ Approuvé

### Contexte

Nous devons choisir un langage de programmation pour développer SkillOps CLI. Les critères principaux sont :
- Rapidité de développement (MVP en 2 semaines)
- Écosystème riche pour APIs (WakaTime, Gemini, GitHub, Telegram)
- Facilité de packaging et distribution
- Courbe d'apprentissage (pour moi en tant qu'apprenant DevOps)

### Options Considérées

#### Option A: Python 3.11+
**Pour :**
- ✅ Écosystème énorme (requests, rich, typer, pytest)
- ✅ Intégrations API natives (google-generativeai, PyGithub)
- ✅ Prototypage rapide
- ✅ Je connais déjà Python (réduire la courbe d'apprentissage)
- ✅ Excellentes bibliothèques CLI (Typer, Rich, Click)

**Contre :**
- ❌ Performance moindre que Go/Rust (mais pas critique pour CLI)
- ❌ Gestion des dépendances parfois complexe (venv, pip)
- ❌ Pas de typage strict natif (nécessite mypy)

#### Option B: Go
**Pour :**
- ✅ Compilation en binaire statique (distribution facile)
- ✅ Performance excellente
- ✅ Concurrence native (goroutines)
- ✅ Typage fort

**Contre :**
- ❌ Écosystème moins riche pour IA/ML
- ❌ Verbeux pour scripts rapides
- ❌ Courbe d'apprentissage supplémentaire
- ❌ Moins de libs pour APIs tierces

#### Option C: Rust
**Pour :**
- ✅ Performance maximale
- ✅ Sécurité mémoire
- ✅ Binaire statique

**Contre :**
- ❌ Courbe d'apprentissage très raide
- ❌ Développement plus lent
- ❌ Écosystème moins mature pour APIs
- ❌ Overkill pour un CLI simple

### Décision

**Choix : Python 3.11+**

**Justification :**
- Le projet est d'abord un **outil d'apprentissage** : Python me permet de me concentrer sur les concepts DevOps (CI/CD, infra, monitoring) plutôt que sur la syntaxe du langage
- MVP rapide : bibliothèques existantes pour toutes les APIs
- Performance non critique : CLI lancé manuellement, pas de contraintes temps réel
- Typage avec mypy pour éviter les bugs

### Conséquences

**Positives :**
- Développement rapide du MVP (objectif 2 semaines tenable)
- Nombreux exemples et documentation pour APIs tierces
- Facilité de maintenance et évolution

**Négatives :**
- Nécessite Python installé sur la machine (pas de binaire standalone)
- Gestion des dépendances via requirements.txt (complexité managée avec poetry plus tard)
- Performance moindre (acceptable pour usage quotidien)

**Mitigations :**
- Utiliser Poetry pour gestion propre des dépendances
- Typage strict avec mypy dans CI/CD
- Tests avec coverage > 80% pour éviter bugs

---

## ADR-002: Interface CLI vs Web Application

**Date:** 2026-01-09  
**Statut:** ✅ Approuvé

### Contexte

Nous devons choisir le type d'interface pour SkillOps. L'utilisateur (moi) doit pouvoir lancer sa routine d'apprentissage quotidienne facilement.

### Options Considérées

#### Option A: CLI (Command Line Interface)
**Pour :**
- ✅ Démarrage instantané (pas de serveur à lancer)
- ✅ Légèreté (pas de frontend, pas de base de données complexe)
- ✅ Intégration facile dans scripts (cron, systemd)
- ✅ Focus sur la logique métier, pas sur l'UI
- ✅ Développement rapide

**Contre :**
- ❌ Pas de visualisations graphiques (charts, heatmaps)
- ❌ Moins intuitif pour utilisateurs non-tech
- ❌ Difficile de partager avec la communauté

#### Option B: Web Application (FastAPI + React)
**Pour :**
- ✅ Interface riche (graphiques, dashboards)
- ✅ Accessible depuis n'importe où (mobile, desktop)
- ✅ Partage facile avec la communauté
- ✅ UX moderne

**Contre :**
- ❌ Temps de développement 4-6× plus long
- ❌ Complexité infra (backend + frontend + base de données)
- ❌ Nécessite serveur running 24/7
- ❌ Overhead pour usage personnel

#### Option C: TUI (Text User Interface - htop style)
**Pour :**
- ✅ Interface riche en terminal
- ✅ Interactif sans quitter le terminal

**Contre :**
- ❌ Complexité développement (gestion événements, refresh)
- ❌ Bibliothèques moins matures (Textual)
- ❌ Pas de gain majeur vs CLI simple

### Décision

**Choix : CLI avec menus interactifs (via Rich + Inquirer)**

**Justification :**
- MVP rapide : focus sur les fonctionnalités core, pas l'UI
- Usage quotidien : je lance l'outil le matin, pas besoin de dashboard 24/7
- Évolution possible : CLI en v1.0, dashboard web en v2.0 (consomme la même logique)
- DevOps learning : automatisation via scripts, cron, CI/CD

**Compromis :** Menus interactifs (Inquirer) pour réduire la friction (pas besoin de mémoriser des commandes)

### Conséquences

**Positives :**
- Développement rapide (2 semaines pour MVP tenable)
- Automatisation facile (cron, systemd)
- Léger et portable
- Focus sur logique métier, pas sur CSS/JS

**Négatives :**
- Pas de visualisations graphiques (temporaire)
- Moins "sexy" pour un portfolio (mais compense avec doc professionnelle)

**Évolution future :**
- Phase 5 (mois 3) : Dashboard web FastAPI + React
- Réutilisation logique métier (API backend)
- CLI reste l'interface principale, web en complément

---

## ADR-003: Framework CLI (Typer vs Click vs Argparse)

**Date:** 2026-01-09  
**Statut:** ✅ Approuvé

### Contexte

Besoin d'un framework pour construire le CLI avec :
- Menus interactifs
- Validation des inputs
- Affichage formaté (couleurs, tableaux)
- Documentation auto-générée

### Options Considérées

#### Option A: Typer + Rich + Inquirer
**Pour :**
- ✅ Typer : syntaxe moderne avec type hints
- ✅ Rich : affichage magnifique (tableaux, progress bars, couleurs)
- ✅ Inquirer : menus interactifs style questions/réponses
- ✅ Documentation auto-générée depuis docstrings
- ✅ Intégration parfaite Python 3.11+

**Contre :**
- ❌ 3 bibliothèques à combiner (légère complexité)

#### Option B: Click
**Pour :**
- ✅ Maturité (utilisé par Flask, pytest)
- ✅ Décorateurs simples

**Contre :**
- ❌ Pas de type hints natifs
- ❌ UI moins riche que Rich
- ❌ Pas de menus interactifs natifs

#### Option C: Argparse (stdlib)
**Pour :**
- ✅ Aucune dépendance externe
- ✅ Standard library

**Contre :**
- ❌ Verbeux et complexe
- ❌ Pas d'UI riche
- ❌ Pas de menus interactifs

### Décision

**Choix : Typer + Rich + Inquirer**

**Justification :**
- Typer pour la structure CLI moderne
- Rich pour l'UX (réduire friction visuelle)
- Inquirer pour navigation intuitive (pas de commandes à mémoriser)

### Conséquences

**Positives :**
- CLI professionnel et agréable à utiliser
- Type safety avec mypy
- Documentation auto-générée

**Négatives :**
- 3 dépendances à maintenir (mitigé : toutes stables et populaires)

---

## ADR-004: Persistence des Données (JSON vs SQLite vs PostgreSQL)

**Date:** 2026-01-09  
**Statut:** ✅ Approuvé

### Contexte

Nous devons stocker :
- État actuel (quelle étape, timestamp)
- Historique quotidien (métriques par jour)
- Statistiques agrégées (streak, moyenne)

Volume : ~30 entrées/mois × 12 mois = 360 entrées/an (très faible)

### Options Considérées

#### Option A: JSON local (.state.yaml, .progress.json)
**Pour :**
- ✅ Zero setup (pas de serveur DB)
- ✅ Lisible par humain (debug facile)
- ✅ Versionnable avec Git
- ✅ Backup simple (cp files)
- ✅ Parfait pour volume faible

**Contre :**
- ❌ Pas de requêtes SQL complexes
- ❌ Performance si gros volume (non applicable ici)
- ❌ Pas de transactions atomiques

#### Option B: SQLite
**Pour :**
- ✅ SQL queries
- ✅ Transactions ACID
- ✅ Pas de serveur (fichier local)

**Contre :**
- ❌ Overkill pour volume faible
- ❌ Moins lisible (binaire)
- ❌ Migration complexity

#### Option C: PostgreSQL
**Pour :**
- ✅ Production-grade
- ✅ Scalable

**Contre :**
- ❌ Serveur à maintenir
- ❌ Overkill absolu pour usage personnel
- ❌ Complexité setup

### Décision

**Choix : JSON/YAML local**

**Structure :**
```
storage/
├── .state.yaml          # État actuel (step_id, timestamp, session_id)
├── .progress.json       # Historique [{date, steps, time, cards}, ...]
└── .metrics.json        # Agrégats {streak, avg_time, total_cards}
```

**Justification :**
- Volume très faible (pas de problème de performance)
- Simplicité maximale (pas de serveur, pas de migrations)
- Debuggable (cat .progress.json)
- Versionnable (Git pour backup)

### Conséquences

**Positives :**
- Zero configuration
- Portable (copier dossier = migration)
- Backup = Git commit

**Négatives :**
- Pas de requêtes complexes (acceptable : queries simples en Python)
- Concurrent writes possibles (mitigé : usage mono-utilisateur)

**Évolution future :**
- Si multi-users (v2.0) : migration vers PostgreSQL
- Migration facile (JSON → SQL INSERT via script)

---

## ADR-005: Gestion des Secrets (dotenv vs Vault vs Cloud Secrets)

**Date:** 2026-01-09  
**Statut:** ✅ Approuvé

### Contexte

Nous devons stocker des secrets :
- WakaTime API key
- Gemini API key
- GitHub token
- Telegram bot token

Environnements :
- Dev local (laptop)
- CI/CD (GitHub Actions)
- Production future (cloud)

### Options Considérées

#### Option A: .env local + GitHub Secrets (CI/CD)
**Pour :**
- ✅ Simple pour dev local (python-dotenv)
- ✅ GitHub Secrets gratuit et intégré CI/CD
- ✅ Pas de serveur additionnel

**Contre :**
- ❌ Pas de rotation automatique
- ❌ Pas d'audit trail

#### Option B: HashiCorp Vault
**Pour :**
- ✅ Production-grade
- ✅ Rotation automatique
- ✅ Audit complet

**Contre :**
- ❌ Serveur à maintenir
- ❌ Overkill pour projet perso
- ❌ Courbe d'apprentissage

#### Option C: AWS Secrets Manager / GCP Secret Manager
**Pour :**
- ✅ Managed service
- ✅ Rotation automatique
- ✅ IAM integration

**Contre :**
- ❌ Coût (même minime)
- ❌ Vendor lock-in
- ❌ Overkill pour MVP

### Décision

**Choix : .env local + GitHub Secrets**

**Implémentation :**
```python
# .env (gitignored)
WAKATIME_API_KEY=waka_xxx
GEMINI_API_KEY=AIza_xxx
GITHUB_TOKEN=ghp_xxx
TELEGRAM_BOT_TOKEN=123456:ABC

# CI/CD : GitHub Secrets
# Injection automatique dans workflow
```

**Justification :**
- Dev local : `.env` simple et rapide
- CI/CD : GitHub Secrets secure et gratuit
- Pas de serveur à maintenir

### Conséquences

**Positives :**
- Zero cost
- Setup en 5 minutes
- Suffisant pour usage personnel

**Négatives :**
- Pas de rotation automatique (manuel)
- Pas d'audit trail (acceptable pour projet perso)

**Évolution future :**
- Phase 5 (cloud) : migration vers AWS Secrets Manager
- Facile : changer juste la méthode de récupération

**Sécurité additionnelle :**
- `.env` dans `.gitignore`
- Pre-commit hook pour détecter secrets dans commits
- Scan des secrets avec gitleaks dans CI/CD

---

## ADR-006: Architecture Pattern (State Machine vs Event-Driven)

**Date:** 2026-01-09  
**Statut:** ✅ Approuvé

### Contexte

L'application doit orchestrer 8 étapes séquentielles :
1. REVIEW_METRICS
2. FORMATION
3. ANALYSIS
4. REINFORCE
5. ZETTELKASTEN
6. FLASHCARDS
7. PORTFOLIO
8. REFLECTION

Contraintes :
- Ordre flexible (utilisateur peut sauter)
- Sauvegarde état entre sessions
- Transitions claires

### Options Considérées

#### Option A: State Machine
**Pour :**
- ✅ États explicites (8 steps)
- ✅ Transitions bien définies (next, previous, skip)
- ✅ Facile à visualiser (diagramme)
- ✅ État persistant simple (.state.yaml)

**Contre :**
- ❌ Rigidité si workflow complexe

#### Option B: Event-Driven Architecture
**Pour :**
- ✅ Flexible (events = step_completed, step_skipped)
- ✅ Extensible (ajouter listeners facilement)

**Contre :**
- ❌ Complexité overhead pour workflow simple
- ❌ Debugging plus difficile
- ❌ Overkill pour 8 étapes linéaires

### Décision

**Choix : State Machine**

**Implémentation :**
```python
from enum import Enum

class Step(Enum):
    REVIEW_METRICS = 1
    FORMATION = 2
    ANALYSIS = 3
    REINFORCE = 4
    ZETTELKASTEN = 5
    FLASHCARDS = 6
    PORTFOLIO = 7
    REFLECTION = 8

class StateMachine:
    def __init__(self, state_file: Path):
        self.current_step = self.load_state()
    
    def next_step(self) -> Step:
        # Transition logic
        pass
    
    def complete_step(self, step: Step):
        # Save progress, move to next
        pass
```

**Justification :**
- Workflow linéaire simple (8 étapes)
- État facile à persister (current_step_id)
- Debugging simple (print current state)

### Conséquences

**Positives :**
- Code simple et maintenable
- État clair à tout moment
- Facile de visualiser avec diagramme

**Négatives :**
- Si workflow devient complexe (branches, conditions), refactoring nécessaire

**Évolution future :**
- Si besoin de parallélisme (ex: Formation + Analysis en même temps), migrer vers Event-Driven

---

## ADR-007: Testing Strategy (Pytest vs Unittest)

**Date:** 2026-01-09  
**Statut:** ✅ Approuvé

### Contexte

Nous devons tester :
- Logique métier (state machine, workflows)
- Intégrations API (avec mocks)
- CLI (inputs/outputs)

Objectif : Coverage > 80%

### Options Considérées

#### Option A: Pytest
**Pour :**
- ✅ Syntaxe simple (pas de self, pas de classes)
- ✅ Fixtures puissantes
- ✅ Plugins riches (pytest-cov, pytest-mock)
- ✅ Assertions claires
- ✅ Standard dans l'industrie Python

**Contre :**
- ❌ Dépendance externe (vs stdlib)

#### Option B: Unittest (stdlib)
**Pour :**
- ✅ Standard library (pas de dépendance)
- ✅ Familier si vient de Java (JUnit style)

**Contre :**
- ❌ Verbeux (classes, self, setUp/tearDown)
- ❌ Moins de features que pytest

### Décision

**Choix : Pytest**

**Structure :**
```
tests/
├── unit/
│   ├── test_state_machine.py
│   ├── test_workflows.py
│   └── test_persistence.py
├── integration/
│   ├── test_api_wakatime.py
│   ├── test_api_gemini.py
│   └── test_api_github.py
└── e2e/
    └── test_cli_flow.py
```

**Justification :**
- Syntaxe moderne et concise
- Fixtures pour setup/teardown propre
- Coverage reporting intégré

### Conséquences

**Positives :**
- Tests lisibles et maintenables
- Coverage facile avec pytest-cov
- Mocking simple avec pytest-mock

**Négatives :**
- Une dépendance de plus (acceptable : standard industrie)

**CI/CD Integration :**
```yaml
# .github/workflows/ci.yml
- name: Run tests
  run: |
    pytest --cov=lms --cov-report=xml
    coverage report --fail-under=80
```

---

## ADR-008: CI/CD Platform (GitHub Actions vs GitLab CI vs Jenkins)

**Date:** 2026-01-09  
**Statut:** ✅ Approuvé

### Contexte

Nous devons automatiser :
- Tests à chaque commit
- Linting (black, pylint, mypy)
- Build (futurs Docker images)
- Déploiement (futur)

### Options Considérées

#### Option A: GitHub Actions
**Pour :**
- ✅ Intégré GitHub (repo déjà sur GitHub)
- ✅ Gratuit pour repos publics (2000 min/mois)
- ✅ Marketplace d'actions (setup-python, etc.)
- ✅ YAML simple

**Contre :**
- ❌ Vendor lock-in GitHub

#### Option B: GitLab CI
**Pour :**
- ✅ Gratuit et généreux (400 min/mois gratuit)
- ✅ Runners auto-hébergés possibles

**Contre :**
- ❌ Repo pas sur GitLab (migration nécessaire)
- ❌ Courbe apprentissage additionnelle

#### Option C: Jenkins
**Pour :**
- ✅ Self-hosted (contrôle total)
- ✅ Plugins extensifs

**Contre :**
- ❌ Serveur à maintenir
- ❌ Setup complexe
- ❌ Overkill pour projet perso

### Décision

**Choix : GitHub Actions**

**Pipeline :**
```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: pytest --cov
      - run: black --check .
      - run: pylint lms/
      - run: mypy lms/
```

**Justification :**
- Déjà sur GitHub
- Gratuit et simple
- Intégration native PRs

### Conséquences

**Positives :**
- Zero setup (juste créer .yml)
- Feedback immédiat sur PRs
- Badge status dans README

**Négatives :**
- Dépendance GitHub (mitigé : migration possible vers GitLab CI si besoin)

**Évolution future :**
- Ajout job `deploy` pour Docker push
- Matrix testing (Python 3.11, 3.12, 3.13)

---

## Récapitulatif des Décisions

| ADR | Décision | Justification Clé |
|-----|----------|-------------------|
| **001** | Python 3.11+ | Écosystème riche, rapidité dev, apprentissage |
| **002** | CLI (pas web) | MVP rapide, focus logique métier |
| **003** | Typer + Rich | UX moderne, menus interactifs |
| **004** | JSON local | Simplicité, volume faible, versionnable |
| **005** | .env + GitHub Secrets | Simple, gratuit, suffisant pour perso |
| **006** | State Machine | Workflow linéaire clair |
| **007** | Pytest | Standard industrie, fixtures, coverage |
| **008** | GitHub Actions | Intégré, gratuit, simple |

---

## Prochaines Étapes

Maintenant que les décisions techniques sont documentées, nous pouvons :

1. ✅ **Setup environnement** (Python 3.11, venv, requirements.txt)
2. ✅ **Structure projet** (créer dossiers src/, tests/, storage/)
3. ✅ **Squelette code** (main.py, state_machine.py, cli.py)
4. ✅ **Premier test** (test_state_machine.py)
5. ✅ **CI/CD** (créer .github/workflows/ci.yml)

---

## Review & Validation

| Rôle | Nom | Date | Validation |
|------|-----|------|------------|
| **Tech Lead** | MB | 2026-01-09 | ✅ Approuvé |
| **Product Manager** | PM Team | _Pending_ | ⏳ Review cohérence URD |
| **DevOps Engineer** | MB | 2026-01-09 | ✅ Approuvé |

---

**Status:** Approved - Ready for Sprint Planning  
**Next Document:** [04-sprint-planning-sprint-1.md](04-sprint-planning-sprint-1.md)

---

*Ces ADRs sont des documents vivants : si une décision doit être revue, un nouvel ADR sera créé (ADR-009, etc.) pour documenter le changement et le raisonnement.*
