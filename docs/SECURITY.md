# Security & Secrets Management

> **SkillOps handles local development secrets securely using OS keyring and file-based config.**

---

## Overview

SkillOps stores sensitive data (API keys) in **three secure layers**:

1. **OS Keyring** (recommended) — Platform keyring (macOS Keychain, Linux Secret Service, Windows Credential Manager)
2. **Per-user Config** — `~/.config/skillops/skillops.env` (read-only by user)
3. **Local .env** — `.env` file (development only, `.gitignore`d)

---

## Secrets Handled by SkillOps

| Secret | Purpose | Required | How to Set |
|--------|---------|----------|-----------|
| `GEMINI_API_KEY` | Google AI (tutor, oncall) | Yes* | `skillops secret-set` or `.env` |
| `WAKATIME_API_KEY` | Code metrics | No | `skillops secret-set` or `.env` |
| `GITHUB_TOKEN` | Portfolio automation | No | `skillops secret-set` or `.env` |
| `TELEGRAM_BOT_TOKEN` | Notifications | No | `skillops secret-set` or `.env` |
| `TELEGRAM_CHAT_ID` | Notifications target | No | `skillops secret-set` or `.env` |

*Required for full workflow; works offline without it.

---

## OS Keyring (Recommended - Secure)

### Setup

```bash
# Enable keyring backend globally
export SKILLOPS_USE_KEYRING=true

# Or add to ~/.bashrc or ~/.zshrc:
echo 'export SKILLOPS_USE_KEYRING=true' >> ~/.bashrc
source ~/.bashrc
```

### Platform Support

- **macOS**: Uses native **Keychain** (✅ built-in)
- **Linux**: Uses **Secret Service** or **Pass** backend (⚠️ may need setup)
- **Windows**: Uses **Credential Manager** (✅ built-in)

### Linux Setup (if needed)

```bash
# Ubuntu/Debian: Install keyring service
sudo apt install python3-keyring gnome-keyring

# Or use Pass backend
brew install pass  # or apt install pass

# Verify keyring works
python -c "import keyring; print(keyring.get_keyring())"
# Output: <class 'keyring.backends.SecretService.SecretService'>
```

### Store Secrets

```bash
# Store GEMINI API key interactively
skillops secret-set GEMINI_API_KEY
# Prompts: Enter value: [hidden]
#        Confirm: [hidden]
# Stored securely in OS keyring

# Store multiple secrets
skillops secret-set WAKATIME_API_KEY
skillops secret-set GITHUB_TOKEN
skillops secret-set TELEGRAM_BOT_TOKEN
```

### Verify Secrets

```bash
# List stored secrets (values are hidden)
skillops secret-list
# Output:
# Secrets in OS keyring:
#   - GEMINI_API_KEY: ••••••••••••
#   - WAKATIME_API_KEY: ••••••••••••
#   - GITHUB_TOKEN: ••••••••••••
```

### Remove Secrets

```bash
# Delete a stored secret
skillops secret-unset GITHUB_TOKEN

# Or remove all
skillops secret-unset GEMINI_API_KEY
skillops secret-unset WAKATIME_API_KEY
```

---

## .env File (For Development)

### Create and Protect

```bash
# Copy template
cp .env.example .env

# Edit with your secrets
nano .env

# Restrict to user only (owner read/write, no group/other)
chmod 600 .env

# Verify permissions
ls -la .env
# -rw------- 1 user user 500 Feb 12 10:00 .env
```

### .env File Contents

```bash
# AI (required for tutor/oncall)
GEMINI_API_KEY=AIzaSyD...

# Metrics (optional)
WAKATIME_API_KEY=waka_XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX

# Portfolio automation (optional)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxx
GITHUB_USERNAME=myusername

# Notifications (optional)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=987654321
TELEGRAM_SCHEDULE_TIME=20:00

# Integrations (optional)
OBSIDIAN_VAULT_PATH=~/Obsidian
ANKI_SYNC_PATH=~/Anki/sync
LABS_PATH=~/labs
```

### .env Never Committed

```bash
# Verify .env is in .gitignore
cat .gitignore | grep -E "\.env"
# Output: .env

# Confirm not staged
git status
# Should NOT show: modified: .env
```

---

## Per-User Config Directory (Persistent)

### Setup

```bash
# Create config directory
mkdir -p ~/.config/skillops

# Create config file with secrets
cat > ~/.config/skillops/skillops.env << EOF
GEMINI_API_KEY=AIza...
GITHUB_TOKEN=ghp_...
TELEGRAM_BOT_TOKEN=123456:ABC...
EOF

# Protect file
chmod 600 ~/.config/skillops/skillops.env

# Verify
ls -la ~/.config/skillops/skillops.env
# -rw------- 1 user user 300 Feb 12 10:00 ~/.config/skillops/skillops.env
```

