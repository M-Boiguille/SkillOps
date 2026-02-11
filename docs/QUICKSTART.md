# SkillOps Quick Start Guide

Get up and running with SkillOps in 5 minutes.

## Prerequisites

- Python 3.11+
- pip or poetry
- Git
- API tokens (optional, required for full feature set)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/M-Boiguille/SkillOps.git
cd SkillOps
```

### 2. Create virtual environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
# or with poetry:
poetry install
```

### 4. Configure API tokens (Optional)

```bash
cp .env.example .env
# Edit .env with your tokens:
# - GITHUB_TOKEN (for portfolio automation)
# - TELEGRAM_BOT_TOKEN & TELEGRAM_CHAT_ID (for notifications)
# - OBSIDIAN_VAULT_PATH (for flashcard generation)
```

## Quick Test Run

### Test the CLI is working

```bash
# Check version
skillops version

# Get help
skillops --help

# Run health check (verify configuration)
skillops health

# Run preflight doctor checks
skillops doctor
```

### Run your first step

```bash
# Launch interactive menu (all steps)
skillops start

# Morning mode (learning: steps 1-3)
skillops start --mode=learning

# Afternoon mode (engineering: steps 4-9)
skillops start --mode=engineering
```

### Example workflow

```bash
# 1. Start the menu and run steps (Review, Read, Tutor, Create, etc.)
skillops start

# 2. Share projects to GitHub (creates repos with auto-generated READMEs)
skillops share \
  --storage-path ./storage \
  --labs-path ~/labs \
  --github-token your_token_here \
  --github-username your_username

# 3. Send daily notification
skillops notify \
  --storage-path ./storage \
  --respect-schedule
```

## Verify Installation

Run the test suite to ensure everything works:

```bash
pytest -v                    # Run all tests
pytest --cov               # Check coverage (target: >80%)
pytest tests/unit/         # Run only unit tests
pytest -k "test_share"     # Run specific tests
```

**Expected output (example):**
```
441 passed, 27 skipped in 12.6s
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# GitHub Portfolio Automation
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
GITHUB_USERNAME=your_username
LABS_PATH=~/labs
# Optional Gemini model override
GEMINI_MODEL=gemini-2.5-flash

# Optional: logical day start hour for streaks (default 4)
SKILLOPS_DAY_START_HOUR=4

# Telegram Notifications
TELEGRAM_BOT_TOKEN=123456789:ABCdEFghIjklmnoPQRstUVwxyz
TELEGRAM_CHAT_ID=987654321

# Flashcard Generation
OBSIDIAN_VAULT_PATH=~/Obsidian
ANKI_SYNC_PATH=~/Anki/sync

# WakaTime (existing)
WAKATIME_API_KEY=waka_xxxxxxxxxxxxxxxx
```

### Storage Directory Structure

SkillOps stores data in your storage directory:

```
storage/
├── skillops.db        # SQLite database (all state + metrics)
└── exports/           # Optional JSON/CSV exports
  ├── skillops_export.json
  └── skillops_export.csv
```

SQLite is the source of truth. Use `skillops export` for human-readable snapshots.

## Troubleshooting

### "Module not found" errors

Make sure your virtual environment is activated:
```bash
source .venv/bin/activate
```

### API token errors

Check your `.env` file is in the project root:
```bash
ls -la .env
cat .env  # (don't share this!)
```

Verify tokens are valid by running:
```bash
skillops health
```

### See detailed logs

Add `--verbose` (or `-v`) to any command to show debug logs, useful for tracing API calls and git operations:
```bash
skillops share --verbose --labs-path ./labs --github-username YOUR_USER
skillops notify --verbose --storage-path ./storage
```

### Test failures

Check Python version:
```bash
python --version  # Should be 3.11+
```

Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

## Next Steps

1. **Read the [FEATURES guide](FEATURES.md)** for detailed documentation on each command
2. **Check [.env.example](.env.example)** for all configuration options
3. **Explore [project-lifecycle/](project-lifecycle/)** for architecture decisions
4. **Set up automation**: See [SETUP_CRON.md](SETUP_CRON.md) or [SETUP_SYSTEMD.md](SETUP_SYSTEMD.md)

## Getting Help

- 📖 Full documentation in [README.md](../README.md)
- 🐛 Issues: [GitHub Issues](https://github.com/M-Boiguille/SkillOps/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/M-Boiguille/SkillOps/discussions)

---

**Pro tip**: Run `skillops --help` anytime to see all available commands with their options.
