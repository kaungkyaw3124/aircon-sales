# Report 2.2

## 1. Goal
Task 2.2: API client matching the contract

## 2. Status
DONE

## 3. Checks
| Check | Result | Command |
|---|---|---|
| Every fixture parses into its model; `normal_day` gives `total_amount == 3660000L` | PASS (`ModelParsingTest`, 2 tests) | `.\gradlew test` |
| Fixture-vs-contract test | PASS (`ContractFixturesTest`); also confirmed it FAILS when `normal_day.json` is changed by 1 kyat | `.\gradlew test`, `.\gradlew testDebugUnitTest --tests *ContractFixturesTest` |
| MockWebServer: login 200, login 401 → `ApiError("invalid_credentials")`, dashboard sends `Authorization: Bearer <token>`, server down → `NetworkError` | PASS (`ApiClientTest`, 6 tests incl. 401-with-token callback and non-JSON 502) | `.\gradlew test` |
| `.\gradlew test` passes | PASS (10 tests, 0 failures) | `.\gradlew test` |

## 4. What changed
- `data/models/Models.kt`: `@Serializable` `LoginRequest`, `LoginResponse`, `User`, `DashboardToday`, `CategoryTotal`, `PaymentMethodTotal`, `Error`; money as `Long`, `change_percent` as `Double?`.
- `data/api/AirconApi.kt`: Retrofit `login`, `dashboardToday`.
- `data/api/ApiClient.kt`: shared `ApiJson`, `AuthInterceptor` (bearer header + 401 callback), `createApi(...)` used by the app and the tests.
- `data/api/ApiResult.kt`: `ApiResult.Success / ApiError(code, message, httpStatus) / NetworkError` and `apiCall {}` mapping.
- `test/resources/contract/*.json`: the 7 response examples from `openapi.yaml` (`ok`, `owner`, `invalid_credentials`, `normal_day`, `empty_day`, `unauthorized`, `missing_field`).
- `test/.../data/ContractFixturesTest.kt`, `ModelParsingTest.kt`, `ApiClientTest.kt`.

## 5. Decisions I made
- Fixture file name = example name in `openapi.yaml`. Only response examples (anything under a `responses` key) are fixtures; the request example (`LoginRequest` `owner`) is not.
- The contract test gets the path from Gradle (`openapi.path` = `android/../docs/openapi.yaml`) and the file is a declared test input, so editing the contract re-runs the test.
- `category`, `role`, `payment_method` are `String`, not Kotlin enums, so a new value from the API doesn't crash the app.
- `ApiJson` ignores unknown fields (forward compatible). The contract test still compares fixtures to the YAML exactly.
- A non-JSON error body (e.g. proxy error page) becomes `ApiError("http_<status>", "Server error (<status>).", status)`; a malformed 2xx body becomes `ApiError("bad_response", …)`.
- `ok` (health) has no app model; the parse test uses a test-only `Health` class.
- `AuthInterceptor` has an `onUnauthorized` hook, wired to "clear token" in task 2.3.

## 6. Questions for the owner
None.

## 7. Not checked / risks
- Not tested against the real API (not reachable until Phase 3), by design.

## 8. Commit
See `git log` (message `task 2.2: API client matching the contract`).
