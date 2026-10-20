# Report 2.7

## 1. Goal
Task 2.7: Fixed brand colours and safer backup settings

## 2. Status
DONE

## 3. Checks
| Check | Result | Command |
|---|---|---|
| `dynamicColor` not used anywhere | PASS (no matches) | `grep -rn "dynamicColor\|dynamic.*ColorScheme" android/app/src` |
| Theme uses primary `#0057B8`, secondary `#00A3E0` | PASS (`ui/theme/Color.kt` → `Theme.kt` light scheme) | read code |
| `allowBackup="false"` in the manifest | PASS | `grep allowBackup android/app/src/main/AndroidManifest.xml` |
| Backup rules exclude all data | PASS: `backup_rules.xml` (before Android 12) and `data_extraction_rules.xml` (cloud backup + device transfer) exclude every domain | read files |
| `.\gradlew recordRoborazziDebug` then `.\gradlew verifyRoborazziDebug` | PASS, all 6 images re-recorded and committed | both commands |
| `.\gradlew test` | PASS (29 tests, 0 failures) | `.\gradlew test` |
| `.\gradlew lint` | PASS: 0 errors, warnings only (old library versions, unused template colours in `colors.xml`, debug cleartext) | `.\gradlew lint` |

## 4. What changed
- `ui/theme/Color.kt`: template purple removed; brand blue/sky (+ lighter dark-theme tints) and green/red change colours, all in one place.
- `ui/theme/Theme.kt`: fixed light and dark schemes; `dynamicColor` parameter and wallpaper colours removed.
- `ui/dashboard/DashboardScreen.kt`: ▲/▼ colours now come from `Color.kt` instead of private values.
- `AndroidManifest.xml`: `allowBackup="false"`.
- `res/xml/backup_rules.xml`, `res/xml/data_extraction_rules.xml`: exclude every domain (D29).
- `app/src/test/screenshots/*.png`: re-recorded with the new colours.

## 5. Decisions I made
- Dark theme uses lighter tints of the brand colours (primary `#9EC5FF`, secondary `#7FD6F5`) so they are readable on dark backgrounds; the exact brand hex values are for the light theme. Change in `Color.kt`.
- Only primary/secondary are set; backgrounds and cards keep Material 3's default neutral (slightly purple-tinted) surfaces.

## 6. Questions for the owner
- The brand blue shows on buttons and the "Log out" link. Backgrounds and cards are still Material's default light grey with a faint purple tint. OK, or should they be pure white/grey (or light blue)?

## 7. Not checked / risks
- Dark theme is not covered by a screenshot (none exist yet; task 2.8 adds dark previews).
- Backup exclusion was not tested on a device (`adb shell bmgr`); it follows Android's documented rules.

## 8. Commit
See `git log` for `task 2.7: fixed brand colours and safer backup settings`.
