# Report 2.9

## 1. Goal
Task 2.9: Handle "too many login attempts" (contract v0.1.1)

## 2. Status
DONE

## 3. Checks
| Check | Result | Command |
|---|---|---|
| Contract has `info.version: 0.1.1` and `rate_limited` on `POST /auth/login` | PASS (pushed by VPS task 3.3) | `git pull --rebase`, read `docs/openapi.yaml` |
| `ContractFixturesTest` passes with the new example | PASS | `.\gradlew test` |
| 429 from MockWebServer shows the message and the countdown; button enabled again at 0 (test clock, no sleep) | PASS: `LoginFlowTest.rateLimitedShowsMessageAndCountdownThenReenables` | `.\gradlew test` |
| Roborazzi screenshot of the rate-limited login screen, committed | PASS: `android/app/src/test/screenshots/login_rate_limited.png` | `.\gradlew recordRoborazziDebug` |
| `.\gradlew test` | PASS (32 tests, 0 failures; 3 full runs in a row) | `.\gradlew test --rerun-tasks` |
| `.\gradlew verifyRoborazziDebug` | PASS (7 screenshots) | `.\gradlew verifyRoborazziDebug` |
| `.\gradlew lint` | PASS: 0 errors, 21 warnings | `.\gradlew lint` |

## 4. What changed
- `data/api/ApiResult.kt`: `ApiError` gets `retryAfterSeconds` (default `null`), read from the `Retry-After` header.
- `ui/login/LoginViewModel.kt`: on an error with `Retry-After`, `retryIn` counts down once per second; `canSubmit` is false while it is above 0.
- `ui/login/LoginScreen.kt`: `LoginContent` takes `retryIn` and shows "Try again in m:ss" under the API message.
- `test/resources/contract/rate_limited.json` (new): fixture identical to the contract example.
- `test/.../data/ApiClientTest.kt`: new test, 429 maps to `ApiError(..., 429, 900)`.
- `test/.../ui/LoginFlowTest.kt`: new test, 429 with `Retry-After: 900` â†’ message, `15:00`, `14:52` after 8 s, `0:01`, then button enabled.
- `test/.../ui/login/LoginScreenshotTest.kt` (new) + `test/screenshots/login_rate_limited.png`: the rate-limited screen at 14:52.

## 5. Decisions I made
- Test clock = Robolectric's paused main looper (`shadowOf(mainLooper).idleFor(...)`): the ViewModel's `delay(1000)` runs on the main dispatcher, so 900 s pass instantly.
- Countdown format `m:ss` ("14:52", "0:01"); shown as normal text under the red API message. The message itself is the API's, unchanged.
- If a 429 arrives **without** `Retry-After`, the app shows the message but does not lock the button (the server still refuses).
- The countdown lives in the ViewModel: it survives rotation, but restarting the app clears it (the server still enforces the limit).

## 6. Questions for the owner
- None.

## 7. Not checked / risks
- Not tried against the real VPS API (tests use MockWebServer only).
- `SetupTest.appStartsWithLabel` failed once in one full run, then passed in 3 more full runs and 3 solo runs. It asserts the login screen right after launch, without waiting for DataStore to load the saved token, so it can race. Pre-existing, not touched (hard rule). Suggest the planner allows changing it to `waitForText("Aircon Sales")`.
- No Android Studio preview added for the rate-limited state (not asked).

## 8. Commit
8510d86 `task 2.9: handle too many login attempts`
