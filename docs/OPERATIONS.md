# Operations Guide

## Current Status

**In production use (local/dev):**
- SQLite state + exports
- Backups/restore scripts
- Logging + alerting hooks
- Chaos Monkey (local) via `skillops chaos`
- `skillops oncall` (incident simulation)
- `skillops post-mortem` (incident write-ups)

**Planned (not implemented yet):**
- `skillops review` (automated code review gate)

## Backups

SkillOps stores all state in SQLite: storage/skillops.db.

### Manual backup

- Copy the database file:
  - storage/skillops.db

### Automated backup (recommended)

Use the provided script:

- [../setup/backup/backup.sh](../setup/backup/backup.sh)

Make it executable:

- `chmod +x setup/backup/backup.sh setup/backup/restore.sh`

Configuration (optional):

- `STORAGE_PATH` (default: ~/.local/share/skillops)
- `SKILLOPS_BACKUP_DIR` (default: $STORAGE_PATH/backups)
- `SKILLOPS_BACKUP_RETENTION_DAYS` (default: 14)

### Export snapshots

- JSON/CSV exports are provided via:
  - skillops export --format json --output ./exports/skillops_export.json
  - skillops export --format csv --output ./exports/

## Restore

- Restore the SQLite file from backup:
  - Replace storage/skillops.db with your backup

- Or import from export snapshots:
  - skillops import-data ./exports/skillops_export.json

### Automated restore

- [../setup/backup/restore.sh](../setup/backup/restore.sh)

Example:

- `bash setup/backup/restore.sh ~/.local/share/skillops/backups/skillops_YYYYmmdd_HHMMSS.db`

## Migration (legacy JSON → SQLite)

If you have old JSON files (.progress.json, formation_log.json, reinforce_progress.json):

- skillops migrate

## Logging

### Text logs (default)

- SKILLOPS_LOG_FORMAT=text

### JSON logs

- SKILLOPS_LOG_FORMAT=json

## Alerting

SkillOps can send alerts on failures.

Environment variables:

- `SKILLOPS_ALERT_TYPE` = email|webhook|both
- `SKILLOPS_ALERT_RECIPIENTS` (comma-separated)
- `SKILLOPS_ALERT_SMTP_HOST`, `SKILLOPS_ALERT_SMTP_PORT`
- `SKILLOPS_ALERT_SMTP_USER`, `SKILLOPS_ALERT_SMTP_PASS`
- `SKILLOPS_ALERT_WEBHOOK_URL`

## Dependency Lockfile

For reproducible installs, use the lockfile:

```
pip install -r requirements-lock.txt
```

Update it after dependency changes:

```
python -m pip freeze | sort > requirements-lock.txt
```

## Data Retention (optional)

By default, no data is deleted. To enable cleanup of old records on startup:

```
export SKILLOPS_RETENTION_DAYS=90
export SKILLOPS_RETENTION_RUN_ON_START=true
```

Manual cleanup (recommended for cron/systemd):

```
skillops retention --days 90 --vacuum
```

This will purge old:
- performance metrics
- chaos events
- resolved incidents

## Day boundary (streaks)

- SKILLOPS_DAY_START_HOUR=4
- Set to local preference (0–23)

## Preflight checks

- skillops doctor

Verifies:
- Environment variables
- Storage write access
- SQLite connectivity
- Optional Gemini dependency

## Restore tests

Recommended monthly procedure:

1. Create a fresh backup with `setup/backup/backup.sh`
2. Restore to a temporary location (copy the backup to a test storage path)
3. Run `skillops doctor`
4. Run a read-only command (`skillops version`)

## Chaos Operations (Local Only)

**Purpose:** validate self-healing and observability.

Guidelines:
- Default is **dry-run**; use `--execute` to apply changes.
- Level 2/3 require **root** privileges.
- Level 3 requires `--allow-dangerous`.

Recommended usage:
- Run during lab sessions, not in production.
- Pair with monitoring to observe recovery signals.
- Review `chaos_events` in SQLite for evidence.
