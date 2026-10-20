#!/bin/bash
# Daily backup of the aircon database: custom-format pg_dump into ~/aircon-backups, keeps the newest 14.
set -euo pipefail

DIR="${BACKUP_DIR:-$HOME/aircon-backups}"
KEEP=14
fail() { echo "$(date -Is) backup FAILED: $*" >&2; exit 1; }
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

# names sort by time (YYYY-MM-DD_HHMM), so keep the last $KEEP
ls -1 "$DIR"/aircon-*.dump | sort | head -n -"$KEEP" | xargs -r rm --
echo "$(date -Is) backup OK: $file ($(stat -c %s "$file") bytes, $(ls -1 "$DIR"/aircon-*.dump | wc -l) kept)"
