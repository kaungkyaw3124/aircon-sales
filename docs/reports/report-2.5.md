# Report 2.5

## 1. Goal
Task 2.5: Loading, error and offline states

## 2. Status
DONE. **Stop for review** (end of the Phase 2 build: owner looks at the screenshots).

## 3. Checks
| Check | Result | Command |
|---|---|---|
| Server error shows message + Retry; Retry reloads | PASS `DashboardStatesTest.serverErrorShowsMessageAndRetryReloads` | `.\gradlew test` |
| Network down with cached data shows the banner and the saved numbers | PASS `networkDownWithCacheShowsBannerAndSavedNumbers` ("Offline — showing saved data", "Last updated 15:42", "3,660,000 Ks") | `.\gradlew test` |
| Network down with no cache shows the error state | PASS `networkDownWithoutCacheShowsErrorState` | `.\gradlew test` |
| Extra: a successful load is saved for offline use | PASS `successfulLoadIsCachedForOffline` | `.\gradlew test` |
| Roborazzi screenshots: loading, error, offline banner; committed | PASS (recorded) | `.\gradlew recordRoborazziDebug` |
| `.\gradlew assembleDebug` | PASS (BUILD SUCCESSFUL) | `.\gradlew assembleDebug` |
| `.\gradlew test` | PASS (29 tests, 0 failures) | `.\gradlew test` |
| `.\gradlew verifyRoborazziDebug` | PASS (all 6 screenshots match) | `.\gradlew verifyRoborazziDebug` |
| `.\gradlew lint` (no lint errors) | PASS: 0 errors, 21 warnings (see section 7) | `.\gradlew lint` |

### Screenshots for the owner
All in `android/app/src/test/screenshots/`:
- `dashboard_normal_day.png`: normal day, ▲ 20.0%
- `dashboard_empty_day.png`: no sales, "No sales yesterday"
- `dashboard_negative_change.png`: ▼ 12.5% in red
- `dashboard_loading.png`: first load spinner
- `dashboard_error.png`: error message + Retry
- `dashboard_offline.png`: "Offline — showing saved data / Last updated 15:42" banner over the saved numbers

## 4. What changed
- `data/repository/SessionStore.kt`: `saveDashboard` / `cachedDashboard` (last `DashboardToday` as JSON in DataStore; cleared on logout).
- `data/repository/SalesRepository.kt`: saves every successful dashboard; exposes the cached one.
- `di/NetworkModule.kt`: OkHttp `callTimeout(15 s)`.
- `ui/dashboard/DashboardViewModel.kt`: network failure → saved dashboard with `offline = true`, or the error state if nothing is saved.
- `ui/dashboard/DashboardUi.kt`: `lastUpdated` ("Last updated 15:42") from `generated_at`.
- `ui/dashboard/DashboardScreen.kt`: error state with Retry button; offline banner.
- `test/.../ui/DashboardStatesTest.kt` (new), `DashboardScreenshotTest.kt` (+3 screenshots), `DashboardViewModelTest.kt` (+ last updated check).
- `test/screenshots/dashboard_loading.png`, `dashboard_error.png`, `dashboard_offline.png` (new).

## 5. Decisions I made
- "Last updated" time = the dashboard's `generated_at` (server time with the Yangon offset), shown as `HH:mm`. So it is Yangon time even if the phone is set to another timezone, and no extra timestamp is stored.
- Only a network failure (no connection, timeout) falls back to saved data. A server error (e.g. 500) shows the error message + Retry, as the task says, even if saved data exists.
- The 15 s timeout is a total-call timeout (connect + send + wait + read).
- The cache is wiped on logout and on a 401, so a different user never sees it.

## 6. Questions for the owner
- Please look at the 6 screenshots above and say if the layout, wording and colours are OK.
- (From 2.4) Fixed brand colours, or follow the phone's wallpaper colours on Android 12+ (current)?

## 7. Not checked / risks
- Lint warnings (not errors): 8 `GradleDependency` + 3 `NewerVersionAvailable` (template libraries such as core-ktx 1.10.1, activity-compose 1.8.0 are old; not upgraded to stay in scope), 7 `UnusedResources` (template colours), 1 `InsecureBaseConfiguration` (debug-only cleartext, intended), 1 `ObsoleteSdkInt`, 1 `RedundantLabel` (template).
- The 15 s timeout itself is not tested (it would make the test suite 15 s slower); it is one line of OkHttp config.
- If the server sends a bad response that isn't a network failure, there is no offline fallback (error state instead).
- Not run on a real device yet (task 2.6).

## 8. Commit
See `git log` (message `task 2.5: loading, error and offline states`).