### Advantages

- Persists across clones/updates of the repo
- Not in version control
- Survives `git clean`
- Can be shared/backed up separately

### Load Order

SkillOps loads secrets in this order (first found wins):

1. Environment variables (highest priority)
2. OS Keyring (if `SKILLOPS_USE_KEYRING=true`)
3. `.env` (current directory)
4. `~/.config/skillops/skillops.env` (user home)

---

## Best Practices

### Do's ✅

- ✅ Store API keys in **OS keyring** (recommended)
- ✅ Use **per-user config** `~/.config/skillops/` for persistence
- ✅ Protect files with `chmod 600`
- ✅ Use **strong, unique** API keys
- ✅ Rotate API keys **every 90 days**
- ✅ Use **fine-grained GitHub tokens** (limited scope)
- ✅ Commit only `.env.example` (no real secrets)
- ✅ Review what secrets are used: `skillops secret-list`

### Don'ts ❌

- ❌ Never commit `.env` or real secrets to git
- ❌ Don't share API keys in chat, email, or logs
- ❌ Don't hardcode secrets in Python code
- ❌ Don't leave secrets in world-readable files
- ❌ Don't use the same API key across services
- ❌ Don't store backups with unencrypted secrets
- ❌ Don't log or print API keys

---

## API Key Rotation

### Why Rotate?

- **Security best practice** (prevents long-term compromise)
- **Compliance** (some orgs require 90-day rotation)
- **Incident response** (immediately after suspected leak)

### GitHub Token Rotation

```bash
# 1. Create new token at https://github.com/settings/tokens
#    Scopes: repo (full), or fine-grained: Contents (R/W), Metadata (R)

# 2. Update in SkillOps
skillops secret-set GITHUB_TOKEN
# Enter new token at prompt

# 3. Test new token
skillops doctor  # Should pass

# 4. Delete old token on GitHub
# https://github.com/settings/tokens (find and delete old one)

# 5. Verify
skillops metrics --hours 1  # Should work
```

### Gemini API Key Rotation

```bash
# 1. Create new key at https://aistudio.google.com/apikey
# 2. Delete old key

# 3. Update in SkillOps
skillops secret-set GEMINI_API_KEY
# Enter new key at prompt

# 4. Test
skillops doctor  # Should pass

# 5. Try AI feature
skillops oncall --dry-run  # Should work
```

### Telegram Bot Rotation

```bash
# 1. Create new bot with @BotFather
# 2. Get new token and chat ID

# 3. Update in SkillOps
skillops secret-set TELEGRAM_BOT_TOKEN
# Prompt for new bot token

# 4. Test notifications
skillops notify --storage-path storage --respect-schedule

# 5. Delete old bot token
# Message @BotFather, `/revoke`, select old token
```

---

## Incident Response

### Suspected Leak (Compromised API Key)

1. **Identify compromised key**
   ```bash
   skillops secret-list  # See what's stored
   ```

2. **Immediately revoke in source**
   - GitHub: https://github.com/settings/tokens → delete
   - Google: https://aistudio.google.com/apikey → delete
   - Telegram: Message @BotFather → `/revoke`

3. **Remove from SkillOps**
   ```bash
   skillops secret-unset GITHUB_TOKEN  # or whichever is compromised
   ```

4. **Audit access logs** (if available)
   ```bash
   # GitHub: https://github.com/settings/log
   # Google Cloud: https://console.cloud.google.com/activity
   ```

5. **Generate new API key**
   - Follow rotation steps above

6. **Update in SkillOps**
   ```bash
   skillops secret-set GITHUB_TOKEN  # With new key
   ```

7. **Verify working**
   ```bash
   skillops doctor
   ```

---

## Backup & Disaster Recovery

### Secure Backup of Secrets

**Option 1: OS Keyring Auto-Backup**
```bash
# OS keyring is typically backed up by system
# No special action needed on most systems
```

**Option 2: Manual Export (Use with Caution)**
```bash
# Export secrets to encrypted file (for offline backup)
# WARNING: Highly sensitive, store very securely

# List what would be backed up:
skillops secret-list

# Store securely (e.g., encrypted USB, safe deposit box)
```

**Option 3: Per-User Config Backup**
```bash
# Backup ~/.config/skillops/ securely
tar czf ~/.config/skillops_backup.tar.gz ~/.config/skillops/

# Store securely with tight permissions
chmod 600 ~/.config/skillops_backup.tar.gz
```

