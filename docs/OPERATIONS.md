# Operations Guide

> **Status:** SkillOps is production-ready for local single-user use with automated backups, metrics, and data retention.

---

## Current Features

**In production use:**
- ✅ SQLite persistence with schema v4, migrations, and consistency checks
- ✅ Automated backups (daily) with retention (14 days default)
- ✅ Restore procedures with validation
- ✅ Metrics and observability (`skillops metrics --hours 24`)
- ✅ Data retention/cleanup (`skillops retention --days 30 --vacuum`)
- ✅ Chaos Monkey (local) via `skillops chaos` (levels 1-3)
- ✅ AI-powered incidents (`skillops oncall` with validation + retry)
- ✅ Post-mortem documentation (`skillops post-mortem`)
- ✅ Secrets management (`skillops secret-set/unset` with OS keyring)
- ✅ Health diagnostics (`skillops doctor` with DB consistency checks)
- ✅ Dependency lockfile (`requirements-lock.txt` for reproducibility)

**Planned (not implemented yet):**
- `skillops review` (AI code review gate)

---

## Daily Operations

### Morning Preflight Check

```bash
# Before starting work
skillops doctor

# Should output all checks green ✓
```

### Run the Learning Workflow

```bash
# Interactive 9-step menu
skillops start

# Or specific mode
skillops start --mode learning   # Steps 1-3 (morning)
skillops start --mode engineering  # Steps 4-9 (afternoon)
```

### View Daily Metrics

```bash
# Last 24 hours
skillops metrics --hours 24

# Last week
skillops metrics --hours 168

# Shows: incidents generated, incidents completed, chaos events, time coding, cards reviewed
```

### Send Notifications (Optional)

```bash
# Send end-of-day summary to Telegram
skillops notify --storage-path storage --respect-schedule

# Or custom time
TELEGRAM_SCHEDULE_TIME=20:00 skillops notify --storage-path storage
```

---

## Backups & Recovery

### Automated Daily Backups (Recommended)

```bash
# Add to crontab -e:
0 23 * * * bash /path/to/SkillOps/setup/backup/backup.sh
```

This creates daily snapshots at 23:00 local time:
```bash
~/.local/share/skillops/backups/skillops_20250212_230015.db
~/.local/share/skillops/backups/skillops_20250211_230012.db
# ... (kept for 14 days by default)
```

### Manual Backup (Before Major Changes)

```bash
bash setup/backup/backup.sh

# Verify it was created
ls -lah ~/.local/share/skillops/backups/ | head -3
```

### Restore from Backup

```bash
# List available backups
ls -lah ~/.local/share/skillops/backups/

# Restore a specific one
bash setup/backup/restore.sh ~/.local/share/skillops/backups/skillops_20250210_230000.db

# Verify
skillops doctor
skillops metrics --hours 1
```

### Backup Configuration

```bash
# Override retention (default: 14 days)
export SKILLOPS_BACKUP_RETENTION_DAYS=30
bash setup/backup/backup.sh

# Override storage location
export STORAGE_PATH=/mnt/external/skillops
bash setup/backup/backup.sh
```

---

## Data Management

### Export Your Data

```bash
# Full JSON snapshot (backup format)
skillops export --format json --output backups/skillops_manual_$(date +%Y%m%d).json

# CSV for analysis in Excel
skillops export --format csv --output exports/

# Archive monthly
skillops export --format json --output archives/skillops_$(date +%Y%m).json
```

### Import Data

```bash
# Restore from exported JSON
skillops import-data backups/skillops_manual_20250212.json

# Merge instead of replace
skillops import-data backups/skillops_manual_20250212.json --merge

# Auto-backup before importing
skillops import-data backups/skillops_manual_20250212.json  # --no-backup to skip
```

### Migrate from Legacy Format

If you have old JSON files from previous versions:

```bash
# Auto-migrate .progress.json, formation_log.json, reinforce_progress.json
skillops migrate

# Data is imported to SQLite, old files kept as backup
```

---

## Data Retention & Cleanup

### View Current Storage

