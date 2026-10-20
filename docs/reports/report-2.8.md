# Report 2.8

## 1. Goal
Task 2.8: Previews in Android Studio

## 2. Status
DONE. **Stop for review.**

## 3. Checks
| Check | Result | Command |
|---|---|---|
| `.\gradlew assembleDebug` | PASS (BUILD SUCCESSFUL) | `.\gradlew assembleDebug` |
| `.\gradlew test` | PASS (29 tests, 0 failures) | `.\gradlew test` |
| `.\gradlew verifyRoborazziDebug` | PASS (6 screenshots match) | `.\gradlew verifyRoborazziDebug` |
| `.\gradlew lint` | PASS: 0 errors, warnings only | `.\gradlew lint` |
| Extra: previews not in the release build | PASS: release compiles; `*PreviewsKt` classes exist only under `build/.../debug/`, none under release | `.\gradlew compileReleaseKotlin`, `find app/build -name "*PreviewsKt*.class"` |

## Previews for the owner
Each function has `@PreviewLightDark`, so it shows twice: light and dark.

| Preview function | File |
|---|---|
| `LoginEmptyPreview` | `android/app/src/debug/java/com/kaungkyaw/airconsales/ui/login/LoginPreviews.kt` |
| `LoginLoadingPreview` | same |
| `LoginErrorPreview` | same |
| `DashboardNormalDayPreview` | `android/app/src/debug/java/com/kaungkyaw/airconsales/ui/dashboard/DashboardPreviews.kt` |
| `DashboardEmptyDayPreview` | same |
| `DashboardNegativeChangePreview` | same |
| `DashboardLoadingPreview` | same |
| `DashboardErrorPreview` | same |
| `DashboardOfflinePreview` | same |

**How to open them:** in Android Studio, open `LoginPreviews.kt` or `DashboardPreviews.kt` (Project view → `app/src/debug/java/...`, or press Shift twice and type the name).
Click **Split** or **Design** at the top-right of the editor. The first time, click **Build & Refresh** in the preview pane.
The build variant must be `debug` (the default).

## 4. What changed
- `ui/login/LoginScreen.kt`: UI moved into `LoginContent(username, password, error, loading, ...)` without the ViewModel, so it can be previewed without Hilt. `LoginScreen` just passes the ViewModel's state in. No behaviour change.
- `src/debug/.../ui/login/LoginPreviews.kt` (new): 3 login previews.
- `src/debug/.../ui/dashboard/DashboardPreviews.kt` (new): 6 dashboard previews, data copied from the contract fixtures `normal_day.json` / `empty_day.json` as Kotlin values.

## 5. Decisions I made
- Previews are in the **debug** source set, same package as each screen. That keeps them out of the release build for certain (release has no R8 shrinking yet, so a preview in `src/main` would ship).
  In Android Studio they show under `app/src/debug/java`, not in the same folder as the screen file.
- Used `@PreviewLightDark` (one annotation = light + dark) instead of two `@Preview`s per function.
- Negative change preview uses the same numbers as the screenshot test (yesterday 4,182,857 Ks, ▼ 12.5%).

## 6. Questions for the owner
- Do the previews show what you want to check? Look especially at the **dark** versions; this is the first time dark mode is visible (brand tints from 2.7).
- From 2.7: backgrounds and cards keep Material's default light grey with a faint purple tint. OK, or pure white/grey?

## 7. Not checked / risks
- I could not open Android Studio's preview pane from here; previews compile, but rendering in the IDE was not seen.
- Preview data is a copy of the fixtures. If the fixtures change, the previews don't follow automatically (tests still do).

## 8. Commit
See `git log` for `task 2.8: previews in Android Studio`.
