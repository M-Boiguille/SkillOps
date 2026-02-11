# SkillOps Features Guide

Complete documentation of all SkillOps features and commands.

## Table of Contents

1. [Interactive Workflow (9 steps)](#interactive-workflow-9-steps)
2. [Core Commands](#core-commands)
3. [Daily Stand-up (Review Metrics)](#daily-stand-up-review-metrics)
4. [Formation Tracking (WakaTime)](#formation-tracking-wakatime)
5. [Tutor (AI Analysis)](#tutor-ai-analysis)
6. [Reinforce (Practice)](#reinforce-practice)
7. [Read & Notes (Zettelkasten)](#read--notes-zettelkasten)
8. [Create (Flashcard Generation)](#create-flashcard-generation)
9. [Flashcards (Anki Review)](#flashcards-anki-review)
10. [Mission Control](#mission-control)
11. [Pull Request (Portfolio Automation)](#pull-request-portfolio-automation)
12. [Reflection & Notifications](#reflection--notifications)
13. [Health & Doctor Checks](#health--doctor-checks)
14. [Advanced Usage](#advanced-usage)

---

## Interactive Workflow (9 steps)

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

## Core Commands

### Getting Help

```bash
# Show all available commands
skillops --help

# Get help for specific command
skillops start --help
skillops share --help
skillops notify --help
skillops export --help
skillops import-data --help
skillops doctor --help
skillops migrate --help
```

### Verbose Output

```bash
# Enable detailed logging for troubleshooting
skillops share --storage-path ./storage --verbose
skillops notify --storage-path ./storage --verbose
```

### Version

```bash
# Display SkillOps version
skillops version
```

### Doctor (Preflight Checks)

```bash
skillops doctor
```

### Migration (Legacy JSON → SQLite)

```bash
skillops migrate
```
```

---

## Daily Stand-up (Review Metrics)

**Purpose:** Review yesterday's learning metrics and progress.

**Command (interactive):**
```bash
skillops start
```

**Output:**
```
📊 Learning Metrics Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Date: 2026-01-11
Time Coded: 3h 42m
Steps Completed: 7/9
Current Streak: 5 days
Average Streak: 3.2 days
Total Learning Hours: 142h
Weekly Average: 20.3h
```

**Data Stored:**
- SQLite summary in `storage/skillops.db`
- Exportable via `skillops export` (JSON/CSV)

**Use Cases:**
- Morning routine: Review what you achieved yesterday
- Motivation tracking: Monitor your streak and consistency
- Planning: Understand which topics need more time

---

## Formation Tracking (WakaTime)

**Purpose:** Track time spent on learning and coding.

**Command (interactive):**
```bash
skillops start
```

**Data Source:**
- WakaTime API integration (requires `WAKATIME_API_KEY`)
- Manual entry option (when API unavailable)

**Output:**
```
⏱️  Formation Tracking
━━━━━━━━━━━━━━━━━━━━━━━━━━
Today's Coding Time: 4h 15m
Languages: Python (60%), Bash (30%), YAML (10%)
Top Projects: SkillOps, DevOps-Labs
Daily Goal: 4h ✅ EXCEEDED
```

**Features:**
- Automatic sync with WakaTime
- Language breakdown
- Project-level tracking
- Daily goal alerts

---

## Tutor (AI Analysis)

**Purpose:** Get AI-generated questions and answers on study topics.

**Command (interactive):**
```bash
skillops start
```

**Requirements:**
- `GEMINI_API_KEY` environment variable

**Example:**
```bash
skillops analysis \
  --storage-path ./storage \
  --topic "Kubernetes networking"
```

**Output:**
```
🧠 AI Analysis Results
━━━━━━━━━━━━━━━━━━━━━━━━━━
Q: What is the difference between ClusterIP and NodePort services?
A: ClusterIP services are only accessible within the cluster through an internal IP...

Q: How does DNS resolution work in Kubernetes pods?
A: Each pod gets a /etc/resolv.conf that points to the cluster DNS server...
```

**Features:**
- Context-aware questions (based on your progress)
- Deep-dive explanations
- Related topics suggestions
- Historical Q&A tracking

---

## Reinforce (Practice)

**Purpose:** Generate personalized practice exercises.

**Command:**
```bash
skillops reinforce --storage-path <path>
```

**Output:**
```
💪 Reinforcement Exercises
━━━━━━━━━━━━━━━━━━━━━━━━━━
Exercise 1: Docker Networking
  Create a custom Docker network with 3 containers
  Time: 30 minutes | Difficulty: ⭐⭐⭐

Exercise 2: Kubernetes Ingress
  Set up an Ingress controller for your services
  Time: 45 minutes | Difficulty: ⭐⭐⭐⭐
```

**Features:**
- Difficulty progression
- Time estimates
- Step-by-step guidance
- Auto-adjusting difficulty based on performance

---

## Read & Notes (Zettelkasten)

**Purpose:** Capture learning notes in atomic, interconnected format.

**Command:**
```bash
skillops zettel --storage-path <path> --note <note-text>
```

**Example:**
```bash
skillops zettel \
  --storage-path ./storage \
  --note "Docker uses namespaces to isolate processes. Related: cgroups, seccomp"
```

**Features:**
- Automatic timestamp and unique ID
- Backlink support (link to other notes)
- Full-text search
- Export to Obsidian

---

## Create (Flashcard Generation)

**Purpose:** Automatically generate Anki flashcards from Obsidian vault.

**Status:** ✅ Sprint 2 - Fully Implemented

### Overview

Extract flashcard content from your Obsidian vault and generate Anki-compatible decks. Supports multiple markdown formats with automatic deduplication.

### Command

```bash
skillops create \
  --storage-path <path> \
  --vault-path <obsidian-vault> \
  --anki-sync-path <anki-sync-dir>
```

### Required Arguments

- `--storage-path`: SkillOps storage directory (e.g., `./storage`)
- `--vault-path`: Path to Obsidian vault (e.g., `~/Obsidian`)
- `--anki-sync-path`: Anki sync directory (e.g., `~/Anki/sync`)

### Supported Formats

#### Format 1: Q:/A:
```markdown
Q: What is a Docker container?
A: A lightweight virtualized environment with isolated filesystem...

Q: What are Docker layers?
A: Layers are stacked read-only filesystems...
```

#### Format 2: Q::/A:: (with markdown)
```markdown
Q:: What does `docker run -v` do?
A:: Mount volumes:
- `-v /host:/container` - Bind mount
- `-v name:/container` - Named volume
```

#### Format 3: Inline ::
```markdown
What is a namespace?:: A namespace provides process isolation in Docker
```

### File Organization

In Obsidian, organize flashcards with tags:

```markdown
# My Flashcard Notes

#flashcard

Q: What is containerization?
A: Process of packaging applications with dependencies...

Q: Name 5 docker commands
A: run, exec, logs, inspect, ps
```

### Output

The feature generates:
1. **Anki TSV file** (`~/Anki/sync/deck.tsv`):
   ```
   What is a Docker container?	A lightweight virtualized...
   What are Docker layers?	Layers are stacked...
   ```

2. **Progress tracking** (SQLite in `storage/skillops.db`):
  - Records a `card_creations` entry (count, source, timestamp)
  - Exportable via `skillops export` (JSON/CSV)

### Features

- **Multiple Format Support**: Q:/A:, Q::/A::, inline ::
- **Tag Filtering**: Only processes notes tagged with `#flashcard`
- **Automatic Deduplication**: SHA256 hashing prevents duplicates
- **Markdown Support**: Preserve formatting in Anki (lists, bold, code)
- **Batch Operations**: Process entire vault in one command
- **Idempotent**: Safe to run multiple times

### Example Workflow

```bash
# 1. Create some flashcards in Obsidian
# - Add notes with Q:/A: format
# - Tag with #flashcard
# - Save

# 2. Run the create command
skillops create \
  --storage-path ./storage \
  --vault-path ~/Obsidian \
  --anki-sync-path ~/Anki/sync

# Output:
# ✓ Scanning vault: ~/Obsidian
# ✓ Found 47 flashcard questions
# ✓ No duplicates (dedup check passed)
# ✓ Generated Anki deck: 47 cards
# ✓ Saved to: ~/Anki/sync/deck.tsv
```

### Integration with Anki

After running `skillops create`:

1. Open Anki
2. Tools → Add-ons → AnkiConnect (install if needed)
3. Create new deck or select existing
4. File → Import → Select TSV from `~/Anki/sync/`
5. Cards appear in your deck

### Configuration

Environment variables (in `.env`):
```bash
OBSIDIAN_VAULT_PATH=~/Obsidian
ANKI_SYNC_PATH=~/Anki/sync
```

---

## Flashcards (Anki Review)

**Purpose:** Review due cards and optionally sync via AnkiConnect.

**Command (interactive):**
```bash
skillops start
```

Select **Flashcards** in the menu.

**Configuration:**
```bash
ANKI_CONNECT_URL=http://localhost:8765
ANKI_AUTO_SYNC=true
```

---

## Mission Control

**Purpose:** Work on ticket-like missions with context, objectives, and validation hints.

**Command (interactive):**
```bash
skillops start
```

Select **Mission Control** in the menu.

**Data sources:**
- `src/lms/data/companies.yaml`
- `src/lms/data/missions/`

---

## Pull Request (Portfolio Automation)

**Purpose:** Automatically create GitHub repositories for your projects with generated READMEs.

**Status:** ✅ Sprint 2 - Fully Implemented

### Overview

Scan a directory for projects, automatically detect tech stack, generate professional READMEs with tech badges, and push to GitHub with zero manual steps.

### Command

```bash
skillops share \
  --storage-path <path> \
  --labs-path <projects-directory> \
  --github-token <token> \
  --github-username <username>
```

### Required Arguments

- `--storage-path`: SkillOps storage directory
- `--labs-path`: Directory containing projects (e.g., `~/labs/`)
- `--github-token`: GitHub personal access token
- `--github-username`: Your GitHub username

### Environment Variables (Alternative)

Instead of CLI args, use `.env`:
```bash
LABS_PATH=~/labs
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
GITHUB_USERNAME=your_username
```

Then simply run:
```bash
skillops share --storage-path ./storage
```

### How It Works

#### Step 1: Project Detection

Scans `~/labs/` for directories that:
- Are not already git repositories
- Contain code files (*.py, *.js, *.go, etc.)

```
~/labs/
├── k8s-playground/          ← Project 1
│   ├── deployment.yaml
│   └── service.yaml
├── python-cli-tool/         ← Project 2
│   ├── main.py
│   ├── requirements.txt
│   └── tests/
└── terraform-aws/           ← Project 3
    ├── main.tf
    └── variables.tf
```

#### Step 2: Tech Stack Detection

Automatically identifies technologies:

| File/Dir | Technology |
|----------|------------|
| package.json | Node.js |
| requirements.txt | Python |
| Dockerfile | Docker |
| main.tf | Terraform |
| go.mod | Go |
| Gemfile | Ruby |

#### Step 3: README Generation

Creates professional README with:
- Project description (first 200 chars of directory analysis)
- Tech badges (shields.io)
- Installation instructions (auto-generated per tech stack)
- Getting started guide
- Features list

**Generated README example:**
```markdown
# k8s-playground

Kubernetes learning project with deployment examples and service manifests.

## Tech Stack

![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Installation

1. Install Kubernetes cluster:
   ```bash
   minikube start
   ```

2. Apply manifests:
   ```bash
   kubectl apply -f .
   ```

## Features

- Multi-tier application deployment
- Service routing configuration
- Health checks and rolling updates

---
*Generated by SkillOps - Automated Portfolio Management*
```

#### Step 4: Git Operations

For each project:
1. `git init` (if not already)
2. `git add .`
3. `git commit -m "Initial commit"`
4. Create GitHub repository via API
5. `git remote add origin https://github.com/user/repo`
6. `git push -u origin main`

#### Step 5: Progress Tracking

- Execution is recorded in the daily session summary (SQLite `storage/skillops.db`).
- Detailed portfolio metadata is available in the command output and can be included in exports as needed.

### Example Workflow

```bash
# 1. Prepare projects in ~/labs/
mkdir -p ~/labs/my-python-project
echo "print('hello')" > ~/labs/my-python-project/main.py

# 2. Create GitHub token at https://github.com/settings/tokens
# Requirements: repo, delete_repo scopes

# 3. Run share command
skillops share \
  --storage-path ./storage \
  --labs-path ~/labs \
  --github-token ghp_xxxx \
  --github-username myusername

# Output:
# Processing my-python-project...
# [████████████░░] 80% - Pushing to GitHub...
# ✓ my-python-project: https://github.com/myusername/my-python-project
# ✓ Repository created and pushed successfully!
```

### Configuration

#### GitHub Token

Get a token at [github.com/settings/tokens](https://github.com/settings/tokens):

1. Click "Generate new token" → "Generate new token (classic)"
2. Name: "SkillOps"
3. Scopes: `repo`, `delete_repo`
4. Copy token to `.env`:
   ```bash
   GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
   ```

#### Repository Setup

The tool automatically:
- Creates repo as public (default)
- Enables "Generate from template" option (if template license exists)
- Sets description from project content

### Features

- **Automatic Tech Detection**: Identifies tech stack without configuration
- **Professional READMEs**: Badges, installation, features auto-generated
- **Zero Manual Steps**: One command to git init, GitHub create, and push
- **Batch Operations**: Process entire directory in one run
- **Idempotent**: Safe to run multiple times (skips existing repos)
- **Error Handling**: Detailed feedback if API fails
- **Progress Tracking**: History of created repositories

### Troubleshooting

**Error: GitHub API returned 401**
- Check GITHUB_TOKEN is valid and not expired
- Regenerate token at github.com/settings/tokens

**Error: "You've exceeded a secondary rate limit"**
- Wait 15 minutes before retrying
- Process fewer projects at once

**Git remote already exists**
- The tool skips projects already pushed to GitHub
- To re-push: `git remote remove origin` first

---

## Reflection & Notifications

**Purpose:** Send daily learning summaries and reminders via Telegram.

**Status:** ✅ Sprint 2 - Fully Implemented

### Overview

Automatically send formatted Telegram messages with your daily learning metrics and motivational reminders.

### Command

```bash
skillops start

# or send a notification directly
skillops notify \
  --storage-path <path> \
  [--respect-schedule]
```

### Required Arguments

- `--storage-path`: SkillOps storage directory

### Options

- `--respect-schedule`: Only send if within scheduled time (default: always send)

### Configuration

Add to `.env`:
```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdEFghIjklmnoPQRstUVwxyz
TELEGRAM_CHAT_ID=987654321
TELEGRAM_SCHEDULE_TIME=08:00  # 8 AM
```

### Getting Started with Telegram

1. **Create Bot**:
   - Message `@BotFather` on Telegram
   - `/newbot` → name it "SkillOps"
   - Copy the token to `.env` as `TELEGRAM_BOT_TOKEN`

2. **Get Chat ID**:
   - Message your bot anything
   - Visit `https://api.telegram.org/bot<token>/getUpdates`
   - Find your chat ID and add to `.env` as `TELEGRAM_CHAT_ID`

### Message Format

Messages are formatted with Markdown:

```
📊 SkillOps Daily Report

Date: 2026-01-11
Time Coded: 3h 42m
Steps Completed: 7/9 ✅
Streak: 5 days 🔥

Top Achievement:
✓ Completed GitHub automation feature
✓ Tested portfolio sharing on 5 projects

Tomorrow's Focus:
→ UX Polish & Error Handling
→ Flashcard review (47 new cards)

💡 Remember: Consistency beats perfection!
```

### Schedule Support

Send notifications only during specific times:

```bash
# Only sends if current time is after 08:00
skillops notify --storage-path ./storage --respect-schedule
```

In cron, you'd run it multiple times:
```bash
# Crontab: Run every hour, respects schedule
0 * * * * /path/to/skillops notify --storage-path ~/.skillops --respect-schedule
```

### Features

- **Markdown Formatting**: Bold, code, emojis for visual appeal
- **Schedule-Aware**: Respects configured notification time
- **Batch Sends**: Multiple recipients support (future)
- **Error Resilient**: Continues on API failures with detailed logging
- **Verbose diagnostics**: Use `--verbose` to see detailed logs

### Example Workflow

```bash
# 1. Set up Telegram bot (one time)
# Get token and chat ID as described above

# 2. Add to .env
echo "TELEGRAM_BOT_TOKEN=..." >> .env
echo "TELEGRAM_CHAT_ID=..." >> .env
echo "TELEGRAM_SCHEDULE_TIME=08:00" >> .env

# 3. Send notification
skillops notify --storage-path ./storage

# 4. (Optional) Schedule via cron
# See SETUP_CRON.md for detailed setup
```

### Troubleshooting

**Error: Invalid token**
- Verify token from `@BotFather`
- Check `.env` for typos

**No message received**
- Check TELEGRAM_CHAT_ID is correct
- Try without `--respect-schedule` first

**Schedule not working**
- Verify TELEGRAM_SCHEDULE_TIME format (HH:MM)
- Use `--verbose` to see schedule checks

---

## Health & Doctor Checks

**Purpose:** Verify all API tokens and configurations are working.

**Status:** ✅ Available

**Commands:**
```bash
skillops health
skillops doctor
```

**Output:**
```
🏥 SkillOps Health Check
━━━━━━━━━━━━━━━━━━━━━━━━━━
GitHub Token:         ✅ Valid
Telegram Bot:         ✅ Connected
Obsidian Vault:       ✅ Readable
WakaTime API:         ✅ Responsive
Storage Directory:    ✅ Writable

Overall Status: ✅ ALL SYSTEMS GO
```

---

## Advanced Usage

### Verbose Logging

Enable detailed logging for troubleshooting:

```bash
skillops share --storage-path ./storage --verbose
skillops notify --storage-path ./storage --verbose
```

### Storage Directory

SkillOps stores all data in a single directory (default: `./storage`):

```
storage/
├── skillops.db          # SQLite database (all state + metrics)
└── exports/             # Optional JSON/CSV exports
  ├── skillops_export.json
  └── skillops_export.csv
```

SQLite is the source of truth. Use `skillops export` for human-readable snapshots.

### CI/CD Integration

Use SkillOps in GitHub Actions:

```yaml
# .github/workflows/daily.yml
name: Daily Learning Routine

on:
  schedule:
    - cron: '0 8 * * *'  # 8 AM daily

jobs:
  routine:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: |
          skillops doctor
          skillops create --storage-path ./storage \
            --vault-path ${{ secrets.OBSIDIAN_PATH }} \
            --anki-sync-path ${{ secrets.ANKI_PATH }}
          skillops notify --storage-path ./storage --respect-schedule
```

---
