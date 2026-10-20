# Phase 0 — Foundations

Order: **structure → database design → API contract → database on VPS → fake data.**
Finish one goal completely (all checks pass) before starting the next.
Stop after each goal and report, so the owner can review.

---

## Goal 0.1 — Project structure + GitHub (Windows PC, `D:\claude\p1`)

Create the monorepo around the existing `/android` project and push it to GitHub.

### Do
- Create `/api` (with a `.gitkeep`) and `/docs/goals` folders.
- Add a root `.gitignore` covering: Android build output (`build/`, `.gradle/`, `local.properties`, `*.apk`, `.idea/`), Python (`.venv/`, `__pycache__/`, `.pytest_cache/`), and `.env`.
- Add a short root `README.md` describing the project and the layout from `CLAUDE.md`.
- Commit and push to the private GitHub repo (the owner creates the empty repo and gives the URL).

### Done when
- `git status` shows no build output, `.venv` or `local.properties` files as untracked.
- `cd android; .\gradlew assembleDebug` still ends in `BUILD SUCCESSFUL`.
- `git push` succeeded and the repo on GitHub shows `CLAUDE.md`, `README.md`, `android/`, `api/`, `docs/`.

---

## Goal 0.2 — Database design (either machine; docs only)

Write `/docs/schema.md`. Design only, no code yet.

### Tables (minimum)
- `branches` — id, name, address, active
- `users` — id, username, password_hash, full_name, role (`owner` / `manager` / `sales`), branch_id (nullable for owner), active
- `products` — id, sku, name, category (`aircon` / `accessory` / `service`), brand, model, capacity_hp (nullable, aircon only), is_inverter (nullable), price, active
- `sales` — id, invoice_no, branch_id, user_id (salesperson), sold_at (timestamp with timezone), total_amount, payment_status (`paid` / `partial` / `unpaid`), note
- `sale_items` — id, sale_id, product_id, quantity, unit_price, line_total

### Must also cover
- Money as integers (smallest currency unit).
- Indexes needed for "sales by day", "sales by branch", "top products".
- `sold_at` stored in UTC; "today" calculated in `Asia/Yangon`.
- A short "future" section: stock levels and daily summary table (Phase 4–5), not built yet.

### Done when
- `/docs/schema.md` lists every table, column, type, key and index.
- Committed and pushed.
- **Owner reviews and approves.** Do not start 0.3 until approved.

---

## Goal 0.3 — API contract (either machine; docs only)

Write `/docs/openapi.yaml` (OpenAPI 3.1) for the Phase 1 endpoints only.

### Endpoints
- `GET /health` — no auth. Returns `{ "status": "ok" }`.
- `POST /auth/login` — body `{ username, password }`. Returns `{ access_token, token_type, expires_in, user: { id, full_name, role, branch_id } }`. 401 on wrong credentials.
- `GET /dashboard/today` — bearer auth. Returns:
  - `date` (YYYY-MM-DD, Asia/Yangon)
  - `total_amount`, `invoice_count`
  - `yesterday_total_amount`, `change_percent` (nullable if yesterday was 0)
  - `by_category`: list of `{ category, amount, quantity }` for aircon / accessory / service
  - `generated_at` (timestamp)

### Rules
- snake_case JSON field names everywhere.
- Every response includes an example.
- Shared error shape: `{ "error": { "code", "message" } }`.

### Done when
- `npx @redocly/cli lint docs/openapi.yaml` passes with no errors.
- Committed and pushed.
- **Owner reviews and approves.**

---

## Goal 0.4 — Database + API skeleton (VPS)

`git pull` first. Set up `/api` so the database from 0.2 is created on the VPS.

### Do
- FastAPI structure: `app/main.py`, `app/db.py`, `app/models.py`, `app/config.py`.
- SQLAlchemy models matching `schema.md`.
- Alembic with one initial migration.
- `docker-compose.yml` in `/api` with `db` (PostgreSQL 16) and `api` services. Postgres port bound to `127.0.0.1` only, never public.
- Two databases: `aircon` (main) and `aircon_test` (tests only).
- `.env.example` with `APP_ENV`, `DATABASE_URL`, `TEST_DATABASE_URL`, `JWT_SECRET`, `JWT_EXPIRE_MINUTES`, `BUSINESS_TZ=Asia/Yangon`.
- `requirements.txt`.

### Done when
- `docker compose up -d db` starts Postgres.
- `alembic upgrade head` runs on an empty database with no errors.
- `alembic downgrade base` then `alembic upgrade head` also works.
- A pytest test (against `aircon_test`) confirms every table in `schema.md` exists.
- `pytest` passes.
- From outside the VPS, port 5432 is **not** reachable (owner checks, or `ss -tlnp | grep 5432` shows `127.0.0.1` only).
- Committed and pushed.

---

## Goal 0.5 — Fake data generator (VPS)

Write `api/scripts/seed.py` to fill the database with realistic test data.

### Data
- 3 branches, 1 owner, 3 managers (one per branch), 6 salespeople.
- About 40 products: aircons (several brands, 1 / 1.5 / 2 / 2.5 HP, inverter and non-inverter), accessories (brackets, copper pipe, remote, stabilizer, drain pipe), services (installation, cleaning, repair).
- 90 days of sales ending today (Asia/Yangon).
- Hotter months (March–May) have more aircon sales. Accessories often appear with aircon sales. Most invoices paid; some partial / unpaid.
- Fixed random seed so data is the same every run.
- Dev login: `owner` / `owner123` (documented in README as dev only).

### Done when
- `python scripts/seed.py --reset` runs without errors and prints row counts per table.
- Running it twice gives identical totals.
- With `APP_ENV=production`, `seed.py --reset` refuses and exits with an error (tested).
- A pytest test checks every sale's `total_amount` equals the sum of its `sale_items.line_total`.
- `pytest` passes.
- Committed and pushed.

---

## End of Phase 0

Report: what was built, final output of `pytest` (VPS) and `.\gradlew assembleDebug` (Windows), and anything that needs the owner's decision before Phase 1.

## After Phase 0

- **Phase 1 (VPS):** API endpoints: login, today dashboard, contract tests.
- **Phase 2 (Windows):** Android app. Can start as soon as `openapi.yaml` is approved, using a fake server (MockWebServer), so it doesn't have to wait for Phase 1 to finish.
