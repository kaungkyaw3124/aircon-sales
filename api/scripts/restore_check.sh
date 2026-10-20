#!/bin/bash
# Restores a dump into a scratch DB, compares row counts of every table with the live aircon DB, drops the scratch DB.
# Never touches aircon or aircon_test. Usage: restore_check.sh <dump>
set -euo pipefail

DUMP="${1:?usage: restore_check.sh <dump>}"
[ -f "$DUMP" ] || { echo "no such file: $DUMP" >&2; exit 1; }
SCRATCH=aircon_restore_check
psql() { docker exec -i -e PGOPTIONS=--client-min-messages=warning aircon-db psql -U aircon -v ON_ERROR_STOP=1 -X -q "$@"; }
counts() {  # "table|rows" for every public table of database $1
  echo "SELECT format('SELECT %L, count(*) FROM %I', tablename, tablename) FROM pg_tables
        WHERE schemaname = 'public' \gexec" | psql -d "$1" -At | tr '|' ' ' | LC_ALL=C sort
}

drop_scratch() { psql -d postgres -c "DROP DATABASE IF EXISTS $SCRATCH WITH (FORCE)"; }
trap drop_scratch EXIT
drop_scratch
psql -d postgres -c "CREATE DATABASE $SCRATCH"
docker exec -i aircon-db pg_restore -U aircon -d "$SCRATCH" --no-owner --exit-on-error < "$DUMP"

live=$(counts aircon)
restored=$(counts "$SCRATCH")
printf '%-22s %10s %10s\n' table aircon restored
LC_ALL=C join -a1 -a2 -e MISSING -o 0,1.2,2.2 <(echo "$live") <(echo "$restored") | while read -r t a r; do
  printf '%-22s %10s %10s %s\n' "$t" "$a" "$r" "$([ "$a" = "$r" ] && echo OK || echo DIFF)"
done
if [ "$live" = "$restored" ]; then
  echo "restore check OK: all row counts match"
else
  echo "restore check FAILED: row counts differ (live data may also have changed since the dump)" >&2
  exit 1
fi
