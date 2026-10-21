# Next tasks

Written by the planner on 2026-10-21. Run `/next` on **each** machine; each does only its own section.
Run the **VPS first** this time: the Windows task 2.9 needs the contract change that VPS task 3.3 pushes.

---

# VPS section — Phase 3 (part 2): ready for the internet

Status: READY

General rules: as before (D21: never touch other projects' containers or ports; no `sudo`; tests on `aircon_test` only).

## Task 3.3 — Login rate limiting (contract v0.1.1)

- **Stop for review:** no

This task **may change `docs/openapi.yaml`** (owner approved, D25), only as described here:
- Add a `429` response to `POST /auth/login` using the shared error shape, with one example named `rate_limited`:
  `{"error": {"code": "rate_limited", "message": "Too many login attempts. Try again in 15 minutes."}}`,
  and a `Retry-After` header (seconds). Bump `info.version` to `0.1.1`. Nothing else in the contract changes.
- Rule (D30): **5 failed logins per username in 15 minutes**, or **20 failed logins per client IP in 15 minutes** → 429
  until the window passes. A successful login resets that username's counter. Counters in **Postgres** (2 workers),
  new table via a new Alembic migration; old rows cleaned up automatically. Client IP from the proxy header only when the request
  comes from a trusted proxy address (configurable; default: no proxy trusted).
- Update `schema.md` with the new table.

### Done when
- `npx @redocly/cli lint docs/openapi.yaml` passes; the only diff in the contract is the 429 response, header, example and version.
- pytest: 5 wrong passwords → 6th attempt 429 (even with the right password) with `Retry-After`; another username still works;
  after the window (clock moved) login works again; a success resets the counter; the IP limit triggers across different usernames;
  counters are shared (two app instances in one test see the same count).
- Schemathesis still passes with the new contract.
- All tests pass. Report, commit, push.

## Task 3.4 — Production hardening

- **Stop for review:** no

- When `APP_ENV=production`: `/docs`, `/redoc`, `/openapi.json` are **off** (404). Dev keeps them.
- Docker log rotation in compose for both services: `max-size: 10m`, `max-file: 5`.
- `api/scripts/create_user.py`: create or update a user (`--username`, `--full-name`, `--role owner|sales`), password typed twice
  at a hidden prompt (never on the command line), minimum 10 characters; `--deactivate` to disable a user. Works in production
  (it's not destructive). Document in `api/README.md`.
- Backups (D31): also keep **one dump per month for 12 months** (the first dump of each month), in addition to the 14 daily.
  After each backup, write `~/aircon-backups/LAST_OK` with the timestamp; on failure write `~/aircon-backups/LAST_FAILED`.

### Done when
- pytest: with `APP_ENV=production`, `/docs`, `/redoc`, `/openapi.json` return 404 in the shared error shape; dev returns 200.
- pytest: `create_user.py` creates a user who can log in; refuses a short password; `--deactivate` makes login fail with 401;
  the password never appears in the process arguments.
- `docker inspect aircon-api` shows the log options; containers healthy after `docker compose up -d`.
- Backup retention test with fake files: 14 newest daily + first-of-month for the last 12 months kept, the rest deleted.
- All tests pass. Report, commit, push.

## Task 3.5 — Go-live checklist

- **Stop for review:** **yes**

Write `docs/GO-LIVE.md`: the exact, numbered steps the owner (with Claude Code) will follow on the day real data starts:
new secrets, `APP_ENV=production`, empty database (no seed), create real users, backup check, restore drill, how to roll back.
Include a "Before exposing to the internet" section listing what 3.6 (HTTPS) still needs from the owner.
Do **not** switch anything to production in this task.

### Done when
- `docs/GO-LIVE.md` exists; every command in it was dry-run where it's safe (say which ones in the report).
- All tests pass. Report, commit, push.
- **Stop for review.**

---

# Windows PC section — contract v0.1.1 + look

Status: READY

General rules: only `/android`; never touch `/api`; **do not change `docs/openapi.yaml`**; tests never use the network.

## Task 2.9 — Handle "too many login attempts" (contract v0.1.1)

- **Stop for review:** no

- **First:** `git pull` and check `docs/openapi.yaml` has `info.version: 0.1.1` and a `rate_limited` example on `POST /auth/login`.
  If not, stop and mark this task BLOCKED with "run `/next` on the VPS first (task 3.3)". Do not edit the contract yourself.
- Add the fixture `contract/rate_limited.json` (so `ContractFixturesTest` passes).
- Login screen on 429: show the API's message, and disable the Log in button for the `Retry-After` seconds, with a countdown
  ("Try again in 14:52").

### Done when
- `ContractFixturesTest` passes with the new example.
- Tests: a 429 from MockWebServer shows the message and the countdown; the button is enabled again when it reaches 0
  (use a test clock, don't sleep).
- Roborazzi screenshot of the rate-limited login screen, committed.
- `.\gradlew test`, `.\gradlew verifyRoborazziDebug`, `.\gradlew lint` pass. Report, commit, push.

## Task 2.10 — Neutral backgrounds + release build hardening

- **Stop for review:** **yes**

- **D32:** backgrounds and cards are neutral: light theme background `#FFFFFF`, cards `#F2F4F7` (no purple/pink tint);
  dark theme background `#121212`, cards `#1E1E1E`. Keep the brand blue for buttons and the title accent.
- Release build: turn on R8 (`isMinifyEnabled = true`, `isShrinkResources = true`) with the keep rules Retrofit,
  Kotlin Serialization and Hilt need. Release must still use HTTPS only (no cleartext).
- Re-record all screenshots.

### Done when
- `.\gradlew assembleRelease` succeeds (unsigned is fine) and `.\gradlew assembleDebug` too.
- A unit test (or JSON round-trip test run against the release variant, if AGP allows) proves serialization models survive R8;
  otherwise explain in the report what was checked instead.
- `.\gradlew recordRoborazziDebug`, then `verifyRoborazziDebug`, `test`, `lint` pass. New images committed.
- Report lists the screenshot paths. **Stop for review.**
