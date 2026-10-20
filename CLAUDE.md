# Aircon Sales Dashboard

An Android app that shows sales data for an aircon and accessories business. The app reads data from an API server that will run on a VPS.

## Project layout

```
/android   Android app (Kotlin + Jetpack Compose)
/api       API server (Python FastAPI + PostgreSQL)
/docs      Contract, schema, goals
  openapi.yaml      API contract: the single source of truth
  schema.md         Database design notes
  PLAN.md           Roadmap (planner)
  DECISIONS.md      Owner's business decisions (planner)
  NEXT.md           Tasks to do now (planner)
  status/           Current state per machine: vps.md, windows.md (Claude Code)
  reports/          One report per task (Claude Code)
  goals/            Older goal files (history)
```

## Where each part runs (important)

One git repository, cloned on two machines and synced through a private GitHub repo.

| Part | Machine | Path |
|---|---|---|
| `/android` | **Windows PC** (Android Studio, Android SDK) | `D:\claude\p1` |
| `/api` + PostgreSQL | **VPS** (Ubuntu, same VM for API and database) | repo clone on the VPS |
| `/docs` | Both (shared contract) | — |

- On the Windows PC: only work in `/android` (and `/docs` when asked). Never try to run the API or database here.
- On the VPS: only work in `/api` (and `/docs` when asked). Never try to build the Android app here.
- If you are on the wrong machine for a task, stop and say so instead of working around it.
- Before starting a goal: `git pull`. After finishing a goal: commit and `git push`, so the other machine sees it.

### Database safety
- The VPS database will later hold real sales data.
- Every destructive script (reset, seed, drop) must refuse to run when `APP_ENV=production`.
- Tests use a separate test database (`aircon_test`), never the main one.

## How we work: planner + task loop

The planner (Claude chat) writes the plan into the repo; Claude Code does the work.

| File | Written by | Purpose |
|---|---|---|
| `docs/PLAN.md` | planner | roadmap of phases and tasks |
| `docs/DECISIONS.md` | planner | owner's business decisions (win over older docs) |
| `docs/NEXT.md` | planner | the tasks to do now, one section per machine, with **Done when** checks |
| `docs/status/vps.md`, `docs/status/windows.md` | Claude Code | where each machine stands after each run |
| `docs/reports/` | Claude Code | one report per task |

The owner starts a run with **`/next`** (`.claude/commands/next.md`). Claude Code never edits
`PLAN.md`, `DECISIONS.md` or `NEXT.md`. `docs/goals/` is the older goal format, kept for history.

## How we work: goal loops

Every task comes from `docs/NEXT.md` (older ones from `/docs/goals/`). Each task has a **Done when** section.

1. Read the goal and the "Done when" checks.
2. Write code.
3. Run the checks.
4. If a check fails, fix the code and run again.
5. Stop only when every check passes. Then report what you did and the final test output.

### Hard rules

- **Never edit, weaken, skip or delete a test to make it pass.** If a test looks wrong, stop and explain why.
- **Never change `docs/openapi.yaml` without asking.** Both the app and the API are tested against it.
- Don't mark a goal done if any check fails or was not run.
- Keep changes inside the goal's scope. Note other ideas at the end of your report instead of doing them.
- Commit after each completed goal with a message like `goal 1.3: today dashboard endpoint`.
- The ponytail plugin is installed: write the minimum code a goal needs. But every check in a goal's
  **Done when** is required, even if ponytail would skip it. Goal files win over ponytail's defaults.

### Reports

After every goal, write `docs/reports/report-<goal>.md` (e.g. `report-0.2.md`) with exactly these sections:

1. **Goal:** number and title
2. **Status:** DONE, BLOCKED, or NEEDS REVIEW
3. **Checks:** table of each "Done when" check, PASS/FAIL, and the command used
4. **What changed:** files added/changed/deleted, one line each on why
5. **Decisions I made:** anything not specified in the goal that I decided myself
6. **Questions for the owner:** anything needing a business decision
7. **Not checked / risks:** what I skipped or couldn't verify
8. **Commit:** hash and message

Commit the report together with the goal's work.

## Commands

### Android (Windows PC, from D:\claude\p1)
```
cd android
.\gradlew assembleDebug        # build
.\gradlew test                 # unit + Robolectric UI tests
.\gradlew lint                 # lint
.\gradlew verifyRoborazziDebug # screenshot tests (once set up)
```

### API (VPS)
```
cd api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest                          # all tests
uvicorn app.main:app --reload   # run locally on :8000
```

## Tech choices

**Android:** Kotlin, Jetpack Compose, Material 3, Retrofit + Kotlin Serialization, Hilt, DataStore (token storage), Vico (charts).
Tests: JUnit, Robolectric, MockWebServer (fake API), Roborazzi (screenshots).
Min SDK 26.

**API:** Python 3.12, FastAPI, SQLAlchemy 2, Alembic (migrations), PostgreSQL, JWT auth.
Tests: pytest, httpx test client, Schemathesis (contract tests).
Run with Docker Compose (API + Postgres).

## Business rules

- Product categories: `aircon`, `accessory`, `service` (installation / repair).
- One store only (no branches).
- Currency is Myanmar kyat (MMK) only. Money is stored as integers in kyat (the smallest unit is 1 kyat). Never use floats for money.
- Business timezone is `Asia/Yangon`. "Today", "yesterday", "this week" are always calculated in this timezone, never server UTC.
- Users have roles: `owner` (all data), `sales` (own sales only). Roles arrive in Phase 5; design for them from the start.
- Sales are never deleted, only voided. Void sales are excluded from every total.

## Security

- No secrets in git. Use `.env` files (gitignored) and provide `.env.example`.
- Every endpoint except `/health` and `/auth/login` requires a valid token.
- The database is never exposed to the internet.
