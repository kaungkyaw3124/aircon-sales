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
- On start, `docker/entrypoint.sh` runs `alembic upgrade head`, then uvicorn (2 workers, `--proxy-headers`).
  If the migration fails the container exits non-zero, so no API runs on an old schema.
- Healthcheck calls `/health`; `docker ps` shows `healthy`.
- Logs (`docker compose logs api`): one line per request, `METHOD /path STATUS 12.3ms`. Path only (no query string,
  headers or body), so tokens and passwords never reach the log. `/health` is not logged (the healthcheck calls it every 10 s).
