# SkillOps 🚀

> **An intelligent Learning Management System (LMS) CLI for orchestrating DevOps self-learning with AI, automatic tracking, and notifications.**

[![CI](https://github.com/M-Boiguille/SkillOps/actions/workflows/ci.yml/badge.svg)](https://github.com/M-Boiguille/SkillOps/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/M-Boiguille/SkillOps/branch/main/graph/badge.svg)](https://codecov.io/gh/M-Boiguille/SkillOps)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![DevOps](https://img.shields.io/badge/Focus-DevOps%20Learning-orange.svg)]()
[![Tests](https://img.shields.io/badge/Tests-276%2F276%20✓-brightgreen.svg)]()

---

## 📖 Overview

**SkillOps** is an automated learning management system designed to optimize daily DevOps training routines. Rather than manually managing tracking, notes, and revisions across 10 different tools, I built a CLI tool that intelligently orchestrates 8 learning steps using a state machine.

### 🎯 Le Problème Résolu

En tant qu'apprenant DevOps autodidacte, je faisais face à :
- ❌ **Manque de discipline** : oublier certaines étapes de ma routine
- ❌ **Tracking manuel chronophage** : copier-coller des métriques entre outils
- ❌ **Absence de feedback** : difficile de mesurer ma progression
- ❌ **Perte de contexte** : notes dispersées, pas de vision d'ensemble

### ✅ La Solution

Un **outil CLI Python** qui :
- 🤖 Automatise le tracking de mon temps de code (WakaTime)
- 🧠 Génère des questions/réponses contextuelles via IA (Gemini)
- 📝 Synchronise mes notes Obsidian et flashcards Anki
- 🔔 M'envoie des rappels et bilans quotidiens (Telegram)
- 📊 Visualise ma progression avec des métriques claires
- 🔄 Gère mon portfolio GitHub automatiquement

---

## 📊 Project Status

### Sprint Progress

| Sprint | Duration | Status | Features | Tests |
|--------|----------|--------|----------|-------|
| **Sprint 1** | 11 jan 2026 | ✅ COMPLETED | 5 core steps + state machine | 216/216 ✓ |
| **Sprint 2** | 11 jan 2026 | ✅ COMPLETED | Telegram + Flashcards + GitHub | 276/276 ✓ |
| **Sprint 3** | 12-18 jan 2026 | 🔄 IN PLANNING | UX Polish + Integration Tests | - |

### Features Status

- ✅ Review Metrics (Sprint 1)
- ✅ Formation Tracking (Sprint 1)
- ✅ Analysis with AI (Sprint 1)
- ✅ Reinforcement (Sprint 1)
- ✅ Zettelkasten Notes (Sprint 1)
- ✅ **Flashcard Generation** (Sprint 2 - NEW!)
- ✅ **Portfolio Automation** (Sprint 2 - NEW!)
- ✅ **Daily Notifications** (Sprint 2 - NEW!)
- 🔄 UX Polish (Sprint 3 - Coming Soon)
- 🔄 DevOps Automation (Sprint 3 - Coming Soon)

---

```
┌──────────────────────────────────────────────────────────────┐
│                    SkillOps CLI Engine                       │
│                   State Machine (8 Steps)                    │
└────────────┬─────────────────────────────────┬───────────────┘
             │                                 │
    ┌────────▼─────────┐              ┌───────▼────────┐
    │  User Interface  │              │ Data Tracking  │
    │  ├─ Typer (CLI)  │              │ ├─ .state.yaml │
    │  ├─ Rich (UI)    │              │ ├─ .progress   │
    │  └─ Inquirer     │              │ └─ .metrics    │
    └──────────────────┘              └────────────────┘
             │
    ┌────────┴────────────────────────────────────────┐
    │                                                  │
┌───▼──────────┐  ┌──────────┐  ┌─────────┐  ┌──────▼──────┐
│ API Clients  │  │ Workflows│  │ Storage │  │ Integration │
│              │  │          │  │         │  │             │
│ ├─ Gemini AI│  │ ├─ Steps │  │ ├─ JSON │  │ ├─ Obsidian │
│ ├─ WakaTime │  │ ├─ State │  │ ├─ YAML │  │ ├─ GitHub   │
│ ├─ GitHub   │  │ └─ Events│  │ └─ CSV  │  │ └─ Telegram │
│ └─ Telegram │  │          │  │         │  │             │
└──────────────┘  └──────────┘  └─────────┘  └─────────────┘
```

---

## 📚 Documentation du Cycle de Vie Projet

**⭐ Pour les recruteurs** : Ce projet suit une méthodologie professionnelle complète, documentée dans [project-lifecycle/](project-lifecycle/).

Ce dossier démontre ma compréhension du cycle de développement logiciel en entreprise :
- 📋 [Product Discovery](project-lifecycle/01-product-discovery-session.md) - Clarification des besoins entre PM et PO
- 📝 [User Requirements Document (URD)](project-lifecycle/02-urd-user-requirements-document.md) - User stories, NFRs, KPIs
- 🏗️ [Architecture Decision Records (ADR)](project-lifecycle/03-adr-architecture-decision-records.md) - Décisions techniques justifiées

**Pourquoi c'est important** : Je ne code pas "au feeling", je suis un processus structuré (Discovery → Specs → Architecture → Dev) comme dans une vraie entreprise tech.

---

## 🎨 Fonctionnalités Principales

### 1️⃣ **Review Metrics** 📊
- Affiche les métriques de la veille (temps codé, étapes complétées)
- Compare avec les objectifs quotidiens
- Calcule le "streak" de jours consécutifs

### 2️⃣ **Formation Tracking** ⏱️
- Intégration WakaTime pour tracking automatique du code
- Suivi des sessions KodeKloud
- Alertes si quota quotidien non atteint

### 3️⃣ **Analysis with AI** 🧠
- Pose des questions sur les concepts étudiés
- Gemini génère des réponses contextuelles
- Stocke les Q&A pour révisions futures

### 4️⃣ **Reinforcement** 💪
- Génère des exercices pratiques personnalisés
- Labs hands-on basés sur la progression
- Validation des acquis

### 5️⃣ **Zettelkasten Notes** 📝
- Prise de notes atomiques (méthode Zettelkasten)
- Synchronisation avec Obsidian
- Liens entre concepts

### 6️⃣ **Flashcards Generation** 🃏
- ✅ **[SPRINT 2]** Création automatique de cartes Anki depuis notes Obsidian
- ✅ **[SPRINT 2]** Export compatible avec Anki (format TSV)
- ✅ **[SPRINT 2]** Déduplication par hash SHA256
- Support 3 formats: `Q:/A:`, `Q::/A::`, inline `::`
- Filtrage par tag `#flashcard`

**Usage:**
```bash
skillops create --storage-path storage --vault-path ~/Obsidian --anki-sync-path ~/Anki/sync
```

### 7️⃣ **Portfolio Automation** 🔧
- ✅ **[SPRINT 2]** Détection automatique des projets dans ~/labs/ sans remote
- ✅ **[SPRINT 2]** Génération de README avec badges tech (Python, Node.js, Docker, etc.)
- ✅ **[SPRINT 2]** Création de repo GitHub via API
- ✅ **[SPRINT 2]** Git init, commit, push automatiques
- Tech stack detection (package.json, requirements.txt, Dockerfile, etc.)

**Usage:**
```bash
export GITHUB_TOKEN=ghp_xxxxx
export GITHUB_USERNAME=your_username
skillops share --labs-path ~/labs
```

### 8️⃣ **Daily Reflection & Notifications** 🌅
- ✅ **[SPRINT 2]** Notifications quotidiennes Telegram avec bilans
- ✅ **[SPRINT 2]** Format Markdown avec métriques (steps complétés, temps, streak)
- ✅ **[SPRINT 2]** Respect du planning (envoie à l'heure prévue)
- ✅ **[SPRINT 2]** Alertes si objectifs non atteints

**Usage:**
```bash
export TELEGRAM_BOT_TOKEN=123456:ABC
export TELEGRAM_CHAT_ID=987654321
export TELEGRAM_SCHEDULE_TIME=20:00
skillops notify --storage-path storage --respect-schedule
```

---

## � Feature Documentation

### 🃏 Flashcard Generation (Sprint 2)

Automatically create flashcards from your Obsidian vault:

```bash
# Setup
export OBSIDIAN_VAULT_PATH=~/Obsidian
export ANKI_SYNC_PATH=~/Anki/sync

# Generate flashcards from vault
skillops create --vault-path $OBSIDIAN_VAULT_PATH --anki-sync-path $ANKI_SYNC_PATH
```

**Features:**
- Scans Obsidian vault for notes with `#flashcard` tag
- Supports 3 markdown formats:
  - `Q: question` / `A: answer`
  - `Q:: question` / `A:: answer`
  - Inline `question :: answer`
- Deduplicates by SHA256 hash (no duplicate cards!)
- Exports TSV format compatible with Anki

**Example Obsidian note:**
```markdown
# Learning - Docker Basics

#flashcard

Q: What is a Docker image?
A: A lightweight, standalone, executable package containing code, runtime, and dependencies.

Q: Difference between image and container?
A: Image = blueprint (immutable), Container = running instance (mutable)
```

Result: `skillops-YYYY-MM-DD.txt` in `ANKI_SYNC_PATH` ready for Anki import!

---

### 🚀 GitHub Portfolio Automation (Sprint 2)

Automatically push lab projects to GitHub:

```bash
# Setup
export GITHUB_TOKEN=ghp_xxxxxxxxx         # From https://github.com/settings/tokens
export GITHUB_USERNAME=your_username
export LABS_PATH=~/labs

# Share projects to GitHub
skillops share --labs-path $LABS_PATH
```

**What it does:**
1. Scans `~/labs/` for project directories
2. Detects projects without Git remote
3. Generates professional `README.md` with:
   - Auto-detected tech stack (Python, Node.js, Docker, Go, etc.)
   - Tech badges (shields.io)
   - Installation & usage sections
4. Creates GitHub repository via API
5. Initializes git, commits, and pushes

**Example output:**
```
Found 3 projects
Processing: my-python-cli
  ✓ Generated README.md
  ✓ Initialized git repository
  ✓ Created commit: "Initial commit"
  ✓ Created GitHub repository
  ✓ Pushed to origin
✓ my-python-cli: https://github.com/user/my-python-cli

Processing: node-api-server
✓ node-api-server: https://github.com/user/node-api-server
```

**Auto-detected tech stacks:**
- Python (requirements.txt, setup.py)
- Node.js (package.json)
- Docker (Dockerfile, docker-compose.yml)
- Go (go.mod)
- Terraform (terraform/)
- And more!

---

### 📱 Daily Telegram Notifications (Sprint 2)

Get daily progress summaries via Telegram:

```bash
# Setup
export TELEGRAM_BOT_TOKEN=123456:ABCdef    # From BotFather
export TELEGRAM_CHAT_ID=987654321          # Your chat ID
export TELEGRAM_SCHEDULE_TIME=20:00        # Optional: Send at specific time

# Send notification
skillops notify --storage-path storage --respect-schedule
```

**What you receive:**
```
📊 SkillOps Daily Summary

✓ Steps Completed: 6/8
  ├─ Review Metrics ✓
  ├─ Formation ✓
  ├─ Analysis ✓
  ├─ Reinforce ✓
  └─ Zettelkasten ✓

⏱️ Time Spent: 3h 45m
🔥 Current Streak: 12 days
📈 Total Cards Reviewed: 342

🎯 Goals for Tomorrow:
  • Complete all 8 steps
  • Code for 4+ hours
  • Review 15+ flashcards
```

**Features:**
- Respects schedule (send only at specified time via --respect-schedule)
- Beautiful Markdown formatting
- Includes metrics and streaks
- Can be run via cron/systemd

---

## 🧭 8-Step Workflow (MVP)

### Overview
- **1. Review:** View yesterday’s coding metrics and streak.
- **2. Formation:** Plan today’s study focus using tracked time.
- **3. Anki:** Review flashcards in the desktop app (placeholder in CLI).
- **4. Create:** Generate flashcards from Obsidian notes and export for Anki.
- **5. Read:** Review notes (placeholder guidance in CLI).
- **6. Reinforce:** Practice exercises with timer and progress tracking.
- **7. Share:** Detect local labs, create GitHub repos, generate README, push.
- **8. Reflection:** Journal your day (placeholder guidance in CLI).

### Commands
```bash
# Interactive menu (all 8 steps)
python -m src.lms.main start

# Run specific steps
python -m src.lms.main review
python -m src.lms.main formation
python -m src.lms.main reinforce
python -m src.lms.main create --vault-path ~/Obsidian --anki-sync-path ~/Anki/sync
python -m src.lms.main share --labs-path ~/labs
python -m src.lms.main notify --respect-schedule
```

### GitHub Token Scopes (for Share step)
- **Classic token:** `repo` (full control of private/public repos)
- **Fine-grained token (recommended):** Repository permissions
  - **Contents:** Read & Write
  - **Metadata:** Read-only

> Fine-grained tokens limit scope to selected repositories and are more secure.

## 🔧 Configuration

All configuration uses environment variables (see `.env.example`):

```bash
# Required
WAKATIME_API_KEY=waka_xxxxxxxxxxxxx

# Optional - Telegram Notifications
TELEGRAM_BOT_TOKEN=123456:ABCdefG
TELEGRAM_CHAT_ID=987654321
TELEGRAM_SCHEDULE_TIME=20:00

# Optional - Flashcard Generation
OBSIDIAN_VAULT_PATH=~/Obsidian
ANKI_SYNC_PATH=~/Anki/sync

# Optional - GitHub Portfolio
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxx
GITHUB_USERNAME=your_username
LABS_PATH=~/labs
```

To get these tokens:
- **WakaTime**: https://wakatime.com/settings/account
- **Telegram**: Message @BotFather on Telegram
- **GitHub (classic):** https://github.com/settings/tokens (scope: `repo`)
- **GitHub (fine-grained recommended):** https://github.com/settings/tokens?type=beta
  - Repository permissions → Contents (Read & Write), Metadata (Read)

---

| Catégorie | Technologies |
|-----------|-------------|
| **Langage** | Python 3.11+ |
| **CLI Framework** | Typer, Rich, Inquirer |
| **APIs** | Google Gemini, WakaTime, GitHub REST API, Telegram Bot API |
| **Persistence** | JSON, YAML, CSV |
| **Testing** | Pytest, Coverage, Mock |
| **CI/CD** | GitHub Actions |
| **Containerisation** | Docker (prévu) |
| **Documentation** | Markdown, Mermaid diagrams |

---

## 🚀 Installation (Prévu)

### Prérequis

- **Python 3.11+** (vérifier avec `python --version`)
- **Git** pour cloner le repository
- **pip** pour gérer les dépendances

### Installation Rapide

```bash
# 1. Cloner le repository
git clone https://github.com/M-Boiguille/SkillOps.git
cd SkillOps

# 2. Créer un environnement virtuel (recommandé)
python -m venv .venv

# 3. Activer l'environnement virtuel
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Configuration des API keys (REQUIS)
cp .env.example .env
# Éditer .env et configurer au minimum :
#   - WAKATIME_API_KEY (https://wakatime.com/settings/account)

# 6. Vérifier l'installation
python -m pytest tests/ -v

# 7. Lancer le CLI
python src/lms/main.py start
```

### 🔑 Configuration des API Keys

**WakaTime (Obligatoire pour l'étape Formation)**

1. Créer un compte sur [WakaTime](https://wakatime.com)
2. Aller dans [Settings → Account](https://wakatime.com/settings/account)
3. Copier votre "Secret API Key"
4. Ajouter dans `.env` :
   ```bash
   WAKATIME_API_KEY=waka_XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
   ```

**Autres APIs (Optionnelles - Prévues Sprint 2+)**
- **Gemini AI** : Pour génération de questions/réponses contextuelles
- **GitHub Token** : Pour automatisation du portfolio
- **Telegram Bot** : Pour notifications quotidiennes

Voir `.env.example` pour la liste complète.

### Structure du Projet

```
SkillOps/
├── src/
│   └── lms/                  # Package principal
│       ├── __init__.py
│       ├── main.py           # Point d'entrée CLI
│       └── persistence.py    # Gestion état & métriques
├── tests/
│   └── lms/                  # Tests unitaires
│       ├── metrics_manager_test.py
│       └── ...
├── storage/                  # Données locales (gitignored)
│   ├── .state.yaml          # État actuel
│   ├── .progress.json       # Historique
│   └── .metrics.json        # Métriques agrégées
├── project-lifecycle/        # Documentation projet
│   ├── 01-product-discovery.md
│   ├── 02-urd-user-requirements.md
│   ├── 03-adr-architecture-decisions.md
│   └── 04-sprint-planning-sprint-1.md
├── requirements.txt          # Dépendances Python
├── pyproject.toml           # Configuration projet
└── README.md                # Documentation principale
```

### Dépendances Principales

| Package | Version | Usage |
|---------|---------|-------|
| **typer** | 0.21.1 | Framework CLI avec type hints |
| **rich** | 14.2.0 | UI terminal (couleurs, tableaux) |
| **inquirer** | 3.4.0 | Menus interactifs |
| **pytest** | 9.0.2 | Framework de tests |
| **pytest-cov** | 7.0.0 | Coverage des tests |
| **PyYAML** | 6.0.3 | Parsing YAML (état) |

Voir [requirements.txt](requirements.txt) pour la liste complète.

### Configuration des API Keys (Optionnel)

Pour utiliser les intégrations API complètes :

```bash
# Créer un fichier .env à la racine
cat > .env << EOF
WAKATIME_API_KEY=waka_xxxxxxxxxxxxx
GEMINI_API_KEY=AIzaxxxxxxxxxxxxxxx
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxx
TELEGRAM_BOT_TOKEN=123456:ABCdef
TELEGRAM_CHAT_ID=123456789
# Optional: HH:MM for scheduled send (used with cron/systemd)
# TELEGRAM_SCHEDULE_TIME=20:00
EOF

# Le fichier .env est automatiquement gitignored
```

**Note :** Le CLI fonctionne sans ces clés (mode offline pour développement).

### Développement

```bash
# Installer avec dépendances de dev
pip install -r requirements.txt

# Configurer pre-commit hooks (recommandé)
pip install pre-commit
pre-commit install

# Lancer les tests avec couverture
pytest tests/ --cov=src/lms --cov-report=term-missing

# Vérifier le code (linting)
black src/ tests/           # Formatage
mypy src/                   # Type checking
flake8 src/ tests/          # Linting

# Lancer les pre-commit hooks manuellement
pre-commit run --all-files

# Lancer le CLI en mode debug
python src/lms/main.py --help
```

#### Pre-commit Hooks

Le projet utilise des hooks pre-commit pour garantir la qualité du code :

- **trailing-whitespace** : Supprime les espaces en fin de ligne
- **end-of-file-fixer** : Ajoute une ligne vide en fin de fichier
- **check-yaml** : Valide la syntaxe YAML
- **check-toml** : Valide la syntaxe TOML
- **black** : Formatage automatique du code Python
- **flake8** : Vérification du style de code (PEP 8)
- **mypy** : Vérification des types statiques

Les hooks s'exécutent automatiquement à chaque commit. Pour forcer l'exécution manuelle :

```bash
pre-commit run --all-files
```

---

## 📋 Workflow Quotidien

```bash
# Démarrer la routine du matin (7h00)
skillops start

# Commande affiche :
┌─────────────────────────────────────────┐
│  SkillOps - Routine du 9 janvier 2026  │
├─────────────────────────────────────────┤
│ 📊 Métriques d'hier :                   │
│   ✅ 8/8 étapes complétées              │
│   ⏱️  3h42 codé (WakaTime)              │
│   🔥 Streak : 18 jours                  │
├─────────────────────────────────────────┤
│ 🎯 Programme aujourd'hui :              │
│   1. [●○○○○○○○] Review Metrics          │
│   2. [○○○○○○○○] Formation               │
│   ...                                   │
└─────────────────────────────────────────┘

# Navigation interactive (flèches ↑↓ ou touches vim j/k)
> Appuyez sur Entrée pour Step 1: Review Metrics

# Notification Telegram automatique en fin de journée
📱 "✅ Bilan : 8/8 étapes | 4h12 codé | 15 cartes créées"

### Envoyer manuellement depuis le CLI

```bash
python -m src.lms.main notify --storage-path storage --respect-schedule
```

Pour un envoi immédiat sans vérifier l'heure planifiée, supprimez `--respect-schedule`.
```

---

## 🎓 Apprentissage DevOps Démontré

Ce projet illustre ma maîtrise des concepts DevOps suivants :

### 🔹 Product Management
- ✅ Product Discovery (voir [Product-Discovery-Session.md](Product-Discovery-Session.md))
- ✅ Priorisation MoSCoW (MVP vs Nice-to-have)
- ✅ User Stories avec Acceptance Criteria
- ✅ OKRs et métriques de succès

### 🔹 Architecture & Design
- ✅ State Machine Pattern
- ✅ API Client abstraction
- ✅ Event-driven architecture
- ✅ Separation of Concerns

### 🔹 DevOps Practices
- ✅ Configuration as Code (YAML)
- ✅ Secrets Management (environment variables)
- ✅ Logging structuré (JSON)
- ✅ CI/CD Pipeline (GitHub Actions - prévu)
- ✅ Containerisation (Docker - prévu)

### 🔹 Observabilité
- ✅ Logs structurés
- ✅ Métriques personnalisées
- ✅ Alerting (Telegram)
- ✅ Dashboard de progression

### 🔹 Automatisation
- ✅ Cron jobs pour exécution planifiée
- ✅ Webhooks GitHub
- ✅ Bot Telegram
- ✅ Génération automatique de contenu (flashcards, README)

---

## 📊 Roadmap

### ✅ Phase 1 : Conception (En cours)
- [ ] Product Discovery Session
- [ ] Documentation technique
- [ ] Définition des besoins et priorisation

### 🚧 Phase 2 : MVP Core (En attente)
- [ ] Machine à états pour orchestration
- [ ] Interface CLI interactive
- [ ] Système de persistence des données
- [ ] Tests de base

### 📅 Phase 3 : Intégrations Externes (En attente)
- [ ] API de tracking de code
- [ ] Intelligence artificielle pour Q&A
- [ ] Automatisation portfolio
- [ ] Notifications temps réel
- [ ] Tests d'intégration

### 📅 Phase 4 : DevOps Pipeline (En attente)
- [ ] Automatisation CI/CD
- [ ] Containerisation
- [ ] Observabilité (logs, métriques, alertes)
- [ ] Documentation complète

### 🔮 Phase 5 : Optimisations (En attente)
- [ ] Interface web de visualisation
- [ ] Synchronisation multi-device
- [ ] Extensions et plugins
- [ ] Ouverture communautaire

---

## 🤝 Contribution

Ce projet est actuellement un outil d'apprentissage personnel, mais les suggestions sont les bienvenues !

Si vous souhaitez :
- 💡 Proposer une amélioration
- 🐛 Signaler un bug
- 📖 Améliorer la documentation
- 🔀 Soumettre une Pull Request

N'hésitez pas à ouvrir une **Issue** sur GitHub.

---

## 📚 Ressources & Inspirations

### Méthodologies Appliquées
- **Product Discovery** : "Inspired" - Marty Cagan
- **DevOps** : "The Phoenix Project", "Accelerate"
- **Learning** : "Make It Stick", méthode Zettelkasten, Deep Work
- **Architecture** : C4 Model, Event Storming

---

## 📄 Licence

MIT License - Voir [LICENSE](LICENSE) pour plus de détails.

---

## ⭐ Pourquoi ce Projet ?

> *"La meilleure façon d'apprendre DevOps, c'est de l'appliquer à un problème réel. SkillOps est né de ma frustration à gérer manuellement ma routine d'apprentissage. Plutôt que d'utiliser 10 outils différents, j'ai construit un système qui les orchestre tous."*

Ce projet démontre que je ne me contente pas d'apprendre des outils en isolation, mais que je comprends :
- 🎯 **Le cycle de vie produit** (discovery, MVP, itération)
- 🏗️ **L'architecture distribuée** (APIs, état, persistence)
- 🔒 **La sécurité** (secrets, encryption, least privilege)
- 📊 **L'observabilité** (logs, métriques, alerting)
- ♻️ **L'automatisation** (CI/CD, cron, webhooks)

**SkillOps n'est pas juste un projet d'apprentissage, c'est un outil que j'utilise quotidiennement pour devenir DevOps Engineer.**

---

<div align="center">

**⭐ Si ce projet vous inspire, n'hésitez pas à le star !**

</div>
