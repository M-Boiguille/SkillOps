# Local Setup & Installation Guide

> **SkillOps is production-ready for local single-user use.** This guide walks you through a complete setup.

---

## Prerequisites

- **Python 3.11+** (check with `python --version`)
- **Git** (for cloning)
- **pip** (comes with Python)
- **~500MB disk** (SQLite database + backups)

---

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/M-Boiguille/SkillOps.git
cd SkillOps
```

### 2. Create Virtual Environment

```bash
# Create isolated Python environment
python -m venv .venv

# Activate it
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies

**Option A: Development (recommended for local use)**
```bash
pip install -e .[dev]
```

**Option B: Production with locked versions (for reproducibility)**
```bash
# Installs exact versions, no surprises
pip install -r requirements-lock.txt
```

**Option C: Minimal (if you only want the CLI)**
```bash
pip install -e .
```

### 4. Verify Installation

```bash
# Check version
skillops version

# Run preflight checks
skillops doctor

# Run smoke tests
pytest -v tests/smoke

# Expected output: All checks pass ✓
```

---

## Configuration

### Option A: OS Keyring (Recommended - Secure)

Store secrets in your OS keyring instead of files:

```bash
# Enable keyring backend
export SKILLOPS_USE_KEYRING=true

# Add your API keys interactively (stored securely in OS)
skillops secret-set GEMINI_API_KEY
# Prompts: Enter API key [hidden], Confirm [hidden]

skillops secret-set WAKATIME_API_KEY
skillops secret-set GITHUB_TOKEN
skillops secret-set TELEGRAM_BOT_TOKEN
```

Check stored secrets:
```bash
skillops secret-list
```

### Option B: .env File (Local Development)

For quick local testing without keyring:

```bash
# Copy example
cp .env.example .env

# Edit with your API keys
nano .env  # or vim, code, etc.

# Protect the file
chmod 600 .env
```

**Minimal .env (if you only use core features):**
```bash
# AI responses (required for tutor/oncall)
GEMINI_API_KEY=AIza...

# Code metrics (optional)
WAKATIME_API_KEY=waka_...

# Notifications (optional)
TELEGRAM_BOT_TOKEN=123456:ABC...
TELEGRAM_CHAT_ID=987654321

# Integrations (optional)
OBSIDIAN_VAULT_PATH=~/Obsidian
ANKI_SYNC_PATH=~/Anki/sync
GITHUB_TOKEN=ghp_...
GITHUB_USERNAME=yourname
LABS_PATH=~/labs
```

**Important:** `.env` is `.gitignore`d and never committed.

### Option C: Per-User Config Directory

For persistent config across sessions:

```bash
# Create config directory
mkdir -p ~/.config/skillops

# Create config file
cat > ~/.config/skillops/skillops.env << EOF
GEMINI_API_KEY=AIza...
WAKATIME_API_KEY=waka_...
TELEGRAM_BOT_TOKEN=123456:ABC...
EOF

# Restrict permissions
chmod 600 ~/.config/skillops/skillops.env
```

---

## Getting API Keys

### Google Gemini (for AI tutor/oncall)

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Click "Create API key"
3. Copy the key
4. Store: `skillops secret-set GEMINI_API_KEY` or add to `.env`

### WakaTime (for code metrics - optional)