```bash
# Database size
du -sh ~/.local/share/skillops/skillops.db

# What's stored
skillops metrics --hours 24
# Shows exact counts: incidents, postmortems, performance_metrics, chaos_events
```

### Clean Up Old Data (On-Demand)

```bash
# Remove data older than 30 days
skillops retention --days 30

# Also optimize database (VACUUM)
skillops retention --days 30 --vacuum
```

### What Gets Cleaned

- **Performance metrics** (WakaTime records, study time)
- **Chaos events** (generated incidents, chaos monkey runs)
- **Resolved incidents** (completed on-call scenarios)

### Schedule Monthly Cleanup

```bash
# In crontab -e (runs 1st of month at 00:00):
0 0 1 * * cd /path/to/SkillOps && skillops retention --days 90 --vacuum
```

---

## Observability

### Health Checks

```bash
# Full system diagnostics
skillops doctor

# Checks:
# ✓ Configuration files (.env, ~/.config/skillops/skillops.env)
# ✓ Database connectivity + schema version
# ✓ Foreign key constraints enabled
# ✓ WAL mode active
# ✓ Keyring backend (if SKILLOPS_USE_KEYRING=true)
# ✓ API credentials (Gemini, WakaTime, GitHub, Telegram)
# ✓ Storage write access
# ✓ Backup directory
```

### Metrics & Statistics

```bash
# Real-time stats
skillops metrics --hours 24

# Weekly review
skillops metrics --hours 168

# Sample output:
# Incidents: 5 generated, 3 completed
# Chaos events: 2 (level 1: 1, level 2: 1)
# Performance metrics: 24 (hourly coding records)
# Flashcards: 12 reviewed
```

### Logging

```bash
# Default: human-readable text
skillops start

# Structured JSON logging (for log aggregation)
export SKILLOPS_LOG_FORMAT=json
skillops start 2>&1 | tee logs/$(date +%Y%m%d_%H%M%S).log

# Parse JSON logs
cat logs/*.log | jq '.level, .message'
```

---

## Secrets Management

### OS Keyring (Recommended - Secure)

```bash
# Enable keyring backend
export SKILLOPS_USE_KEYRING=true

# Store secrets securely in OS
skillops secret-set GEMINI_API_KEY
# Prompts: Enter value [hidden], Confirm [hidden]

skillops secret-set WAKATIME_API_KEY
skillops secret-set GITHUB_TOKEN
skillops secret-set TELEGRAM_BOT_TOKEN

# List stored secrets (values hidden)
skillops secret-list

# Remove if needed
skillops secret-unset GITHUB_TOKEN
```

### Local .env File (For Development)

```bash
# Create and protect
cat > .env << EOF
GEMINI_API_KEY=AIza...
WAKATIME_API_KEY=waka_...
EOF

chmod 600 .env
```

### Per-User Config Directory

```bash
# Store in ~/.config/skillops/ (persists across sessions)
mkdir -p ~/.config/skillops
cat > ~/.config/skillops/skillops.env << EOF
GEMINI_API_KEY=AIza...
GITHUB_TOKEN=ghp_...
EOF

chmod 600 ~/.config/skillops/skillops.env
```

---

## Incident & Post-Mortem Workflow

### Generate Test Incidents

```bash
# Dry-run (no data saved)
skillops oncall --dry-run

# Generate real incident
skillops oncall

# Shows:
# - Incident description
# - Severity level
# - Hints (progressive disclosure)
# - Validation questions
# - Post-mortem template
```

### Post-Mortem Documentation

```bash
skillops post-mortem

# Generates structured format:
# - Timeline
# - Root cause analysis
# - Prevention measures
# - Follow-up actions
```

### Track Incidents in Database

```bash
# View all incidents
sqlite3 ~/.local/share/skillops/skillops.db

sqlite> SELECT id, severity, created_at, status FROM incidents LIMIT 5;
sqlite> SELECT count(*) FROM postmortems;
```

---

## Chaos Operations (Local Only)

### Purpose

Validate self-healing capabilities, observability, and incident response procedures.

### Levels

- **Level 1** (safe): Read-only, network emulation
- **Level 2** (moderate): Write operations, requires root
- **Level 3** (destructive): Process termination, requires `--allow-dangerous`

