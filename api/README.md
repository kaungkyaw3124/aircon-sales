# API

FastAPI + PostgreSQL. Runs on the VPS. See the root `CLAUDE.md` for the commands.

```
cp .env.example .env            # then set real secrets
docker compose up -d            # aircon-db on 127.0.0.1:5433, aircon-api on 127.0.0.1:8000
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/alembic upgrade head
.venv/bin/python scripts/seed.py --reset   # fake data
.venv/bin/pytest                           # uses aircon_test
```

## Fake data (dev only)

`scripts/seed.py` creates **development-only** logins: `owner` / `owner123` and `sales1`..`sales4` / `sales123`.
Never use these on a real server. `--reset` refuses to run when `APP_ENV=production`.
