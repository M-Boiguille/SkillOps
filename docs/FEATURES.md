# SkillOps Features Guide

Complete documentation of all SkillOps features and commands.

## Table of Contents

1. [Core Commands](#core-commands)
2. [Review Metrics (Step 1)](#review-metrics)
3. [Formation Tracking (Step 2)](#formation-tracking)
4. [AI Analysis (Step 3)](#ai-analysis)
5. [Reinforcement (Step 4)](#reinforcement)
6. [Zettelkasten Notes (Step 5)](#zettelkasten-notes)
7. [Flashcard Generation (Step 6) - Sprint 2](#flashcard-generation)
8. [Portfolio Automation (Step 7) - Sprint 2](#portfolio-automation)
9. [Daily Notifications (Step 8) - Sprint 2](#daily-notifications)
10. [Health Check](#health-check)
11. [Advanced Usage](#advanced-usage)

---

## Core Commands

### Getting Help

```bash
# Show all available commands
skillops --help

# Get help for specific command
skillops review --help
skillops create --help
skillops share --help
skillops notify --help
```

### Verbose Output

```bash
# Enable detailed logging for troubleshooting
skillops review --storage-path ./storage --verbose
```

### Version

```bash
# Display SkillOps version
skillops --version
```

---

## Review Metrics

**Purpose:** Review yesterday's learning metrics and progress.

**Command:**
```bash
skillops review --storage-path <path>
```

**Required Arguments:**
- `--storage-path`: Directory where progress is stored (e.g., `./storage` or `~/.skillops`)

**Options:**
- `--verbose`: Show detailed logging

**Output:**
```
📊 Learning Metrics Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Date: 2026-01-11
Time Coded: 3h 42m
Steps Completed: 7/8
Current Streak: 5 days
Average Streak: 3.2 days
Total Learning Hours: 142h
Weekly Average: 20.3h
```

**Data Stored:**
```json
{
  "date": "2026-01-11",
  "hours_coded": 3.7,
  "steps_completed": 7,
  "streak": 5,
  "notes": "Good progress on DevOps fundamentals"
}
```

**Use Cases:**
- Morning routine: Review what you achieved yesterday
- Motivation tracking: Monitor your streak and consistency
- Planning: Understand which topics need more time

---

## Formation Tracking

**Purpose:** Track time spent on learning and coding.

**Command:**
```bash
skillops formation --storage-path <path>
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

## AI Analysis

**Purpose:** Get AI-generated questions and answers on study topics.

**Command:**
```bash
skillops analysis --storage-path <path> [--topic <topic>]
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

## Reinforcement

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

## Zettelkasten Notes

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

## Flashcard Generation

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

2. **Progress tracking** (`.progress.json`):
   ```json
   {
     "date": "2026-01-11",
     "flashcards_created": 47,
     "flashcards_hash": "sha256:abc123...",
     "vault_scanned": true
   }
   ```

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

## Portfolio Automation

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

Stores in `.progress.json`:
```json
{
  "date": "2026-01-11",
  "repositories_created": 3,
  "repositories": [
    {
      "name": "k8s-playground",
      "url": "https://github.com/user/k8s-playground",
      "tech_stack": ["Kubernetes", "Docker"],
      "commit": "a322f7a1b2c3d4e5f6g7h8i9j0k1l2m3"
    }
  ]
}
```

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

## Daily Notifications

**Purpose:** Send daily learning summaries and reminders via Telegram.

**Status:** ✅ Sprint 2 - Fully Implemented

### Overview

Automatically send formatted Telegram messages with your daily learning metrics and motivational reminders.

### Command

```bash
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
Steps Completed: 7/8 ✅
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
- **Dry-Run Mode**: Test without sending (use `--verbose`)

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

## Health Check

**Purpose:** Verify all API tokens and configurations are working.

**Status:** ✅ Sprint 3 - Planned (Coming Soon)

**Command:**
```bash
skillops health
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

Enable detailed logging for all commands:

```bash
skillops review --storage-path ./storage --verbose
# Output: DEBUG logs for troubleshooting
```

### Dry-Run Mode

Test commands without side effects:

```bash
skillops share --storage-path ./storage --dry-run
# Shows what would happen without actual git/GitHub operations
```

### Exit Codes

Scripts can check success/failure:

```bash
skillops notify --storage-path ./storage
if [ $? -eq 0 ]; then
  echo "✅ Notification sent"
else
  echo "❌ Notification failed"
fi
```

Possible codes:
- `0`: Success
- `1`: Configuration error
- `2`: API error
- `3`: File system error

### Storage Directory

SkillOps stores all data in a single directory (default: `./storage`):

```
storage/
├── .state.yaml          # Current step, timestamp
├── .progress.json       # Daily progress history
├── .metrics.json        # Streak, averages, totals
└── .session.log         # Detailed operation log
```

All files are human-readable (JSON/YAML) for easy inspection and version control.

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
          skillops review --storage-path ./storage
          skillops create --storage-path ./storage \
            --vault-path ${{ secrets.OBSIDIAN_PATH }} \
            --anki-sync-path ${{ secrets.ANKI_PATH }}
          skillops notify --storage-path ./storage
```

---

## Feature Comparison Matrix

| Feature | Status | Sprint | Tests | Coverage |
|---------|--------|--------|-------|----------|
| Review Metrics | ✅ Implemented | 1 | 3 | 100% |
| Formation Tracking | ✅ Implemented | 1 | 3 | 100% |
| AI Analysis | ✅ Implemented | 1 | 3 | 100% |
| Reinforcement | ✅ Implemented | 1 | 3 | 100% |
| Zettelkasten | ✅ Implemented | 1 | 3 | 100% |
| Flashcards | ✅ Implemented | 2 | 17 | 95% |
| Portfolio | ✅ Implemented | 2 | 36 | 90% |
| Notifications | ✅ Implemented | 2 | 7 | 100% |
| Health Check | 🔄 Planned | 3 | TBD | TBD |
| Progress Bars | 🔄 Planned | 3 | TBD | TBD |
| Systemd/Cron | 🔄 Planned | 3 | TBD | TBD |

---

**Last Updated**: Sprint 2 Complete (11 janvier 2026)
**Next Update**: Sprint 3 Complete (18 janvier 2026)