### Usage

```bash
# Dry-run (safe preview)
skillops chaos --level 1

# Execute chaos
skillops chaos --level 1 --execute

# Generate events (stored in chaos_events table)
skillops chaos --level 2 --execute

# Dangerous (requires confirmation)
skillops chaos --level 3 --execute --allow-dangerous

# View results
skillops metrics --hours 1
sqlite3 ~/.local/share/skillops/skillops.db "SELECT * FROM chaos_events;"
```

### Best Practices

- Run during lab sessions, not during critical work
- Pair with `skillops metrics` to observe recovery
- Review `chaos_events` in database for evidence
- Keep logs for post-mortem analysis

---

## Automation

### Cron Jobs (Recommended)

```bash
# Daily backup (23:00)
0 23 * * * bash /path/to/SkillOps/setup/backup/backup.sh

# Daily notifications (20:00)
0 20 * * * cd /path/to/SkillOps && skillops notify --storage-path storage --respect-schedule

# Monthly cleanup (1st at 00:00)
0 0 1 * * cd /path/to/SkillOps && skillops retention --days 90 --vacuum

# Weekly metrics export (Sunday at 23:59)
59 23 * * 0 cd /path/to/SkillOps && skillops export --format json --output archives/skillops_$(date +\%Y\%m%d).json
```

### Systemd Timers (Alternative)

See [../setup/systemd/](../setup/systemd/) for systemd unit files and timers.

```bash
systemctl --user enable skillops.timer
systemctl --user start skillops.timer
systemctl --user status skillops.timer
```

---

## Dependencies & Reproducibility

### Locked Dependency File

For reproducible installs across environments:

```bash
# Install exact pinned versions
pip install -r requirements-lock.txt

# Verify exact versions installed
pip freeze | head -10
```

### Update Dependencies (When Needed)

```bash
# Upgrade packages
pip install --upgrade -r requirements.txt

# Regenerate lockfile
pip freeze > requirements-lock.txt

# Commit updated lockfile
git add requirements-lock.txt
git commit -m "chore: Update dependency lockfile"
```

---

## Troubleshooting

### Database Issues

| Problem | Solution |
|---------|----------|
| "Database locked" | Kill processes: `pkill -f skillops` |
| "Disk full" | Clean old data: `skillops retention --days 30 --vacuum` |
| "Schema mismatch" | Restore backup: `bash setup/backup/restore.sh <backup_file>` |

### Backup Issues

| Problem | Solution |
|---------|----------|
| "Backup failed" | Check permissions: `chmod 755 ~/.local/share/skillops` |
| "No backups found" | Run manual: `bash setup/backup/backup.sh` |
| "Restore failed" | Verify file exists: `ls -la ~/.local/share/skillops/backups/` |

### API Issues

| Problem | Solution |
|---------|----------|
| "API key not found" | Set via keyring: `skillops secret-set GEMINI_API_KEY` |
| "Connection timeout" | Check network: `ping aistudio.google.com` |
| "Rate limit" | Wait 1 minute, then retry (exponential backoff auto-applies) |

---

## Configuration Reference

| Variable | Default | Purpose |
|----------|---------|---------|
| `SKILLOPS_STORAGE_PATH` | `~/.local/share/skillops` | SQLite database location |
| `SKILLOPS_USE_KEYRING` | `false` | Enable OS keyring for secrets |
| `SKILLOPS_LOG_FORMAT` | `text` | `text` or `json` |
| `SKILLOPS_DAY_START_HOUR` | `4` | Hour when streaks reset (0-23) |
| `SKILLOPS_BACKUP_RETENTION_DAYS` | `14` | Keep backups for N days |
| `SKILLOPS_RETENTION_DAYS` | `90` | Clean data older than N days |

---

## Next Steps

1. **Setup automated backups**: Add to crontab
2. **Run daily health checks**: `skillops doctor`
3. **View metrics**: `skillops metrics --hours 24`
4. **Review backups**: `ls -lah ~/.local/share/skillops/backups/`
5. **Read deployment guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
6. **Security setup**: [SECURITY.md](SECURITY.md)
