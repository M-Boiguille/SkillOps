#!/bin/bash
# SkillOps backup script
# Usage: bash setup/backup/backup.sh

set -euo pipefail

STORAGE_PATH="${STORAGE_PATH:-$HOME/.local/share/skillops}"
DB_PATH="$STORAGE_PATH/skillops.db"
BACKUP_DIR="${SKILLOPS_BACKUP_DIR:-$STORAGE_PATH/backups}"
RETENTION_DAYS="${SKILLOPS_BACKUP_RETENTION_DAYS:-14}"

mkdir -p "$BACKUP_DIR"

if [ ! -f "$DB_PATH" ]; then
  echo "[backup] Database not found: $DB_PATH" >&2
  exit 1
fi

STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_FILE="$BACKUP_DIR/skillops_${STAMP}.db"

cp "$DB_PATH" "$BACKUP_FILE"

echo "[backup] Saved $BACKUP_FILE"

if command -v find >/dev/null 2>&1; then
  find "$BACKUP_DIR" -name "skillops_*.db" -type f -mtime "+$RETENTION_DAYS" -print -delete
  echo "[backup] Pruned backups older than $RETENTION_DAYS days"
fi