1. Sign up at [WakaTime](https://wakatime.com)
2. Go to [Settings → Account](https://wakatime.com/settings/account)
3. Copy "Secret API Key"
4. Store: `skillops secret-set WAKATIME_API_KEY`

### GitHub (for portfolio automation - optional)

1. Go to [GitHub Settings → Tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Scopes: `repo` (for your private/public repos)
4. Copy the token
5. Store: `skillops secret-set GITHUB_TOKEN`

### Telegram (for notifications - optional)

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot`
3. Follow prompts (name your bot)
4. Copy the bot token
5. Get your chat ID: Message `@userinfobot`, copy the ID
6. Store:
   ```bash
   skillops secret-set TELEGRAM_BOT_TOKEN
   skillops secret-set TELEGRAM_CHAT_ID
   ```

---

## First Run

### Scenario 1: No API Keys (Offline Testing)

```bash
skillops start
# Works with mock data, no external APIs needed
```

### Scenario 2: Minimal Setup (Tutor + Metrics)

```bash
# Required for full functionality
skillops secret-set GEMINI_API_KEY
skillops secret-set WAKATIME_API_KEY

skillops doctor
skillops start
```

### Scenario 3: Full Setup (All Features)

```bash
# All secrets
skillops secret-set GEMINI_API_KEY
skillops secret-set WAKATIME_API_KEY
skillops secret-set GITHUB_TOKEN
skillops secret-set TELEGRAM_BOT_TOKEN

skillops doctor
skillops start
```

---

## Storage & Data Location

### SQLite Database

```bash
# Default location (auto-created):
~/.local/share/skillops/skillops.db

# Or override:
export SKILLOPS_STORAGE_PATH=~/.skillops_data
skillops start
```

### Backups

```bash
# Manual backup
cp ~/.local/share/skillops/skillops.db ~/.local/share/skillops/skillops.db.backup

# Or use the automated script:
bash setup/backup/backup.sh

# List backups:
ls -lah ~/.local/share/skillops/backups/
```

### Restore from Backup

```bash
bash setup/backup/restore.sh ~/.local/share/skillops/backups/skillops_YYYYmmdd_HHMMSS.db
```

---

## Development Tools

### Run Tests

```bash
# All tests
pytest -v

# Just smoke tests (quick)
pytest -v tests/smoke

# With coverage
pytest --cov=src/lms --cov-report=term-missing tests/

# Run specific test
pytest -v tests/lms/test_oncall_ai.py::test_generate_incident_with_retry
```

### Code Quality

```bash
# Format code (black)
black src/ tests/

# Type checking (mypy)
mypy src/

# Linting (flake8)
flake8 src/ tests/

# All at once (pre-commit)
pre-commit run --all-files
```

### Install Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install

# Now hooks run automatically on every commit
# To run manually:
pre-commit run --all-files
```

---

## Common Tasks

### Schedule Daily Reminders (Cron)

Edit crontab:
```bash
crontab -e
```

Add line (runs skillops at 8 AM daily):
```bash
0 8 * * * cd /path/to/SkillOps && skillops notify --storage-path storage --respect-schedule
```

### Automate Backups (Daily)

```bash
# In crontab:
0 23 * * * bash /path/to/SkillOps/setup/backup/backup.sh
```

### Clean Up Old Data

```bash
# Remove performance metrics older than 30 days
skillops retention --days 30

# Also optimize database after cleanup
skillops retention --days 30 --vacuum
```

### View Statistics

```bash
# Last 24 hours
skillops metrics --hours 24

# Last 7 days
skillops metrics --hours 168
```

### Perform Health Check

```bash
skillops doctor

# Checks:
# ✓ Config file permissions
# ✓ Database connectivity
# ✓ Keyring backend (if enabled)
# ✓ API credentials (Gemini, WakaTime, etc)
# ✓ File storage access
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'skillops'"

**Solution:** Make sure the venv is activated and dependencies installed:
```bash
source .venv/bin/activate
pip install -e .[dev]
skillops version
```

### Issue: "GEMINI_API_KEY not found"

**Solution:** Set it via keyring or .env:
```bash
# Via keyring
skillops secret-set GEMINI_API_KEY

# Or via .env
echo "GEMINI_API_KEY=AIza..." >> .env
chmod 600 .env
```

### Issue: "Database locked" errors

**Solution:** Database is already in use. Check for running processes:
```bash
# Kill any lingering processes
pkill -f skillops
# Then retry
skillops start
```

### Issue: Tests failing with "connection refused"

**Solution:** SQLite needs write access. Check permissions:
```bash
chmod 755 ~/.local/share/skillops
chmod 644 ~/.local/share/skillops/skillops.db
skillops doctor
```

### Issue: Keyring not working on Linux

**Solution:** Install system keyring backend:
```bash
# Ubuntu/Debian:
sudo apt install python3-keyring

# Or use .env file instead:
export SKILLOPS_USE_KEYRING=false
```

---

## Next Steps

1. **Read the workflow**: [docs/FEATURES.md](FEATURES.md)
2. **Run the daily menu**: `skillops start`
3. **Try incident simulation**: `skillops oncall`
4. **Check stats**: `skillops metrics --hours 24`
5. **Schedule automation**: See "Schedule Daily Reminders" above
6. **Setup backups**: Run `bash setup/backup/backup.sh`

---

## Support

- 📖 Full documentation: [README.md](../README.md)
- 🔧 Operations guide: [OPERATIONS.md](OPERATIONS.md)
- 🔒 Security guide: [SECURITY.md](SECURITY.md)
- 🎯 Features list: [FEATURES.md](FEATURES.md)
- 🐛 Issues: [GitHub Issues](https://github.com/M-Boiguille/SkillOps/issues)

---

**Happy learning! 🚀**
