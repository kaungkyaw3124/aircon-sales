# Report 2.3

## 1. Goal
Task 2.3: Login screen + saved token

## 2. Status
DONE

## 3. Checks
| Check | Result | Command |
|---|---|---|
| Successful login navigates to dashboard (and the dashboard call carries the saved token) | PASS `LoginFlowTest.successfulLoginShowsDashboard` | `.\gradlew test` |
| Wrong password shows the API message | PASS `wrongPasswordShowsApiMessage` | `.\gradlew test` |
| Button disabled while loading and when fields are empty | PASS `buttonDisabledWhenFieldsEmptyAndWhileLoading` | `.\gradlew test` |
| Saved token skips login | PASS `savedTokenSkipsLogin` | `.\gradlew test` |
| 401 on dashboard returns to login (token cleared) | PASS `unauthorizedOnDashboardReturnsToLogin` | `.\gradlew test` |
| Extra: Logout clears token and returns to login | PASS `logoutClearsTokenAndReturnsToLogin` | `.\gradlew test` |
| `.\gradlew test` passes | PASS (16 tests, 0 failures); `assembleDebug` also BUILD SUCCESSFUL | `.\gradlew assembleDebug test` |

## 4. What changed
- `data/repository/SessionStore.kt`: token + user in DataStore; `clear()` wipes everything on logout.
- `data/repository/SalesRepository.kt`: `login` (saves session on success), `dashboardToday`, `logout`.
- `di/ConfigModule.kt`: now also provides the DataStore. `di/NetworkModule.kt`: builds the API with the interceptor reading the saved token; a 401 on a call that carried a token clears the session.
- `ui/AirconNavHost.kt`: `SessionViewModel` + NavHost; the saved token decides login vs dashboard, back stack cleared on each switch.
- `ui/login/LoginViewModel.kt`, `LoginScreen.kt`: username, hidden password, Log in button, progress bar, API error text.
- `ui/dashboard/DashboardViewModel.kt`, `DashboardScreen.kt`: minimal dashboard (total + Log out); full screen comes in 2.4.
- `ui/Format.kt`: `formatKs` ("3,660,000 Ks").
- `MainActivity.kt`: hosts `AirconNavHost`.
- `test/.../ui/LoginFlowTest.kt` (Hilt + Robolectric + MockWebServer), `ui/TestHelpers.kt`.

## 5. Decisions I made
- Navigation follows the saved token instead of each screen navigating: login, logout and "401 anywhere" all just change the token, and the screen follows. One place, no missed cases.
- The 401 → logout lives in the OkHttp interceptor, so every authenticated call (now and later) gets it. A 401 on login (no token sent) does not trigger it.
- Username is trimmed before sending; password is sent as typed.
- Network failure on login shows "Can't reach the server. Check the connection and try again."
- UI tests use the real `MainActivity` with Hilt; only the base URL and DataStore are replaced (`@UninstallModules(ConfigModule)` + `@BindValue`).

## 6. Questions for the owner
None.

## 7. Not checked / risks
- `android:allowBackup="true"` (template default) means Android backup could include the saved token. Not changed (out of scope); worth deciding before release.
- Token expiry is only noticed when the API returns 401; the app does not read `expires_in`.

## 8. Commit
See `git log` (message `task 2.3: login screen + saved token`).
