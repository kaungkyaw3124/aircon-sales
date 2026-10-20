# Report 0.4

## 1. Goal
Task 0.4 — Database + API skeleton

## 2. Status
DONE

## 3. Checks

Preflight (Step 0):

| Item | Result |
|---|---|
| `docker --version` | Docker 29.1.3 |
| `docker compose version` | 2.40.3 |
| `python3 --version` | **3.14.4** (3.12+ required; OK) |
| `node --version` | v24.22.0 |
| `free -h` | 3.3 GiB RAM (2.1 GiB available), 3.8 GiB swap |
| `df -h /` | 64 GB, 51 GB free |
| `docker ps` | first: *permission denied* (user not in `docker` group). Owner ran `sudo usermod -aG docker administrator`. Then: one existing container `telegram-product-requests-postgres-1` on `127.0.0.1:5432` (not touched) |
| `ss -tlnp` | taken on 127.0.0.1: 5432 (other project's Postgres), 8080 (uvicorn), 20241 (cloudflared), 35695 |
| `python3 -m venv` | first failed: no ensurepip. Owner ran `sudo apt install -y python3.14-venv` |

**Port 5432 is taken, so our Postgres is on `127.0.0.1:5433`.** The API uses `127.0.0.1:8000`.

| Done when | Result | Command |
|---|---|---|
| Postgres starts, healthy | PASS | `docker compose up -d db` + `docker compose ps` → `aircon-db … (healthy) 127.0.0.1:5433->5432/tcp` |
| Upgrade on empty `aircon` | PASS | `alembic upgrade head` |
| Downgrade then upgrade | PASS | `alembic downgrade base && alembic upgrade head` |
| Tables + `invoice_no_seq` exist | PASS | `pytest` → `test_all_tables_and_invoice_sequence_exist` |
| `line_total != quantity * unit_price` rejected | PASS | `test_line_total_must_equal_quantity_times_unit_price` |
| Void without `void_reason` rejected | PASS | `test_void_sale_without_reason_is_rejected` (also checks that void *with* a reason is accepted) |
| Duplicate `serial_no` rejected | PASS | `test_duplicate_serial_is_rejected` |
| Delete product used by sale item rejected | PASS | `test_deleting_product_used_by_sale_item_is_rejected` |
| `/health` from the `api` container | PASS | `curl -s 127.0.0.1:8000/health` → `{"status":"ok"}` |
| Ports on 127.0.0.1 only | PASS | `ss -tlnp` → `127.0.0.1:5433`, `127.0.0.1:8000` |
| No `.env` / `.venv` in git | PASS | `git status` (both show as ignored) |

pytest output:
```
.....                                                                    [100%]
5 passed in 0.74s
```

Extra check: `alembic check` → "No new upgrade operations detected." The models and the hand-written
migration agree on tables, columns, indexes, unique constraints and FKs. (It does not compare CHECKs. Those are
copied by hand and the tests cover the key ones.)

## 4. What changed
- `api/app/main.py` — FastAPI app with `GET /health` only.
- `api/app/config.py` — settings from env / `.env` (pydantic-settings).
- `api/app/db.py` — engine + session factory.
- `api/app/models.py` — SQLAlchemy 2 models for all 7 tables + `invoice_no_seq`, with every CHECK, UNIQUE, FK (RESTRICT), default and index from `schema.md`.
- `api/alembic.ini`, `api/alembic/env.py`, `api/alembic/script.py.mako` — Alembic setup. The URL comes from `DATABASE_URL` unless the caller sets it (tests do).
- `api/alembic/versions/0001_initial.py` — one hand-written initial migration (tables, CHECKs, sequence, indexes; downgrade drops everything).
- `api/docker-compose.yml` — project `aircon`, containers `aircon-db` (postgres:16, volume `aircon-pgdata`, `127.0.0.1:5433`) and `aircon-api` (`127.0.0.1:8000`).
- `api/docker/init-test-db.sql` — creates `aircon_test` on first start (`aircon` is created by `POSTGRES_DB`).
- `api/Dockerfile`, `api/.dockerignore` — API image (python:3.14-slim, same Python as the VPS venv).
- `api/.env.example` — all required variables. A real `api/.env` (gitignored, mode 600) has a random DB password and JWT secret.
- `api/requirements.txt` — pinned versions.
- `api/tests/conftest.py` — migrates `aircon_test` (downgrade base → upgrade head) once per session. Refuses any DB not named `*_test`. Each test runs in a rolled-back transaction.
- `api/tests/test_schema.py` — the schema checks above.

## 5. Decisions I made
- **Postgres port 5433** (5432 is used by another project on this VPS).
- **Python 3.14** in the Docker image to match the VPS (only 3.14 is installed; the spec says 3.12+).
- Constraint/index names follow a naming convention (`ck_sales_void_fields`, `ix_sales_user_id_sold_at`, …), so future migrations can refer to them by name.
- The API container gets `DATABASE_URL` pointing at `db:5432` (compose network). The host `.env` points at `127.0.0.1:5433`.
- `bcrypt` is pinned now because 0.5's seed needs it for password hashes.
- Commands with docker are run as `sg docker -c "…"` in this session, because the group change needs a new login.

## 6. Questions for the owner
- None.

## 7. Not checked / risks
- Being in the `docker` group is effectively root access on the VPS. That is normal for Docker, but worth knowing.
- `restart: unless-stopped` on both containers: they come back after a VPS reboot. Phase 3 will revisit production setup.
- The API container does not run migrations on start. For now `alembic upgrade head` is run from the host venv.

## 8. Commit
See `git log` (`task 0.4: database + API skeleton`).
