# Deployment & Rollback

## Deployment Checklist

1. **Update code**
   - Pull latest changes and install dependencies.
2. **Preflight**
   - Run `skillops doctor`.
3. **Run tests**
   - `pytest -v` (or CI status green).
4. **Enable automation**
   - systemd timer or cron job.
5. **Smoke checks**
   - `skillops version`
   - `skillops doctor`
   - `pytest -v tests/smoke`

**Note:** Chaos is **local-only**. Do not enable `skillops chaos --execute` in production.

## Rollback Procedure

1. Stop automation:
   - `systemctl --user stop skillops.timer` (or disable cron)
2. Restore last known good backup:
   - `bash setup/backup/restore.sh ~/.local/share/skillops/backups/skillops_YYYYmmdd_HHMMSS.db`
3. Verify:
   - `skillops doctor`
4. Restart automation:
   - `systemctl --user start skillops.timer`

## Release Strategy

- **CI/CD mandatory**: lint → tests → build → release
- Tag releases as `vX.Y.Z` and publish from the release workflow.
