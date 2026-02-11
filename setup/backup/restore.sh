#!/bin/bash
# SkillOps restore script
# Usage: bash setup/backup/restore.sh /path/to/skillops_YYYYmmdd_HHMMSS.db

set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 /path/to/skillops_backup.db" >&2
  exit 1
fi

BACKUP_FILE="$1"
STORAGE_PATH="${STORAGE_PATH:-$HOME/.local/share/skillops}"
DB_PATH="$STORAGE_PATH/skillops.db"

if [ ! -f "$BACKUP_FILE" ]; then
  echo "[restore] Backup file not found: $BACKUP_FILE" >&2
  exit 1
fi

mkdir -p "$STORAGE_PATH"

if [ -f "$DB_PATH" ]; then
  CURRENT_BACKUP="$DB_PATH.bak_$(date +%Y%m%d_%H%M%S)"
  cp "$DB_PATH" "$CURRENT_BACKUP"
  echo "[restore] Existing DB saved to $CURRENT_BACKUP"
fi

cp "$BACKUP_FILE" "$DB_PATH"

echo "[restore] Restored database to $DB_PATH"
