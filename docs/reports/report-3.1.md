# Report 3.1

## 1. Goal
3.1 — Production-ready container

## 2. Status
DONE

## 3. Checks
| Check | Result | Command |
|---|---|---|
| Image has no pytest/schemathesis | PASS (0 matches; httpx and hypothesis also absent) | `docker compose build api` then `docker run --rm aircon-api pip list \| grep -ciE "pytest\|schemathesis"` |
| down/up: both containers healthy, `/health` OK | PASS (`healthy healthy`, `{"status":"ok"}`) | `docker compose down && docker compose up -d`, `docker inspect -f '{{.State.Health.Status}}' aircon-api aircon-db`, `curl 127.0.0.1:8000/health` |
| Data still there | PASS (all 8 tables same counts: customers 60, products 41, sale_item_serials 181, sale_items 1051, sales 499, users 5, voided_sale_serials 3, alembic_version 1) | row count of every table before and after, `diff` identical |
| Login + `/dashboard/today` via curl | PASS (login 200 → dashboard 200, wrong password 401) | `curl -X POST /auth/login …`, `curl -H "Authorization: Bearer …" /dashboard/today` |
| Empty DB is migrated on start | PASS: log shows `Running upgrade  -> 0001`, all tables + `alembic_version=0001` created; scratch DB dropped after | `CREATE DATABASE aircon_migrate_test`, `docker run … -e DATABASE_URL=…/aircon_migrate_test aircon-api`, `\dt`, then `docker rm -f` + `DROP DATABASE` |
| Failed migration → container exits non-zero | PASS (`exit=1` against a missing DB) | `docker run … DATABASE_URL=…/does_not_exist aircon-api`, `docker inspect -f '{{.State.ExitCode}}'` |
| Logs show request lines, no `password`/`Bearer` values | PASS (4 request lines, 0 matches for `password\|bearer\|owner123\|wrong-pass`, 0 matches for the token) | `docker compose logs api \| grep -ciE …` |
| All tests pass | PASS: `64 passed` three runs in a row (~38 s) | `cd api && .venv/bin/pytest -q` |

Sample log lines:
```
aircon-api  | 2026-10-20 20:29:15,757 INFO app.access POST /auth/login 200 477.2ms
aircon-api  | 2026-10-20 20:29:15,830 INFO app.access GET /dashboard/today 200 26.4ms
aircon-api  | 2026-10-20 20:29:16,293 INFO app.access POST /auth/login 401 403.3ms
```

## 4. What changed
- `api/requirements.txt`: runtime deps only.
- `api/requirements-dev.txt` (new): `-r requirements.txt` + pytest, httpx, PyYAML, schemathesis.
- `api/docker/entrypoint.sh` (new): `alembic upgrade head` (with `set -e`), then `exec uvicorn` with 2 workers, `--proxy-headers`, no `--reload`, uvicorn's own access log off.
- `api/Dockerfile`: runs the entrypoint.
- `api/.dockerignore`: also leaves out `tests/`, `.hypothesis`, `requirements-dev.txt`.
- `api/docker-compose.yml`: healthcheck on `api` calling `/health` with Python's urllib (the slim image has no curl).
- `api/app/main.py`: logging to stdout + middleware that logs `METHOD /path STATUS ms`, one line per request.
- `api/app/auth.py`: two login 500s fixed (see Decisions).
- `api/tests/test_request_log.py` (new): request lines are logged, `/health` is not, and the password and token never appear.
- `api/tests/test_auth.py`: 2 new tests, password > 72 bytes → 401 and NUL in username → 401.
- `api/README.md`: dev install uses `requirements-dev.txt`; new "Container" section.

## 5. Decisions I made
- **Two login bugs found by Schemathesis while running the tests; fixed so "all tests pass" holds.** They were already there (random inputs found them this run):
  a password longer than 72 bytes (bcrypt raises) and a username containing a NUL byte (Postgres raises) both gave **500**.
  Both now give the normal 401 `invalid_credentials`. No contract change.
- The request log has the **path only**. There is no query string, no headers and no body, so tokens and passwords can't leak by design.
- **`/health` is not logged.** The Docker healthcheck calls it every 10 s, which would add ~8,600 noise lines a day.
- uvicorn's own access log is turned off (`--no-access-log`) so there is exactly one line per request (ours, with duration).
- `--forwarded-allow-ips '*'`: the API port is published on 127.0.0.1 only, and Docker's proxy hides the real source,
  so trusting only 127.0.0.1 would ignore any front proxy. Revisit in 3.4 when the real proxy is chosen.
- Log timestamps are **UTC** (container time). Business dates are still Yangon in the API.
- Migration proof used a scratch database `aircon_migrate_test` (created and dropped), not `aircon_test`.

## 6. Questions for the owner
None.

## 7. Not checked / risks
- `CLAUDE.md` "Commands → API" still says `pip install -r requirements.txt` for the venv. The tests need `requirements-dev.txt` now.
  I didn't edit `CLAUDE.md`; the planner may want to update that line.
- With 2 workers, any future in-memory state (e.g. a login rate limiter for 3.3) is per worker. 3.3 should keep its counters in Postgres, or accept 2× the limit.
- The Starlette "use httpx2" deprecation warning in tests was already there before this task.

## 8. Commit
See `git log` (message: `task 3.1: production-ready container`).
