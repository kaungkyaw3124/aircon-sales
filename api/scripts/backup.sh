#!/bin/bash
# Daily backup of the aircon database: custom-format pg_dump into ~/aircon-backups.
# Keeps the newest 14, plus the first dump of each of the last 12 months (D31).
# Writes LAST_OK (timestamp) on success, LAST_FAILED (timestamp + reason) on failure.
set -euo pipefail

DIR="${BACKUP_DIR:-$HOME/aircon-backups}"
KEEP=14
fail() {
  echo "$(date -Is) backup FAILED: $*" >&2
  echo "$(date -Is) $*" > "$DIR/LAST_FAILED" 2>/dev/null || true
  exit 1
}
trap 'fail "command failed on line $LINENO"' ERR

mkdir -p "$DIR" || fail "cannot create $DIR"
chmod 700 "$DIR"
file="$DIR/aircon-$(TZ=Asia/Yangon date +%Y-%m-%d_%H%M).dump"
tmp="$file.part"

# write to .part first so a failed dump never looks like a good one
docker exec aircon-db pg_dump -U aircon -d aircon -Fc > "$tmp" || { rm -f "$tmp"; fail "pg_dump failed"; }
[ -s "$tmp" ] || { rm -f "$tmp"; fail "dump is empty"; }
mv "$tmp" "$file"
chmod 600 "$file"

# names sort by time (YYYY-MM-DD_HHMM): keep the last $KEEP, and the first of each of the last 12 months
all=$(ls -1 "$DIR"/aircon-*.dump | sort)
keep=$(echo "$all" | tail -n "$KEEP"; echo "$all" | awk '{m = substr($0, length($0) - 19, 7)} !seen[m]++' | tail -n 12)
echo "$all" | { grep -vxF -f <(echo "$keep") || true; } | xargs -r rm --
date -Is > "$DIR/LAST_OK"
rm -f "$DIR/LAST_FAILED"
echo "$(date -Is) backup OK: $file ($(stat -c %s "$file") bytes, $(ls -1 "$DIR"/aircon-*.dump | wc -l) kept)"
