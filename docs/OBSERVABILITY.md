# Observability & Monitoring

> **SkillOps provides built-in metrics, logging, and database-level observability.**

---

## Quick Start

```bash
# View last 24 hours of metrics
skillops metrics --hours 24

# Weekly summary
skillops metrics --hours 168

# Health check
skillops doctor
```

---

## Metrics Command

### Real-Time Statistics

```bash
# Last 24 hours
skillops metrics --hours 24

# Output:
# Incidents: 5 generated, 3 completed
# Chaos events: 2 (level 1: 1, level 2: 1)
# Performance metrics: 24 (hourly coding records)
# Flashcards: 12 reviewed

# Last week
skillops metrics --hours 168

# Specific period
skillops metrics --hours 72
```

### What Gets Measured

- **Incidents**: Generated and completed on-call scenarios
- **Chaos events**: Generated incidents from chaos monkey
- **Performance metrics**: Coding time, learning time
- **Flashcards**: Cards reviewed via Anki
- **Study sessions**: Time spent per activity

---

## Logging

### Text Logs (Default)

```bash
# Human-readable output
export SKILLOPS_LOG_FORMAT=text

# Run a workflow
skillops start
```

### JSON Logs (Structured)

```bash
# Machine-readable JSON output
export SKILLOPS_LOG_FORMAT=json

# Capture to file
cd /path/to/SkillOps && skillops start 2>&1 | tee logs/$(date +%Y%m%d_%H%M%S).log

# Parse JSON
cat logs/*.log | jq '.level, .message'
```

### Log Configuration

| Variable | Values | Purpose |
|----------|--------|---------|
| `SKILLOPS_LOG_FORMAT` | `text` (default), `json` | Output format |
| `SKILLOPS_LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | Verbosity |

---

## Database Queries

### Performance Metrics Table

```bash
# Connect to database
sqlite3 ~/.local/share/skillops/skillops.db

# Last 24 hours of coding metrics
sqlite> SELECT * FROM performance_metrics
        WHERE timestamp >= datetime('now', '-24 hours')
        ORDER BY timestamp DESC;

# Summary by step
sqlite> SELECT step_id, COUNT(*) as count, AVG(duration_seconds) as avg_duration
        FROM performance_metrics
        GROUP BY step_id
        ORDER BY count DESC;

# Success rate
sqlite> SELECT step_id,
               SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate
        FROM performance_metrics
        WHERE timestamp >= datetime('now', '-7 days')
        GROUP BY step_id;
```

### Chaos Events Table

```bash
# Recent chaos activity
sqlite> SELECT id, level, status, created_at
        FROM chaos_events
        ORDER BY created_at DESC
        LIMIT 20;

# Chaos by level
sqlite> SELECT level, COUNT(*) as count,
               SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successes
        FROM chaos_events
        GROUP BY level;

# Recent failures
sqlite> SELECT id, level, error_message
        FROM chaos_events
        WHERE status = 'failed'
        ORDER BY created_at DESC
        LIMIT 10;
```

### Incidents & Postmortems

```bash
# Active incidents
sqlite> SELECT id, severity, title, created_at, status
        FROM incidents
        WHERE status = 'open'
        ORDER BY created_at DESC;

# Postmortem coverage
sqlite> SELECT i.id, i.title,
               CASE WHEN p.id IS NOT NULL THEN 'completed' ELSE 'missing' END as postmortem_status
        FROM incidents i
        LEFT JOIN postmortems p ON i.id = p.incident_id
        ORDER BY i.created_at DESC
        LIMIT 20;

# Incident stats
sqlite> SELECT severity, COUNT(*) as count,
               SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved
        FROM incidents
        WHERE created_at >= datetime('now', '-30 days')
        GROUP BY severity;
```

---

## Health Diagnostics

### Full System Check

```bash
skillops doctor

# Verifies:
# ✓ Configuration files found
# ✓ Database connectivity
# ✓ Schema version
# ✓ Foreign key constraints
# ✓ WAL mode enabled
# ✓ Keyring backend (if enabled)
# ✓ API credentials
# ✓ Storage write access
# ✓ Backup directory
```

### Per-Component Checks

```bash
# Database integrity
sqlite3 ~/.local/share/skillops/skillops.db "PRAGMA integrity_check;"
# Output: ok

# Schema version
sqlite3 ~/.local/share/skillops/skillops.db "SELECT version FROM _schema_version;"
# Output: 4

