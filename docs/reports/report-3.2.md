# Report 3.2

## 1. Goal
3.2 — Daily database backup + restore test

## 2. Status
NEEDS REVIEW (all checks pass; the task says stop for review)

## 3. Checks
| Check | Result | Command |
|---|---|---|
| `backup.sh` by hand creates a dump | PASS: `~/aircon-backups/aircon-2026-10-21_0300.dump` (38 153 bytes), folder mode `700`, file `600` | `api/scripts/backup.sh`, `stat -c %a ~/aircon-backups` |
| Keeps only 14 | PASS: 16 fake older dumps + 1 real = 17 → after one run **14**, the 3 oldest deleted, newest real dump kept | fake files `aircon-2026-09-01..16_0230.dump`, then `backup.sh`, `ls aircon-*.dump \| wc -l` |
| Backup failure → non-zero + reason | PASS: `backup FAILED: cannot create /proc/nope`, exit 1 | `BACKUP_DIR=/proc/nope api/scripts/backup.sh` |
| `restore_check.sh` same counts, exit 0 | PASS: all 8 tables match (sales 499, sale_items 1051, …), exit 0 | `api/scripts/restore_check.sh ~/aircon-backups/aircon-2026-10-21_0300.dump` |
| Scratch DB gone afterwards | PASS: databases left are `aircon, aircon_test, postgres, template0, template1` | `psql -c 'select datname from pg_database'` |
| Bad dump → non-zero, scratch DB still dropped | PASS: exit 1, `aircon_restore_check` gone | `restore_check.sh junk-file` |
| `crontab -l` shows the job | PASS (see line below) | `crontab -l` |
| Cron really runs it | PASS: a temporary entry for 20:33 UTC wrote `backup OK … aircon-2026-10-21_0303.dump` to `backup.log`; entry then removed | temporary crontab line, `cat ~/aircon-backups/backup.log` |
| "Restore for real" command in README works | PASS on a scratch DB `aircon_restore_drill`: restored twice with `--clean --if-exists` (exit 0 both), 499 sales, then dropped. **Not** run against `aircon`. | see README |
| All tests pass | PASS: `64 passed` | `cd api && .venv/bin/pytest -q` |

Crontab line:
```
# aircon daily backup: 02:30 Asia/Yangon = 20:00 UTC (server is UTC, Yangon has no DST)
0 20 * * * /home/administrator/aircon-sales/api/scripts/backup.sh >> /home/administrator/aircon-backups/backup.log 2>&1
```

restore_check output:
```
table                      aircon   restored
alembic_version                 1          1 OK
customers                      60         60 OK
products                       41         41 OK
sale_item_serials             181        181 OK
sale_items                   1051       1051 OK
sales                         499        499 OK
users                           5          5 OK
voided_sale_serials             3          3 OK
restore check OK: all row counts match
```

## 4. What changed
- `api/scripts/backup.sh` (new): `pg_dump -Fc` via `docker exec aircon-db`, writes `.part` then renames (a failed dump never looks good), keeps newest 14, clear `backup FAILED: <reason>` + exit 1.
- `api/scripts/restore_check.sh` (new): restore into `aircon_restore_check`, per-table counts side by side, exit 1 on any difference, scratch DB always dropped (trap).
- `api/README.md`: "Backups" section (both scripts, cron line, how to check the log, how to restore for real).
- User crontab (not in git): the line above.

## 5. Decisions I made
- Cron time is written as **20:00 UTC**. Ubuntu's cron has no per-job timezone, and Yangon has no DST, so this is always 02:30 Yangon.
- Dump file names use **Yangon** time (so a 02:30 backup is named for the business day it ran on).
- Retention sorts by file name (the name is the timestamp), not by modification time, so a copied/touched file can't confuse it.
- Two backups in the same minute overwrite each other (name is to the minute, as the task specifies).
- `restore_check.sh` compares with the *live* database, as asked. On a real trading day, sales made after the dump will show as `DIFF` and exit 1. That is expected; check the time of the dump.
- `BACKUP_DIR` env var overrides the folder (used only to test the failure path).

## 6. Questions for the owner
1. **Off-server copy of backups?** Right now the dumps sit on the same VPS as the database. If the VPS (or its disk/account) is lost, the backups go with it. Options: copy each dump to Google Drive / another server / the owner's PC. Which one?
2. Are **14 daily** backups enough, or do you also want e.g. one per month kept for a year?

## 7. Not checked / risks
- Nobody is alerted if the nightly backup fails. It only writes to `backup.log`. Worth adding a check (e.g. the app/owner sees "last backup" age) later.
- The "restore for real" steps were rehearsed on a scratch DB only, not on `aircon`.
- Backups are not encrypted (they're in a 700 folder on the server). Encrypt before copying them anywhere off-server.

### What is still missing before the API can be opened to the internet
1. **Login rate limiting** (3.3, D25): contract v0.1.1 with `429`. With 2 workers, keep the counters in Postgres (in-memory = per worker).
2. **HTTPS + exposure** (3.4): owner must choose the domain and Cloudflare Tunnel vs Nginx + Let's Encrypt. Then tighten
   `--forwarded-allow-ips` (now `*`) to the real proxy.
3. **`/docs`, `/redoc` and `/openapi.json` are open without a token** (all return 200 today). That breaks the rule "every endpoint except
   `/health` and `/auth/login` requires a token". Turn them off when `APP_ENV=production`.
4. **Real accounts instead of dev logins:** the DB has seeded `owner/owner123` and `sales1..4/sales123`, and the data is fake.
   Production needs `APP_ENV=production`, a clean database (no seed), real users with strong passwords, and a way to create them
   (there is no "create user" script yet).
5. **Fresh production secrets:** new `POSTGRES_PASSWORD` and `JWT_SECRET` when the real data starts.
6. **Off-server backup copy** (question 1 above) and an alert when a backup fails.
7. **Docker log rotation:** `aircon-api` uses the `json-file` driver with no size limit. Add `max-size`/`max-file` in compose so logs can't fill the disk.
8. Token lifetime is 24 h with no logout/revoke. A stolen token works until it expires. OK for now? (business call)

## 8. Commit
See `git log` (message: `task 3.2: daily database backup + restore test`).
