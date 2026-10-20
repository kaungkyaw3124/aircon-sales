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

# Windows PC section — Phase 2: Android MVP

Status: READY

General rules for this section:
- Work only in `/android` (and its own report/status files). Never touch `/api`.
- The real API is not reachable from the PC yet (Phase 3). All tests use **MockWebServer** with JSON taken from the
  contract examples. No test may need the network.
- Kotlin + Jetpack Compose + Material 3, Hilt, Retrofit + Kotlin Serialization, DataStore. Versions through the
  Gradle version catalog (`gradle/libs.versions.toml`). Keep `minSdk 26`.
- Money is `Long` (kyat). Show it with thousands separators and "Ks", e.g. `3,660,000 Ks`. Never `Double` for money.
- API base URL comes from `BuildConfig.API_BASE_URL` (debug default `http://10.0.2.2:8000/`, which is the PC from the emulator).

## Task 2.1 — App foundation

- **Stop for review:** no

- Add dependencies: Hilt, Retrofit, Kotlin Serialization (+ Retrofit converter), OkHttp + MockWebServer (test),
  DataStore, Navigation Compose, Robolectric, Roborazzi, kotlinx-coroutines-test, Turbine.
- Package structure: `data/` (api, models, repository), `ui/` (login, dashboard, theme), `di/`.
- `BuildConfig.API_BASE_URL` as above. `android:usesCleartextTraffic` allowed **only in debug** (network security config).
- App label: "Aircon Sales".

### Done when
- `.\gradlew assembleDebug` → BUILD SUCCESSFUL.
- `.\gradlew test` → passes (at least one trivial Robolectric test proving the setup works).
- Report, commit, push.

## Task 2.2 — API client matching the contract

- **Stop for review:** no

- Kotlin `@Serializable` models for `LoginRequest`, `LoginResponse`, `User`, `DashboardToday`, `CategoryTotal`,
  `PaymentMethodTotal`, `Error`, using `@SerialName` for snake_case. `change_percent` is `Double?`.
- Retrofit interface: `login`, `dashboardToday` (bearer token via an OkHttp interceptor).
- Error mapping: any non-2xx body is parsed as the shared error shape into a typed result
  (`ApiResult.Success / ApiError(code, message, httpStatus) / NetworkError`).
- **Contract fixtures:** copy every response example from `docs/openapi.yaml` into
  `android/app/src/test/resources/contract/<name>.json`. Add a test that reads `docs/openapi.yaml` (via a test-only
  YAML library, path `../docs/openapi.yaml` from the project) and fails if any fixture differs from its example.
  This keeps the app tied to the contract.

### Done when
- Unit tests parse every fixture into its model without error, and the `normal_day` fixture gives `total_amount == 3660000L`.
- The fixture-vs-contract test passes.
- MockWebServer tests: login 200, login 401 → `ApiError("invalid_credentials")`, dashboard sends `Authorization: Bearer <token>`,
  server down → `NetworkError`.
- `.\gradlew test` passes. Report, commit, push.

## Task 2.3 — Login screen + saved token

- **Stop for review:** no

- Login screen: username, password (hidden), Login button, loading state, error text from the API message.
- On success, save token + user (DataStore) and go to the dashboard. On app start, a saved token goes straight to the dashboard.
- Logout action on the dashboard clears the token and returns to login.
- A 401 from any authenticated call clears the token and returns to login.

### Done when
- Robolectric UI tests: successful login navigates to dashboard; wrong password shows the API message; button disabled
  while loading and when fields are empty; saved token skips login; 401 on dashboard returns to login.
- `.\gradlew test` passes. Report, commit, push.

## Task 2.4 — Today dashboard screen

- **Stop for review:** no

Shows `/dashboard/today` (D17, D18):
- Big total (`3,660,000 Ks`), invoice count, date.
- Change vs yesterday: ▲ green / ▼ red with percent; "No sales yesterday" when `change_percent` is null.
- Three category cards (Aircon / Accessories / Service) with amount and quantity.
- Payment methods list. "Not fully paid": count and amount. "Voided today": count (only if > 0).
- Pull to refresh.

### Done when
- ViewModel tests with the `normal_day` and `empty_day` fixtures check the displayed values
  (formatted strings, arrow direction, null change text).
- Roborazzi screenshot tests for: normal day, empty day, negative change. Recorded images committed.
- `.\gradlew test` and `.\gradlew verifyRoborazziDebug` pass. Report, commit, push.

## Task 2.5 — Loading, error and offline states

- **Stop for review:** **yes** (end of Phase 2 build; owner looks at screenshots)

- Loading indicator on first load. Error state with message and Retry.
- Offline: keep showing the last loaded dashboard with "Last updated 10:42" and a banner "Offline — showing saved data".
  (Cache the last `DashboardToday` JSON in DataStore.)
- Timeout 15 s.

### Done when
- Tests: server error shows message + Retry, Retry reloads; network down with cached data shows the banner and the
  saved numbers; network down with no cache shows the error state.
- Roborazzi screenshots for: loading, error, offline banner. Committed.
- `.\gradlew assembleDebug`, `.\gradlew test`, `.\gradlew verifyRoborazziDebug`, `.\gradlew lint` pass (no lint errors).
- Report lists the screenshot file paths so the owner can open them.
- **Stop for review.**
