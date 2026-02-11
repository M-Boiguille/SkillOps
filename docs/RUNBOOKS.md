# Runbooks

## Incident: SkillOps job failed

1. Check logs
   - systemd: `journalctl --user-unit=skillops.service -n 50`
   - cron: `tail -50 ~/.local/share/skillops/cron.log`
2. Run preflight
   - `skillops doctor`
3. Re-run failed step
   - `skillops start` and execute the step manually

## Incident: Database corruption / missing data

1. Stop automation
2. Restore latest backup
   - `bash setup/backup/restore.sh ~/.local/share/skillops/backups/skillops_YYYYmmdd_HHMMSS.db`
3. Validate
   - `skillops doctor`

## Incident: Telegram/GitHub/WakaTime failure

1. Verify tokens in environment
2. Re-run `skillops doctor`
3. Rotate token if needed

## Escalation

- **RTO target:** 1 hour
- **RPO target:** 24 hours
- Owner: project maintainer
