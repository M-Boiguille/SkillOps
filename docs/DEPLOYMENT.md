# Local Deployment & Rollback

> **SkillOps is production-ready for local single-user use.** This guide covers local deployment, backups, and rollback procedures.

---

## Local Deployment Checklist

### Pre-Deployment

- [ ] **Update code**: `git pull origin main`
- [ ] **Install dependencies**: `pip install -r requirements-lock.txt` (for reproducibility)
- [ ] **Verify setup**: `skillops doctor` (all checks pass)
- [ ] **Run tests**: `pytest -v` (or `pytest -v tests/smoke` for quick check)
- [ ] **Create backup**: `bash setup/backup/backup.sh` (before deploying)

### Deployment

- [ ] **Enable automation**:
  - **Cron** (recommended): `crontab -e` and add:
    ```bash
    # Daily cleanup at 23:00
    0 23 * * * bash /path/to/SkillOps/setup/backup/backup.sh

    # Daily notifications at 20:00 (optional)
    0 20 * * * cd /path/to/SkillOps && skillops notify --storage-path storage --respect-schedule
    ```
  - **Systemd** (alternative): `systemctl --user enable skillops.timer` (if configured)

### Post-Deployment

- [ ] **Smoke tests**: `pytest -v tests/smoke`
- [ ] **Functional check**: `skillops start` → run one step successfully
- [ ] **Verify backup**: `ls -lah ~/.local/share/skillops/backups/`

---

## Backup & Recovery

### Automated Daily Backups

```bash
# Setup daily backup at 23:00 (add to crontab)
0 23 * * * bash /path/to/SkillOps/setup/backup/backup.sh

# Verify backups are created
ls -lah ~/.local/share/skillops/backups/
# Output: skillops_20250212_230015.db, skillops_20250211_230012.db, ...
```

### Manual Backup (Before Any Change)

```bash
# Backup now
bash setup/backup/backup.sh

# Or copy directly
cp ~/.local/share/skillops/skillops.db ~/.local/share/skillops/skillops.db.manual_backup
```

### Restore from Backup

```bash
# List available backups
ls -lah ~/.local/share/skillops/backups/

# Restore a specific backup
bash setup/backup/restore.sh ~/.local/share/skillops/backups/skillops_20250210_230000.db

# Verify restore
skillops doctor
skillops metrics --hours 1  # Check data is there
```

### Backup Retention

Backups are kept for 14 days by default:

```bash
# Override retention (keep 30 days of backups)
export SKILLOPS_BACKUP_RETENTION_DAYS=30
bash setup/backup/backup.sh
```

---

## Rollback Procedure

If something breaks after deployment:

### 1. Stop Any Running Processes

```bash
# Kill any running skillops instances
pkill -f "skillops start"
pkill -f "skillops notify"

# Or disable cron jobs temporarily
crontab -e
# Comment out the skillops lines
```

### 2. Restore Last Known Good State

```bash
# Find the most recent backup before the issue
ls -lah ~/.local/share/skillops/backups/

# Restore it
bash setup/backup/restore.sh ~/.local/share/skillops/backups/skillops_20250210_230000.db

# Verify
skillops doctor
```

### 3. Revert Code Changes (If Needed)

```bash
# Check recent commits
git log --oneline -5

# Revert to previous version
git revert HEAD  # Revert last commit
# Or
git checkout HEAD~1 -- src/  # Go back one commit for src/
```

### 4. Reinstall Dependencies

```bash
source .venv/bin/activate
pip install -r requirements-lock.txt
skillops doctor
```

### 5. Resume Operations

```bash
# Re-enable cron jobs
crontab -e
# Uncomment the skillops lines

# Manual test
skillops start  # Run one step

# Verify metrics
skillops metrics --hours 1
```

---

## Data Retention & Cleanup

### View Current Storage

```bash
skillops metrics --hours 24
# Shows: incidents, postmortems, performance_metrics, chaos_events

# Check database size
du -sh ~/.local/share/skillops/skillops.db
```

### Automatic Cleanup (On-Demand)

```bash
# Remove data older than 30 days
skillops retention --days 30

# Remove AND optimize database
skillops retention --days 30 --vacuum
```

### What Gets Cleaned

- **Performance metrics** (older than --days): WakaTime stats, study time
- **Chaos events** (older than --days): Generated incidents, chaos monkey runs
- **Resolved incidents** (older than --days): Completed on-call scenarios

### Schedule Regular Cleanup

Add to crontab (runs monthly):

```bash
0 0 1 * * cd /path/to/SkillOps && skillops retention --days 90 --vacuum
```

---

## Secrets & Configuration Management

### Store Secrets in OS Keyring (Recommended)

