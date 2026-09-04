#!/usr/bin/env bash
# Rotate world backups: keep the NEWEST 3 plus one archive per month.
# Usage: ./scripts/rotate_backups.sh [backups_dir]
set -euo pipefail

BACKUP_DIR="${1:-$(dirname "$0")/../backups}"

if [[ ! -d "$BACKUP_DIR" ]]; then
  echo "backup dir not found: $BACKUP_DIR" >&2
  exit 1
fi

# newest-first list of backup directories
mapfile -t all < <(ls -1dt "$BACKUP_DIR"/world_backup_*/ 2>/dev/null || true)

if (( ${#all[@]} <= 4 )); then
  echo "only ${#all[@]} backups, nothing to rotate"
  exit 0
fi

declare -A keep
for ((i = 0; i < 3 && i < ${#all[@]}; i++)); do
  keep["${all[i]}"]=1
done
# monthly archive: the oldest backup of each calendar month stays forever
for d in "${all[@]}"; do
  date_part=$(basename "$d" | sed -E 's/^world_backup_([0-9]{8})_.*/\1/')
  month="${date_part:0:6}"
  if [[ -n "$month" && -z "${monthly[$month]:-}" ]]; then
    monthly[$month]=1
    keep["$d"]=1
  fi
done

echo "keeping:"
for d in "${all[@]}"; do
  if [[ -n "${keep[$d]:-}" ]]; then
    echo "  KEEP $(basename "$d")"
  else
    echo "  DROP $(basename "$d")"
    rm -rf "$d"
  fi
done