# Foreign keys enabled
sqlite3 ~/.local/share/skillops/skillops.db "PRAGMA foreign_keys;"
# Output: 1

# WAL mode active
sqlite3 ~/.local/share/skillops/skillops.db "PRAGMA journal_mode;"
# Output: wal
```

---

## Data Export for Analysis

### JSON Export (Complete Backup)

```bash
# Export all data
skillops export --format json --output backup_$(date +%Y%m%d).json

# Archive monthly
skillops export --format json --output archives/skillops_$(date +%Y%m).json
```

### CSV Export (For Excel/Sheets)

```bash
# Export as CSV
skillops export --format csv --output exports/

# Resulting files:
# - exports/incidents.csv
# - exports/performance_metrics.csv
# - exports/chaos_events.csv
# - exports/postmortems.csv
```

### Import and Merge

```bash
# Import exported data
skillops import-data backup_20250212.json

# Merge with existing (don't replace)
skillops import-data backup_20250212.json --merge
```

---

## Observability Stack (Optional)

### Recommended Setup

For local dev environment, SQLite + CLI is sufficient. For more advanced monitoring:

**Option 1: Grafana + SQLite**
```bash
# Install Grafana SQLite plugin
# Create panels: incidents/day, chaos success rate, coding time trend

# Query example (Grafana):
SELECT
  datetime(created_at) as time,
  COUNT(*) as count
FROM incidents
WHERE created_at >= $__timeFrom
GROUP BY datetime(created_at)
```

**Option 2: Log Aggregation (Optional)**
```bash
# If collecting JSON logs centrally:
cat logs/*.log | jq '.' > logs_archive.jsonl

# Parse for insights
jq 'select(.level == "ERROR")' logs_archive.jsonl | wc -l
```

**Option 3: Time-Series Database (Advanced)**
```bash
# Export metrics to InfluxDB (if needed later)
# Write custom script to read SQLite and push to InfluxDB
# Create Grafana dashboards on top
```

---

## Alerting (Optional)

### Email Alerts

```bash
# Configure
export SKILLOPS_ALERT_TYPE=email
export SKILLOPS_ALERT_SMTP_HOST=smtp.gmail.com
export SKILLOPS_ALERT_SMTP_PORT=587
export SKILLOPS_ALERT_SMTP_USER=your-email@gmail.com
export SKILLOPS_ALERT_SMTP_PASS=app-password
export SKILLOPS_ALERT_RECIPIENTS=your-email@gmail.com

# Test
skillops doctor  # Should send alert on error
```

### Webhook Alerts

```bash
# Send to webhook (e.g., Discord, Slack)
export SKILLOPS_ALERT_TYPE=webhook
export SKILLOPS_ALERT_WEBHOOK_URL=https://hooks.slack.com/...

# Automatic triggers: API errors, DB failures, etc.
```

### Combined Alerts

```bash
export SKILLOPS_ALERT_TYPE=both  # Email + Webhook
export SKILLOPS_ALERT_RECIPIENTS=user@example.com
export SKILLOPS_ALERT_WEBHOOK_URL=https://...
```

---

## Monitoring Checklist

### Daily

- [ ] `skillops doctor` — all green
- [ ] `skillops metrics --hours 24` — expected activity

### Weekly

- [ ] Review incident trends
- [ ] Check chaos events for anomalies
- [ ] Verify backups are being created

### Monthly

- [ ] Run full database integrity check
- [ ] Export metrics for analysis
- [ ] Rotate API keys
- [ ] Review and archive old logs

---

## Troubleshooting

### "No metrics found"

```bash
# Run a workflow first to generate data
skillops start

# Then query
skillops metrics --hours 1
```

### "Database queries slow"

```bash
# Optimize database
skillops retention --days 90 --vacuum

# Or manually
sqlite3 ~/.local/share/skillops/skillops.db "VACUUM;"
```

### "Logs not appearing"

```bash
# Check log format
echo $SKILLOPS_LOG_FORMAT  # Should be: text or json

# Enable debug logging
export SKILLOPS_LOG_LEVEL=DEBUG
skillops start
```

---

## Next Steps

1. **Daily monitoring**: `skillops metrics --hours 24`
2. **Weekly check**: Review incidents in database
3. **Monthly archive**: `skillops export --format json`
4. **Advanced**: Setup Grafana with SQLite datasource
5. **Read more**: [OPERATIONS.md](OPERATIONS.md)

Data source:

- `storage/skillops.db`

## CLI Metrics Summary

Quick summary from the CLI:

```
skillops metrics --hours 24
```
