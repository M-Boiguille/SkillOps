# SkillOps 🚀

> **An intelligent Learning Management System (LMS) CLI for orchestrating DevOps self-learning with AI, automatic tracking, and notifications.**

[![CI](https://github.com/M-Boiguille/SkillOps/actions/workflows/ci.yml/badge.svg)](https://github.com/M-Boiguille/SkillOps/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/M-Boiguille/SkillOps/branch/main/graph/badge.svg)](https://codecov.io/gh/M-Boiguille/SkillOps)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![DevOps](https://img.shields.io/badge/Focus-DevOps%20Learning-orange.svg)]()
[![Tests](https://img.shields.io/badge/Tests-passing-brightgreen.svg)]()

---

## 📖 Overview

**SkillOps** is an automated learning management system designed to optimize daily DevOps training routines. Rather than manually managing tracking, notes, and revisions across 10 different tools, I built a CLI tool that intelligently orchestrates 9 learning steps using a state machine.

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

## ✅ Current Workflow (9 steps)

1. **Daily Stand-up** — metrics & streak recap
2. **Read** — articles and knowledge capture
3. **Tutor** — AI Q&A and concept reinforcement
4. **Reinforce** — practice exercises
5. **Create** — flashcard generation from Obsidian
6. **Flashcards** — Anki review workflow
7. **Mission Control** — tickets/incidents with validation
8. **Pull Request** — portfolio automation (GitHub)
9. **Reflection** — daily journal & wrap-up

---

## ✅ Current Status: Production-Ready (Local)

**Fully Production-Ready Features:**
- ✅ Interactive 9-step workflow with **learning/engineering modes**
- ✅ WakaTime metrics + SQLite tracking with schema v4 migrations
- ✅ Obsidian/Anki flashcard pipeline
- ✅ GitHub portfolio automation
- ✅ Telegram notifications + health/doctor checks
- ✅ **Chaos Monkey (local)**: `skillops chaos` with levels 1–3
- ✅ **🤖 AI-Powered On-Call**: `skillops oncall` with adaptive incidents, progressive hints, validation, retry with exponential backoff, and spaced repetition (Anki-style)
- ✅ **Post-Mortem documentation**: `skillops post-mortem` for incident analysis
- ✅ **Secrets Management**: OS keyring support with `skillops secret-set/unset`
- ✅ **Observability**: `skillops metrics --hours 24` for real-time stats + structured logging
- ✅ **Data Retention**: Automatic cleanup of performance metrics/chaos events with `skillops retention --days 30`
- ✅ **Database Hardening**: WAL mode, 5s busy timeout, foreign keys, consistency checks
- ✅ **Reproducible Installs**: `requirements-lock.txt` with all pinned versions

**Planned (not implemented yet):**
- `skillops review` (AI code review + guardrails)

---

## 🧭 Future Action Plan (no dates)

1. **Adopt the workflow daily** and collect friction points.
2. **Harden self-healing** around Chaos (alerts, retries, readiness checks).
3. **Practice On-Call workflow** with generated incidents + post-mortems.
4. **Add Code Review gate** (`skillops review`) for diffs/secrets/quality.
5. **Build reference labs** in ~/labs with full observability stacks.
6. **Expand observability** (metrics dashboards + failure signals).
7. **Evolve architecture** toward services (API + background workers).

## 🚀 Quickstart

### Option 1: Development Install (with dev tools)
```bash
git clone https://github.com/M-Boiguille/SkillOps.git
cd SkillOps
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install with dev dependencies (recommended for local use)
pip install -e .[dev]

# Or use the reproducible lockfile for exact versions:
pip install -r requirements-lock.txt
```

### Option 2: Production Install (locked dependencies)
```bash
git clone https://github.com/M-Boiguille/SkillOps.git
cd SkillOps
python -m venv .venv
source .venv/bin/activate

# Install exact locked versions for reproducibility
pip install -r requirements-lock.txt
```

### Configure and Verify
```bash
# Setup secrets with OS keyring (recommended)
export SKILLOPS_USE_KEYRING=true
skillops secret-set GEMINI_API_KEY  # Interactive prompt, stored securely
skillops secret-set WAKATIME_API_KEY

# Or use .env file (local only, keep private)
cp .env.example .env
# Edit .env and add your API keys
chmod 600 .env

# Verify installation
skillops doctor  # Full system check
pytest -v tests/smoke  # Smoke tests
```

### Start Learning
```bash
skillops start  # Interactive 9-step workflow
```

> **First time?** See [LOCAL_SETUP.md](docs/LOCAL_SETUP.md) for detailed local installation guide.

---

## 📚 Book Processing Pipeline (Gemini Batch)

Répertoire attendu :
- `books/pending/` → PDF à traiter
- `books/processing/` → jobs en cours (manifest)
- `books/completed/` → résultats JSONL téléchargés
- `books/books-manifest.yaml` → état global

Commandes principales :

```bash
skillops check-books
skillops submit-books --api-key "$GEMINI_API_KEY"
skillops fetch-books --book networking-fundamentals
skillops import-books --vault ~/Obsidian --book networking-fundamentals
skillops process-pipeline --watch --interval 15
```

---

## 🧪 Tests

```bash
source .venv/bin/activate
python -m pytest -v
```

---

## 📚 Documentation

**Getting Started:**
- [**LOCAL_SETUP.md**](docs/LOCAL_SETUP.md) ← **Start here!** Complete local installation guide
- [QUICKSTART.md](docs/QUICKSTART.md) — Quick 5-minute walkthrough

**Operations & Production:**
- [DEPLOYMENT.md](docs/DEPLOYMENT.md) — Local deployment, backups, rollback procedures
- [OPERATIONS.md](docs/OPERATIONS.md) — Daily operations, metrics, retention, automation
- [SECURITY.md](docs/SECURITY.md) — Secrets management, API key rotation, incident response

**Features & Workflow:**
- [FEATURES.md](docs/FEATURES.md) — Detailed feature descriptions
- [CHAOS.md](docs/CHAOS.md) — Chaos Monkey testing and observability

**Advanced:**
- [OBSERVABILITY.md](docs/OBSERVABILITY.md) — Metrics, logging, monitoring
- [RUNBOOKS.md](docs/RUNBOOKS.md) — Common procedures and troubleshooting
- [GOVERNANCE.md](docs/GOVERNANCE.md) — Project governance and contribution guidelines

---

## 🔔 Daily Telegram Notifications

```bash
export TELEGRAM_BOT_TOKEN=123456:ABC
export TELEGRAM_CHAT_ID=987654321
export TELEGRAM_SCHEDULE_TIME=20:00
skillops notify --storage-path storage --respect-schedule
```

---

## 🧭 9-Step Workflow

### Overview
- **1. Daily Stand-up:** View yesterday’s coding metrics and streak.
- **2. Read:** Capture articles and notes.
- **3. Tutor:** AI Q&A and concept reinforcement.
- **4. Reinforce:** Practice exercises.
- **5. Create:** Generate flashcards from Obsidian notes and export for Anki.
- **6. Flashcards:** Review due cards via AnkiConnect.
- **7. Mission Control:** Solve tickets and incidents with acceptance criteria.
- **8. Pull Request:** Detect local labs, create GitHub repos, generate README, push.
- **9. Reflection:** Journal your day and wrap up.

### Commands
```bash
# Interactive menu (all 9 steps)
skillops start

# Learning mode (morning: steps 1-3)
skillops start --mode=learning

# Engineering mode (afternoon: steps 4-9)
skillops start --mode=engineering

# Run specific steps
skillops create --vault-path ~/Obsidian --anki-sync-path ~/Anki/sync
skillops share --labs-path ~/labs
skillops notify --respect-schedule
```

### GitHub Token Scopes (for Pull Request step)
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
| **Persistence** | SQLite (primary) + JSON/CSV export |
| **Testing** | Pytest, Coverage, Mock |
| **CI/CD** | GitHub Actions |
| **Containerisation** | Docker (optionnel) |
| **Documentation** | Markdown, Mermaid diagrams |

---

## 🚀 Installation

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
pip install -e .[dev]

# 5. Configuration des API keys (optionnel)
cp .env.example .env
# Éditer .env selon les intégrations utilisées

# 6. Vérifier l'installation
pytest -v

# 7. Lancer le CLI
skillops start
```

### 🔑 Configuration des API Keys

**WakaTime (Optionnel, pour les métriques de code)**

1. Créer un compte sur [WakaTime](https://wakatime.com)
2. Aller dans [Settings → Account](https://wakatime.com/settings/account)
3. Copier votre "Secret API Key"
4. Ajouter dans `.env` :
   ```bash
   WAKATIME_API_KEY=waka_XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
   ```

**Autres APIs (Optionnelles)**
- **Gemini AI** : Pour génération de questions/réponses contextuelles
- **GitHub Token** : Pour automatisation du portfolio
- **Telegram Bot** : Pour notifications quotidiennes

Voir `.env.example` pour la liste complète.

### Structure du Projet

Voir [STRUCTURE.md](STRUCTURE.md) pour le détail de l’arborescence.

### Dépendances Principales

| Package | Version | Usage |
|---------|---------|-------|
| **typer** | 0.21.1 | Framework CLI avec type hints |
| **rich** | 14.2.0 | UI terminal (couleurs, tableaux) |
| **inquirer** | 3.4.0 | Menus interactifs |
| **pytest** | 9.0.2 | Framework de tests |
| **pytest-cov** | 7.0.0 | Coverage des tests |
| **PyYAML** | 6.0.3 | Parsing YAML (catalogs/configs) |

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

## � CLI Usage Guide

### Quick Start - Start the Daily Learning Workflow

```bash
skillops start
```

**What happens:**
- Interactive menu appears with 9 learning steps
- Navigate with ↑↓ arrows (or j/k for vim users)
- Select a step and execute its workflow
- After completion, return to menu for next step
- Press Ctrl+C to exit

### All Available Commands

#### `skillops start` - Main Interactive Menu
```bash
# Start with default settings
skillops start

# Enable debug logging for troubleshooting
skillops start --verbose

# Enable monitoring (metrics + alerts)
skillops start --enable-monitoring
```

**Navigation Tips:**
- **↑↓ arrows** or **j/k** to move between steps
- **Enter** to execute selected step
- **Ctrl+C** to exit menu
- Each step displays emoji and completion status

#### `skillops setup` - Initial Configuration
```bash
# Interactive setup wizard
skillops setup

# Create/switch profiles
skillops setup --profile profile-name
```

**Configuration includes:**
- API key setup (WakaTime, Gemini, GitHub, Telegram)
- Storage location
- Notification preferences
- Learning goals

#### `skillops doctor` - Preflight Diagnostics
```bash
# Check environment and configuration
skillops doctor

# Optional legacy health check
skillops health
```

**Validates:**
- ✓ Configuration files (.env)
- ✓ API connections (all external services)
- ✓ File storage access
- ✓ Required dependencies

#### `skillops export` - Backup Your Progress
```bash
# Export to JSON (complete backup)
skillops export --format json --output backup.json

# Export to CSV (for Excel analysis)
skillops export --format csv --output ./exports/

# Short form
skillops export -f json -o ~/backups/$(date +%Y%m%d).json
```

**Output formats:**
- **JSON**: Single file with metadata + all progress history
- **CSV**: Flat table (date, steps, time, cards per row)

#### `skillops import-data` - Restore Progress
```bash
# Import from JSON file
skillops import-data backup.json

# Import from CSV file
skillops import-data progress.csv

# Merge with existing data instead of replacing
skillops import-data backup.json --merge

# Import without auto-backup
skillops import-data backup.json --no-backup
```

**Import features:**
- Automatic backup created before import (unless --no-backup)
- Merge mode combines with existing data
- Replace mode overwrites existing

#### Legacy JSON/YAML Migration (Optional)
If you have old JSON/YAML files from previous versions, use the CLI migration command:

```bash
skillops migrate
```

It migrates legacy files like `.progress.json`, `formation_log.json`, and `reinforce_progress.json` into `storage/skillops.db`.

#### `skillops doctor` - Preflight Checks
```bash
skillops doctor
```

**Doctor checks:**
- Environment variables (API keys, vault paths)
- SQLite connectivity and storage write access
- Optional Gemini dependency availability

#### `skillops notify` - Send Telegram Summary
```bash
# Send daily summary notification
skillops notify --storage-path storage

# Respect schedule time from .env
skillops notify --storage-path storage --respect-schedule

# With debug output
skillops notify --storage-path storage --verbose
```

**Notification includes:**
- Total steps completed
- Time spent coding
- Current streak
- Flashcards reviewed
- Tomorrow's goals

#### `skillops version` - Check Version
```bash
skillops version
```

### Step-by-Step Workflow Descriptions

See the full step documentation in [docs/FEATURES.md](docs/FEATURES.md).

### Configuration & Environment Variables

**Configuration (.env file):**
```bash
# Optional - Metrics
WAKATIME_API_KEY=waka_xxxxxxxxxxxxx

# Optional - AI
GEMINI_API_KEY=AIzaxxxxxxxxxxxxxxx

# Optional - Portfolio
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxx
GITHUB_USERNAME=your_username

# Optional - Notifications
TELEGRAM_BOT_TOKEN=123456:ABCdef
TELEGRAM_CHAT_ID=987654321
TELEGRAM_SCHEDULE_TIME=20:00

# Optional - Integrations
OBSIDIAN_VAULT_PATH=~/Obsidian
ANKI_SYNC_PATH=~/Anki/sync
LABS_PATH=~/labs
```

**Getting Tokens:**
- **WakaTime**: https://wakatime.com/settings/account
- **Gemini AI**: https://aistudio.google.com/apikey
- **GitHub**: https://github.com/settings/tokens (scope: repo)
- **Telegram**: Message @BotFather, `/start`, `/newbot`

### Keyboard Shortcuts in Menu

| Key | Action |
|-----|--------|
| ↑ | Move up |
| ↓ | Move down |
| j | Move down (vim) |
| k | Move up (vim) |
| Enter | Execute step |
| Ctrl+C | Exit |
| Tab | Quick navigation |

### Examples: Common Use Cases

**Daily morning routine:**
```bash
# Start workflow for today
skillops start
```

**Minimal local preflight (recommended):**
```bash
skillops doctor
pytest -v tests/smoke
bash setup/backup/backup.sh
bash setup/backup/restore.sh ~/.local/share/skillops/backups/skillops_YYYYmmdd_HHMMSS.db
```

**Weekly backup:**
```bash
# Create a SQLite backup
bash setup/backup/backup.sh
```

**Monday recovery (restore from backup):**
```bash
# Restore if something went wrong
bash setup/backup/restore.sh ~/.local/share/skillops/backups/skillops_YYYYmmdd_HHMMSS.db
```

See the operations guide: [docs/OPERATIONS.md](docs/OPERATIONS.md)

**Automate daily notifications (cron):**
```bash
# In crontab -e:
0 20 * * * cd /path/to/SkillOps && skillops notify --storage-path storage --respect-schedule
```

**Check system health before starting:**
```bash
skillops doctor && skillops start
```

---



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
- ✅ CI/CD Pipeline (GitHub Actions)
- ✅ Containerisation (Docker, optionnel)

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

---

Voir la roadmap détaillée dans [project-lifecycle/](project-lifecycle/).
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