```bash
# Enable keyring backend
export SKILLOPS_USE_KEYRING=true

# Add secrets
skillops secret-set GEMINI_API_KEY
skillops secret-set GITHUB_TOKEN

# List stored secrets
skillops secret-list

# Remove a secret if needed
skillops secret-unset GITHUB_TOKEN
```

### Or Use Local .env File

```bash
# Create protected config
cat > ~/.config/skillops/skillops.env << EOF
GEMINI_API_KEY=AIza...
GITHUB_TOKEN=ghp_...
EOF

chmod 600 ~/.config/skillops/skillops.env
```

---

## Database Integrity Checks

### Run Health Checks

```bash
# Full system diagnostics
skillops doctor

# Output checks:
# ✓ Config files found
# ✓ Database connection OK
# ✓ Schema version 4 verified
# ✓ Foreign keys enabled
# ✓ Keyring backend ready (if enabled)
# ✓ API credentials valid
```

### Manual Database Verification

```bash
# Check database consistency
sqlite3 ~/.local/share/skillops/skillops.db

sqlite> PRAGMA integrity_check;
# Output: ok

sqlite> SELECT version FROM _schema_version;
# Output: 4

sqlite> SELECT COUNT(*) FROM incidents;
# Output: (number of incidents)

sqlite> .quit
```

---

## Disaster Recovery (Data Loss)

### Scenario: Database Corrupted or Lost

```bash
# 1. Check for backups
ls -lah ~/.local/share/skillops/backups/

# 2. If backup exists, restore it
bash setup/backup/restore.sh ~/.local/share/skillops/backups/skillops_20250210_230000.db

# 3. If no backups, migration from old JSON (if you have it)
skillops migrate  # Imports legacy .progress.json, formation_log.json, reinforce_progress.json

# 4. If no backups and no JSON, start fresh
rm ~/.local/share/skillops/skillops.db
skillops start  # Creates fresh database
```

---

## Dependency Management

### Using Locked Versions (Recommended)

For reproducible deployments, always use the lockfile:

```bash
# Production-like install
pip install -r requirements-lock.txt

# Verify exact versions
pip freeze | head -10
```

### Updating Dependencies

```bash
# Only when needed (breaking bugs, security issues)
pip install --upgrade pip setuptools
pip install --upgrade -r requirements.txt

# Re-generate lockfile
pip freeze > requirements-lock.txt
git add requirements-lock.txt
git commit -m "chore: Update dependency lockfile"
```

---

## Monitoring & Alerts

### Health Checks

```bash
# Run before critical operations
skillops doctor

# Expected output: All green ✓
```

### Log Monitoring (Optional)

```bash
# View logs in JSON format
export SKILLOPS_LOG_FORMAT=json

# Store logs for analysis
cd /path/to/SkillOps && skillops start 2>&1 | tee logs/$(date +%Y%m%d_%H%M%S).log
```

### Metrics Review

```bash
# Daily metrics check
skillops metrics --hours 24

# Weekly summary
skillops metrics --hours 168

# Monthly archive
skillops export --format json --output exports/skillops_$(date +%Y%m).json
```

---

## Release Strategy

SkillOps uses semantic versioning and CI/CD:

### Version Scheme

- `vX.Y.Z` (e.g., `v0.4.2`)
- `X` = breaking changes
- `Y` = new features
- `Z` = bugfixes

### Release Workflow

1. **Feature development** → branches off `main`
2. **Pull request** → triggers CI (lint → tests → coverage)
3. **Code review** → required before merge
4. **Merge to main** → CI runs full test suite
5. **Tag release** → `git tag vX.Y.Z && git push --tags`
6. **GitHub Release** → auto-published with changelog

### Local Tag Management

```bash
# List releases
git tag -l

# Update to latest release
git fetch --tags
git checkout v0.4.2

# Or stay on main for latest development
git checkout main
git pull origin main
```

---

## Troubleshooting Deployments

| Issue | Solution |
|-------|----------|
| **"Database locked"** | Kill lingering processes: `pkill -f skillops` |
| **"Import error"** | Reinstall: `pip install -e .[dev]` |
| **"API key not found"** | Set via keyring: `skillops secret-set GEMINI_API_KEY` |
| **"Backup failed"** | Check permissions: `chmod 755 ~/.local/share/skillops` |
| **"Tests failing"** | Clear DB and retry: `rm ~/.local/share/skillops/skillops.db && pytest -v` |

---

## Next Steps

1. **Run deployment checklist** above
2. **Setup daily backups** via crontab
3. **Schedule retention cleanup** monthly
4. **Monitor with**: `skillops metrics --hours 24`
5. **Read**: [OPERATIONS.md](OPERATIONS.md) and [SECURITY.md](SECURITY.md)
