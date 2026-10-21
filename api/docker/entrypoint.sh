#!/bin/sh
# Migrate first; if that fails the container exits non-zero and no API runs on an old schema.
set -e
alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2 --no-proxy-headers --no-access-log
