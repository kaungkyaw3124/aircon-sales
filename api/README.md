# API

FastAPI + PostgreSQL. Runs on the VPS. See the root `CLAUDE.md` for the commands.

```
cp .env.example .env            # then set real secrets
docker compose up -d            # aircon-db on 127.0.0.1:5433, aircon-api on 127.0.0.1:8000
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt   # dev = runtime + test tools
.venv/bin/alembic upgrade head
.venv/bin/python scripts/seed.py --reset   # fake data
.venv/bin/pytest                           # uses aircon_test
```

## Fake data (dev only)

`scripts/seed.py` creates **development-only** logins: `owner` / `owner123` and `sales1`..`sales4` / `sales123`.
Never use these on a real server. `--reset` refuses to run when `APP_ENV=production`.

## Container

- The image installs `requirements.txt` only (runtime). Test tools live in `requirements-dev.txt`.
- On start, `docker/entrypoint.sh` runs `alembic upgrade head`, then uvicorn (2 workers, `--no-proxy-headers`:
  the app itself reads `X-Forwarded-For`, and only from IPs listed in `TRUSTED_PROXIES`).
  If the migration fails the container exits non-zero, so no API runs on an old schema.
- Healthcheck calls `/health`; `docker ps` shows `healthy`.
- Logs (`docker compose logs api`): one line per request, `METHOD /path STATUS 12.3ms`. Path only (no query string,
  headers or body), so tokens and passwords never reach the log. `/health` is not logged (the healthcheck calls it every 10 s).

## Users

`scripts/create_user.py` creates or updates a login. It changes one user and deletes nothing, so it works in production.
The password is typed twice at a hidden prompt (at least 10 characters), never on the command line.
```
docker exec -it aircon-api python scripts/create_user.py --username owner --full-name "U Kyaw Kyaw" --role owner
docker exec -it aircon-api python scripts/create_user.py --username sales1 --role sales     # update: new password, role
docker exec -it aircon-api python scripts/create_user.py --username sales1 --deactivate    # can't log in any more
```
A new user needs `--full-name` and `--role`. Setting a new password also re-activates a deactivated user.
(From the venv instead of the container: `.venv/bin/python scripts/create_user.py …`, uses `DATABASE_URL` from `.env`.)

## Production mode

With `APP_ENV=production`: `/docs`, `/redoc` and `/openapi.json` answer 404 (they need no token, so they're off);
`seed.py --reset` refuses to run. Docker keeps at most 5 × 10 MB of logs per container.

## Login rate limit

5 failed logins per username, or 20 per client IP, in 15 minutes → `429 rate_limited` with `Retry-After` (D30).
Counts live in the `login_failures` table. To unlock someone early:
`docker exec aircon-db psql -U aircon -d aircon -c "delete from login_failures where username='<name>'"`.

Behind a reverse proxy on this host, requests reach the container from the Docker gateway (`172.19.0.1`);
set `TRUSTED_PROXIES=172.19.0.1` then, or every client shares one IP counter.

## Backups

`scripts/backup.sh` dumps the `aircon` database (`pg_dump -Fc` inside `aircon-db`) to
`~/aircon-backups/aircon-YYYY-MM-DD_HHMM.dump` (Yangon time; folder mode 700, files 600, outside the repo).
It keeps the newest 14 dumps plus the first dump of each of the last 12 months (D31), and exits non-zero with a
`backup FAILED: <reason>` line on any error.
After a good backup it writes the time to `~/aircon-backups/LAST_OK` and removes `LAST_FAILED`; after a failure it writes
`LAST_FAILED` (time + reason) and leaves `LAST_OK` alone. Quick check: `cat ~/aircon-backups/LAST_OK; ls ~/aircon-backups/LAST_FAILED`.

It runs daily at 02:30 Yangon from the `administrator` user's crontab (the server clock is UTC; Yangon is UTC+6:30, no DST):
```
0 20 * * * /home/administrator/aircon-sales/api/scripts/backup.sh >> /home/administrator/aircon-backups/backup.log 2>&1
```
Check it: `tail ~/aircon-backups/backup.log`.

`scripts/restore_check.sh <dump>` proves a dump is usable: it restores it into a scratch database `aircon_restore_check`,
prints the row count of every table next to the live `aircon` counts, then drops the scratch database.
Exit 0 only if every count matches (on a busy day, sales made after the dump will show as a difference).
It never touches `aircon` or `aircon_test`.

### Restore for real (replaces all current data)

Only do this when the live data is lost or broken. Run `backup.sh` first, so today's state is kept too.
```
cd ~/aircon-sales/api
./scripts/restore_check.sh ~/aircon-backups/<dump>          # 1. make sure the dump is good
docker compose stop api                                      # 2. nothing writes while restoring
docker exec -i aircon-db pg_restore -U aircon -d aircon --clean --if-exists --no-owner --exit-on-error \
  < ~/aircon-backups/<dump>                                  # 3. replace the data
docker compose start api                                     # 4. migrations run on start, then the API
curl -s 127.0.0.1:8000/health
```
If the dump is from an older schema, the API's start-up `alembic upgrade head` brings it up to date.
