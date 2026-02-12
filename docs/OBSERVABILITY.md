# Observability

## Logging

- Default: text logs
- JSON logs: set `SKILLOPS_LOG_FORMAT=json`

## Metrics

Performance metrics are recorded in SQLite table `performance_metrics`.

Useful queries:

- Last 24h executions:
  - `SELECT * FROM performance_metrics WHERE timestamp >= datetime('now', '-24 hours');`
- Failures by step:
  - `SELECT step_id, COUNT(*) FROM performance_metrics WHERE success = 0 GROUP BY step_id;`

## Chaos Events

Chaos actions are recorded in SQLite table `chaos_events`.

Useful queries:
- Recent chaos activity:
  - `SELECT * FROM chaos_events ORDER BY timestamp DESC LIMIT 50;`
- Failures by level:
  - `SELECT level, COUNT(*) FROM chaos_events WHERE status = 'failed' GROUP BY level;`

## Alerting

Alerting is available via email/webhook.

Environment variables:

- `SKILLOPS_ALERT_TYPE` = email|webhook|both
- `SKILLOPS_ALERT_RECIPIENTS`
- `SKILLOPS_ALERT_SMTP_HOST`, `SKILLOPS_ALERT_SMTP_PORT`
- `SKILLOPS_ALERT_SMTP_USER`, `SKILLOPS_ALERT_SMTP_PASS`
- `SKILLOPS_ALERT_WEBHOOK_URL`

## Dashboards

Recommended approach:

- Use Grafana with the SQLite data source.
- Create panels for:
  - executions per step
  - success rate per step
  - average duration per step
  - daily failures

Data source:

- `storage/skillops.db`

## CLI Metrics Summary

Quick summary from the CLI:

```
skillops metrics --hours 24
```
