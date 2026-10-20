# Report 2.4

## 1. Goal
Task 2.4: Today dashboard screen

## 2. Status
DONE

## 3. Checks
| Check | Result | Command |
|---|---|---|
| ViewModel test, `normal_day`: formatted strings (`3,660,000 Ks`, `5 invoices`, `Tue, 20 Oct 2026`, categories, methods, Not fully paid, voided), arrow `▲ 20.0% vs yesterday` / UP | PASS `DashboardViewModelTest.normalDay` | `.\gradlew test` |
| ViewModel test, `empty_day`: zeros, `No sales yesterday` (null change), no methods, no "Voided today" | PASS `DashboardViewModelTest.emptyDay` | `.\gradlew test` |
| Negative change `▼ 12.5%` / DOWN (and 0.0 → flat, no arrow) | PASS `DashboardViewModelTest.negativeAndZeroChange` | `.\gradlew test` |
| Roborazzi screenshots: normal day, empty day, negative change; images committed | PASS (recorded with `recordRoborazziDebug`) | `.\gradlew recordRoborazziDebug` |
| `.\gradlew test` | PASS (22 tests, 0 failures) | `.\gradlew test` |
| `.\gradlew verifyRoborazziDebug` | PASS; also confirmed it FAILS when the green arrow colour is changed (then restored) | `.\gradlew verifyRoborazziDebug` |

Screenshots (open these):
- `android/app/src/test/screenshots/dashboard_normal_day.png`
- `android/app/src/test/screenshots/dashboard_empty_day.png`
- `android/app/src/test/screenshots/dashboard_negative_change.png`

## 4. What changed
- `ui/dashboard/DashboardUi.kt`: `DashboardToday.toUi()`, all display strings and the trend (UP/DOWN/FLAT/NONE) in one tested function.
- `ui/dashboard/DashboardViewModel.kt`: state holds `DashboardUi`; `refreshing` flag for pull to refresh (numbers stay on screen while refreshing).
- `ui/dashboard/DashboardScreen.kt`: big total, invoice count, date, coloured change line, 3 category cards, Payment methods, Not fully paid, Voided today (only if > 0), pull to refresh, Log out. Stateless `DashboardContent` so screenshots need no network.
- `test/.../ui/dashboard/DashboardViewModelTest.kt`: ViewModel + real repository against MockWebServer with the contract fixtures.
- `test/.../ui/dashboard/DashboardScreenshotTest.kt` + `test/screenshots/*.png`.

## 5. Decisions I made
- Labels: Aircon / Accessories / Service; Cash / Bank / KBZPay / WavePay / Other. Unknown values from the API show as-is.
- Change line: `▲ 20.0% vs yesterday` (green), `▼ 12.5% vs yesterday` (red), `0.0% vs yesterday` (grey, no arrow), `No sales yesterday` (grey).
- Category quantity shown as `Qty 2`. Date shown as `Tue, 20 Oct 2026` (English).
- Payment method with no sales today: "No payments yet".
- The screenshot test files use a phone size of 411×891 dp. The images use the app's theme as-is. On Android 12+ phones the app takes its colours from the wallpaper (template default), so colours on a real phone can differ from the screenshots.

## 6. Questions for the owner
- Should the app use fixed brand colours instead of the phone's wallpaper colours (Android 12+)? Today it follows the wallpaper (template default).

## 7. Not checked / risks
- Not seen on a real phone or emulator yet (task 2.6). Very large totals (e.g. 1,000,000,000 Ks) in the narrow category cards are not tested and may wrap.

## 8. Commit
See `git log` (message `task 2.4: today dashboard screen`).
