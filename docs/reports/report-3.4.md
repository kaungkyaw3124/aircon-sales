# Report 3.4

## 1. Goal
Task 3.4 — Production hardening

## 2. Status
DONE

## 3. Checks

| Check | Result | Command |
|---|---|---|
| `APP_ENV=production`: `/docs`, `/redoc`, `/openapi.json` → 404 in the shared error shape | PASS | `pytest tests/test_production.py::test_docs_off_in_production` (fresh process with `APP_ENV=production`) |
| Dev: the same three → 200 | PASS | `…::test_docs_on_in_development` (3 cases); live dev container `curl /docs` → 200 |
| `create_user.py` creates a user who can log in | PASS | `…::test_create_user_can_log_in` |
| Refuses a short password | PASS | `…::test_create_user_refuses_bad_password` (short, and mismatched second entry) |
| `--deactivate` → login 401 | PASS | `…::test_deactivate_makes_login_fail` |
| Password never in the process arguments | PASS | `…::test_password_cannot_be_given_as_argument` (`--password` is rejected by argparse, exit 2); all tests feed it via the hidden prompt and check it's not echoed |
| `docker inspect aircon-api` shows the log options | PASS | `docker inspect -f '{{json .HostConfig.LogConfig}}' aircon-api aircon-db` → `{"Type":"json-file","Config":{"max-file":"5","max-size":"10m"}}` for both |
| Containers healthy after `docker compose up -d` | PASS | `docker compose up -d --build`; both `healthy`, `/health` ok |
| Backup retention with fake files: 14 newest + first-of-month for 12 months, rest deleted | PASS | `…::test_backup_retention_daily_and_monthly` (499 fake daily dumps, fake `docker` on PATH) |
| All tests pass | PASS — 85 passed in 79 s | `cd api && .venv/bin/pytest -q` |

Also: `…::test_backup_failure_writes_last_failed`, `…::test_update_changes_password_and_role`;
`docker exec aircon-api python scripts/create_user.py --help` works in the image; one real `backup.sh` run wrote `LAST_OK`.

## 4. What changed
- `api/app/main.py` — docs/redoc/openapi URLs set to `None` when `APP_ENV=production`.
- `api/docker-compose.yml` — `json-file` logging, `max-size: 10m`, `max-file: 5`, on both services.
- `api/scripts/create_user.py` — new: create/update/deactivate a user, hidden double prompt, ≥ 10 chars.
- `api/scripts/backup.sh` — monthly retention (D31), `LAST_OK` / `LAST_FAILED`.
- `api/tests/test_production.py` — 12 tests for the above.
- `api/README.md` — Users, Production mode, backup retention and status files.

## 5. Decisions I made
- `create_user.py` on an existing user: `--full-name`/`--role` optional (kept if not given), always asks a new password,
  and **re-activates** the user. `--deactivate` asks no password and fails if the user doesn't exist.
- Password also refused above 72 bytes (bcrypt's limit; such a password could never log in).
- `LAST_OK` stays after a failure (it still says when the last good backup was); `LAST_FAILED` is removed by the next good backup.
  So "is `LAST_FAILED` there?" = "did the last run fail?".
- "Last 12 months" = the 12 newest months that have a dump. With a daily cron that's the same as the last 12 calendar months;
  if backups stopped for a while, older monthlies are kept rather than deleted.
- The rate-limit proxy setting from 3.3 already removed `--forwarded-allow-ips '*'` (the "tighten in 3.4" note).

## 6. Questions for the owner
None new. (Off-site backup location is still open from D31 → task 3.7.)

## 7. Not checked / risks
- The "password not in process arguments" check proves the script has no way to take one; it does not inspect `ps` of a live run.
- Recreating the containers for the log options restarted Postgres (dev data only, volume kept, healthy after).
- Nothing watches `LAST_FAILED` yet; someone has to look (or 3.5/3.7 can add an alert).

## 8. Commit
See `git log` (message: `task 3.4: production hardening`).
