# Next tasks

Written by the planner on 2026-10-21. Run `/next` on **each** machine; each does only its own section.
Both machines can run at the same time. `docs/openapi.yaml` (approved, D19) is the contract for both sides.

---

# VPS section — Phase 3 (part 1): make the server dependable

Status: READY

Phase 1 is done and approved (D24). These tasks don't depend on how the API will be exposed to phones;
that needs owner answers first (see `docs/PLAN.md`, Phase 3).

General rules for this section:
- Never touch the other projects on this server (D21): container `telegram-product-requests-postgres-1`, ports 5432, 8080,
  `cloudflared`. Only `aircon-*` containers and our own files.
- No `sudo`. If something truly needs it, stop and mark BLOCKED with the exact commands.
- **Do not change `docs/openapi.yaml`** in this section (the Windows PC is testing against it right now).

## Task 3.1 — Production-ready container

- **Stop for review:** no

- Split dependencies: `requirements.txt` (runtime only) and `requirements-dev.txt` (`-r requirements.txt` + pytest,
  httpx, schemathesis, ...). The Docker image installs runtime only. The venv installs dev.
- On container start, run `alembic upgrade head`, then start uvicorn (an entrypoint script). If the migration fails,
  the container exits non-zero (no API running on an old schema).
- Docker healthcheck on the `api` service calling `/health`.
- uvicorn without `--reload`, with `--proxy-headers` and 2 workers.
- Log to stdout in one line per request (method, path, status, duration ms). Never log passwords or tokens.

### Done when
- `docker compose build api` image contains no pytest/schemathesis (`docker run --rm aircon-api pip list` check).
- `docker compose down` then `docker compose up -d`: both containers healthy, `/health` OK, data still there
  (row counts the same as before), login + `/dashboard/today` work via `curl`.
- Starting the API against an empty test database runs the migration automatically (prove it, then clean up).
- `docker compose logs api` shows request lines and contains no `password` or `Bearer` values.
- All tests pass. Report, commit, push.

## Task 3.2 — Daily database backup + restore test

- **Stop for review:** **yes**

- `api/scripts/backup.sh`: `pg_dump` of `aircon` (custom format, via `docker exec aircon-db`) into
  `~/aircon-backups/aircon-YYYY-MM-DD_HHMM.dump` (outside the repo, folder mode 700). Keeps the newest 14 dumps.
  Exits non-zero and prints the reason on any failure.
- `api/scripts/restore_check.sh <dump>`: restores into a scratch DB `aircon_restore_check`, compares row counts of every
  table with `aircon`, prints them, then drops the scratch DB. Never touches `aircon` or `aircon_test`.
- Schedule `backup.sh` daily at 02:30 Yangon with the **user's** crontab (`crontab -e` style, no sudo). Log to
  `~/aircon-backups/backup.log`.
- Document both scripts in `api/README.md`, including how to restore for real.

### Done when
- `backup.sh` run by hand creates a dump; running it 16 times (or faking old files) leaves only 14.
- `restore_check.sh` on that dump prints identical row counts for every table and exits 0; the scratch DB is gone afterwards.
- `crontab -l` shows the job. Report includes the line.
- All tests pass. Report, commit, push.
- **Stop for review.** In the report, list what is still missing before the API can be opened to the internet.

---

# Windows PC section — Phase 2 wrap-up

Status: READY

Phase 2 is approved: the owner ran the app on a Xiaomi phone over USB against the VPS (D27).

General rules for this section:
- Work only in `/android` (and its own report/status files). Never touch `/api`. **Do not change `docs/openapi.yaml`.**
- All tests use MockWebServer / fixtures, never the network.

## Task 2.6 — Verify the planner's debug-URL change + "run on phone" guide

- **Stop for review:** no

The planner changed the debug `API_BASE_URL` to `http://127.0.0.1:8000/` and updated `SetupTest` to match (D26, commit 0ae1e5d).
- Check that change builds and all tests still pass. If anything else referred to `10.0.2.2`, update it.
- Write `android/README.md` "Run on a phone or emulator" for the owner, in short numbered steps:
  1. SSH tunnel: `ssh -p 10066 -N -L 127.0.0.1:8000:127.0.0.1:8000 administrator@93.127.132.69` (leave open).
  2. adb from the owner's SDK at `D:\android studio\platform-tools\adb.exe`: `adb devices`, then `adb reverse tcp:8000 tcp:8000`
     (again after every reconnect / emulator restart).
  3. Xiaomi phones: Developer options → **Install via USB** must be on.
  4. Run ▶ in Android Studio, log in `owner` / `owner123` (dev only).
  5. Common errors and their fix: "Can't reach the server" (tunnel or adb reverse missing), `INSTALL_FAILED_USER_RESTRICTED`.
- Add `android/run-on-phone.ps1` that finds the SDK from `local.properties`, runs `adb devices` and `adb reverse tcp:8000 tcp:8000`,
  and prints a clear message if no device is connected. (The tunnel stays a manual step: it needs the owner's SSH login.)

### Done when
- `.\gradlew assembleDebug` and `.\gradlew test` pass.
- `grep -r "10.0.2.2" android --include=*.kt --include=*.kts --include=*.md` finds nothing outside build output.
- `run-on-phone.ps1` runs without a device and prints the "no device" message (exit code non-zero).
- Report, commit, push.

## Task 2.7 — Fixed brand colours and safer backup settings

- **Stop for review:** no

- **D28:** fixed brand colours, no dynamic (wallpaper) colours. Primary `#0057B8` (blue), secondary `#00A3E0` (sky blue),
  keep green ▲ / red ▼ for change. Light and dark themes both defined. Put the colours in one place so the owner can change them.
- **D29:** `android:allowBackup="false"`, and backup/data-extraction rules exclude everything, so the saved token is never
  copied into Android backups.
- Re-record the Roborazzi screenshots with the new colours.

### Done when
- `dynamicColor` is not used anywhere (`grep`), the theme uses the colours above.
- `allowBackup="false"` in the manifest; backup rules exclude all data.
- `.\gradlew recordRoborazziDebug` then `.\gradlew verifyRoborazziDebug` pass; new images committed.
- `.\gradlew test` and `.\gradlew lint` pass (no lint errors).
- Report, commit, push.

## Task 2.8 — Previews in Android Studio

- **Stop for review:** **yes**

The owner wants to look at screens inside Android Studio without running the app.
- Add Compose `@Preview` functions (light and dark) for: login (empty, loading, error), dashboard (normal day, empty day,
  negative change, loading, error, offline). Use the contract fixtures' data (as Kotlin values), no network, no Hilt.
- Previews live next to each screen (`*Previews.kt`) and are not in the release build's code paths.

### Done when
- `.\gradlew assembleDebug`, `.\gradlew test`, `.\gradlew verifyRoborazziDebug`, `.\gradlew lint` pass.
- Report lists each preview function and the file it's in, and tells the owner how to open them
  (open the file → **Split** or **Design** view, top-right of the editor).
- **Stop for review.**