### Restore After Reinstall

```bash
# 1. Restore config directory
tar xzf ~/.config/skillops_backup.tar.gz -C ~/

# 2. Or manually re-enter secrets
skillops secret-set GEMINI_API_KEY
skillops secret-set GITHUB_TOKEN

# 3. Verify
skillops doctor
```

---

## Database Encryption (Optional)

SkillOps uses SQLite without native encryption. For local use, OS-level security is sufficient:

### File System Permissions

```bash
# Restrict database permissions
chmod 600 ~/.local/share/skillops/skillops.db

# Verify
ls -la ~/.local/share/skillops/skillops.db
# -rw------- 1 user user 1048576 Feb 12 10:00 skillops.db
```

### Full-Disk Encryption (Recommended)

```bash
# Enable full-disk encryption on your system
# Ubuntu: LUKS (automatic on install)
# macOS: FileVault 2 (System Preferences → Security & Privacy)
# Windows: BitLocker (Settings → System → About)

# Verify encryption is enabled
sudo cryptsetup status /dev/mapper/cryptname  # Linux
diskutil secureDelete freespace 0 /Volumes/YourDisk  # macOS
```

---

## Dependency Security

### Vulnerability Scanning

```bash
# Check for known vulnerabilities in dependencies
pip install safety
safety check

# Generate report
safety check --json > safety_report.json
```

### Keep Dependencies Updated

```bash
# Update to latest versions
pip install --upgrade pip setuptools wheel

# Update SkillOps dependencies
pip install --upgrade -r requirements.txt

# Re-lock versions for reproducibility
pip freeze > requirements-lock.txt
```

---

## Configuration Permissions

### File Permissions Checklist

```bash
# .env file (if using local config)
ls -la .env
# Must be: -rw------- (owner read/write only)
# If not: chmod 600 .env

# ~/.config/skillops/skillops.env
ls -la ~/.config/skillops/skillops.env
# Must be: -rw------- (owner read/write only)
# If not: chmod 600 ~/.config/skillops/skillops.env

# Database
ls -la ~/.local/share/skillops/skillops.db
# Must be: -rw------- (owner read/write only)
# If not: chmod 600 ~/.local/share/skillops/skillops.db

# Storage directory
ls -la ~/.local/share/skillops/
# Must be: drwx------ (owner read/write/execute only)
# If not: chmod 700 ~/.local/share/skillops/

# Verify all
skillops doctor  # Checks permissions automatically
```

---

## Health Checks

### Daily Security Check

```bash
# Run before important work
skillops doctor

# Verifies:
# ✓ Config file permissions (readable only by user)
# ✓ Database permissions (readable only by user)
# ✓ API credentials present and valid
# ✓ Keyring backend working (if enabled)
```

### Monthly Security Audit

```bash
# Review API key usage
# 1. GitHub: https://github.com/settings/personal-access-tokens
# 2. Google: https://aistudio.google.com/apikey
# 3. WakaTime: https://wakatime.com/settings/api-key

# Check for unused/old keys
# Delete any you don't recognize

# Review recent access logs (if available)
# GitHub: https://github.com/settings/log
```

---

## Compliance & Standards

SkillOps follows these security practices:

- ✅ **OWASP Top 10**: No hardcoded secrets, secure storage
- ✅ **Principle of Least Privilege**: Fine-grained GitHub tokens
- ✅ **Defense in Depth**: Multiple secret storage options
- ✅ **Secure Defaults**: Requires explicit keyring enable
- ✅ **Dependency Scanning**: Pre-commit hooks + CI checks
- ✅ **No Data Exfiltration**: Runs locally, minimal network I/O

---

## Support & Escalation

### Questions?

- 📖 [LOCAL_SETUP.md](LOCAL_SETUP.md) — Detailed setup guide
- 🔧 [OPERATIONS.md](OPERATIONS.md) — Daily operations
- 📋 [DEPLOYMENT.md](DEPLOYMENT.md) — Deployment procedures

### Report Security Issues

- 🔒 **Private**: Do NOT open a public GitHub issue
- 📧 Email maintainer directly with details
- 🔐 Include: issue description, impact, recommended fix

---

## Next Steps

1. **Enable OS keyring**: `export SKILLOPS_USE_KEYRING=true`
2. **Store API keys**: `skillops secret-set GEMINI_API_KEY`
3. **Run health check**: `skillops doctor`
4. **Schedule rotation**: Calendar reminder every 90 days
5. **Review backup strategy**: [DEPLOYMENT.md](DEPLOYMENT.md#backup--recovery)
