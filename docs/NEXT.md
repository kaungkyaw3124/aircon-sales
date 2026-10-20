# Next tasks

Written by the planner on 2026-10-21. Run `/next` on **each** machine; each does only its own section.
Both machines can run at the same time. `docs/openapi.yaml` (approved, D19) is the contract for both sides.

---

# VPS section — Phase 1: Backend MVP

Status: READY

General rules for this section:
- All tests run against `aircon_test` only. Never reseed or migrate `aircon` from a test.
- Response bodies must match `docs/openapi.yaml` exactly (field names, types, order of `by_category`).
- "Now" must be injectable (a clock dependency), so tests can fix the time.

## Task 1.1 — Error handling

- **Stop for review:** no

- Every 4xx/5xx response uses the shared shape `{"error": {"code", "message"}}`:
  `422` → code `validation_error` (override FastAPI's default body), `404` → `not_found`,
  `405` → `method_not_allowed`, unhandled exception → `500` `internal_error` (no stack trace in the body; log it).
- Keep `GET /health` as is.

### Done when
- pytest: a bad body on any endpoint gives 422 in the shared shape; an unknown path gives 404 in the shared shape;
  a route that raises gives 500 in the shared shape with no traceback text.
- All tests pass. Report, commit, push.

## Task 1.2 — Login with JWT

- **Stop for review:** no

- `POST /auth/login` exactly as in the contract. Passwords checked with bcrypt (the seed uses bcrypt).
- Wrong username, wrong password, or inactive user → the **same** `401 invalid_credentials` (don't reveal which).
- JWT HS256, secret from `JWT_SECRET`, lifetime from `JWT_EXPIRE_MINUTES` (default 1440). Claims: `sub` (user id), `role`, `exp`.
- A `get_current_user` dependency: missing / bad / expired token, or a user deactivated after login → `401 unauthorized`.
- If `JWT_SECRET` is missing or shorter than 32 characters, the app refuses to start.

### Done when
- pytest covers: correct login (200, fields match contract, `expires_in` matches config); wrong password; unknown user;
  inactive user (all three give the identical 401 body); missing fields (422); expired token (401); token signed with
  another secret (401); user deactivated after token was issued (401); short `JWT_SECRET` refuses to start.
- All tests pass. Report, commit, push.

## Task 1.3 — `GET /dashboard/today`

- **Stop for review:** no

Exactly as in the contract and D17, D18, D23:
- Yangon business day → UTC range, as in `schema.md`. Completed sales only for totals.
- `by_category` always 3 items in order aircon, accessory, service. `by_payment_method` leaves out empty methods.
- `unpaid_count`/`unpaid_amount` = completed sales with status `unpaid` or `partial` (full amounts, D17).
- `void_count` by `voided_at` on today's Yangon day (D18).
- `change_percent` = `(today - yesterday) / yesterday * 100` rounded to 1 decimal (half away from zero); `null` if yesterday is 0.
- Role `sales`: every number filtered to `sales.user_id = current user` (D23). Role `owner`: everything.
- One or a few SQL queries with aggregates, not a Python loop over all rows.

### Done when
- pytest builds small, hand-made datasets (not the seed) and checks exact numbers for:
  a normal day; an empty day (all zeros, `change_percent` null, `by_payment_method` empty);
  a void sale excluded from totals but counted in `void_count`; a sale sold yesterday and voided today
  (counts in today's `void_count`, not in yesterday's total); a `partial` sale appearing under its method **and** in unpaid;
  a `sales` user seeing only their own sales; yesterday = 0 → `change_percent` null; a negative change (e.g. -12.5).
- One test rebuilds the contract's `normal_day` example (the 5 invoices described in `openapi.yaml`) and checks
  the response equals the example (except `generated_at`, `date`).
- All tests pass. Report, commit, push.

## Task 1.4 — Yangon day boundaries

- **Stop for review:** no

- With the clock fixed, test the edges: a sale at 23:59:59 Yangon counts today; at 00:00:00 the next day it doesn't;
  a sale at 00:00:00 Yangon counts; a sale at 23:59 UTC that is already "tomorrow" in Yangon is not counted as today.
- Test that the result does not depend on the server timezone (run the same test with `TZ=UTC` and `TZ=America/New_York`).

### Done when
- Those boundary tests pass. All tests pass. Report, commit, push.

## Task 1.5 — Contract tests

- **Stop for review:** **yes** (end of Phase 1)

- Schemathesis against the app (in-process ASGI is fine), loading `docs/openapi.yaml`, with a valid token for
  authenticated endpoints. Checks: status codes documented, responses match schemas, no 500s.
- Run the live container too: rebuild `aircon-api`, then with the seeded `aircon` DB:
  `curl` login as `owner` / `owner123`, then `GET /dashboard/today` with the token.

### Done when
- Schemathesis run passes with no failures.
- The live `curl` sequence returns 200 and a body that matches the contract. Paste both responses (token shortened) in the report.
- All tests pass. Report, commit, push.
- **Stop for review.**

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
