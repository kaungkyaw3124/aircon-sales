# Report 2.10

## 1. Goal
Task 2.10: Neutral backgrounds + release build hardening

## 2. Status
DONE. **Stop for review.**

## 3. Checks
| Check | Result | Command |
|---|---|---|
| `.\gradlew assembleRelease` (unsigned) | PASS: `app-release-unsigned.apk`, 1.66 MB (debug is 13.5 MB) | `.\gradlew assembleRelease` |
| `.\gradlew assembleDebug` | PASS | `.\gradlew assembleDebug` |
| Serialization models survive R8 | PASS by inspection, no test (see below) | `build/outputs/mapping/release/{seeds,configuration}.txt` |
| `.\gradlew recordRoborazziDebug` | PASS: all 7 images re-recorded | `.\gradlew recordRoborazziDebug` |
| `.\gradlew verifyRoborazziDebug` | PASS | `.\gradlew verifyRoborazziDebug` |
| `.\gradlew test` | PASS (32 tests, 0 failures) | `.\gradlew test` |
| `.\gradlew lint` | PASS: 0 errors, 21 warnings | `.\gradlew lint` |
| Release is HTTPS only | PASS: the merged release manifest has no `usesCleartextTraffic` / `networkSecurityConfig`, so targetSdk 37's default (no cleartext) applies. The cleartext config is only in `src/debug` | grep of `build/intermediates/merged_manifest/release/.../AndroidManifest.xml` |

All of these were run together in one go: `.\gradlew assembleRelease assembleDebug verifyRoborazziDebug test lint --rerun-tasks` → BUILD SUCCESSFUL.

### How R8 + serialization was checked (no test)
AGP unit tests always run on the classes before R8, even for the release variant. A test on the shrunk code needs a device (instrumented test). So I checked what R8 was told to keep and what it did keep:
- `configuration.txt` includes the rules that ship inside the libraries: kotlinx-serialization 1.12.0 (`kotlinx-serialization-common.pro`), Retrofit 3.0.0 (`retrofit2.pro`), Hilt 2.60.1 and hilt-lifecycle-viewmodel. `-keepattributes Signature, InnerClasses, EnclosingMethod` and `RuntimeVisibleAnnotations` are on.
- `seeds.txt` (what R8 kept) has each model's `Companion` field and `Companion.serializer()` (e.g. `LoginResponse$Companion: KSerializer serializer()`), plus `AirconApi.login(...)` and `AirconApi.dashboardToday(...)`.
- Model classes get short names (`LoginResponse -> pr0`). That is fine: JSON field names live in the generated serializers as strings (`@SerialName`), not in class or field names.
- So no extra app keep rules were needed. `src/main/keepRules/rules.keep` now says so.

**Not proven:** the release APK was never run on a phone (no device here, and the APK is unsigned).

## Screenshots (re-recorded)
- `android/app/src/test/screenshots/dashboard_normal_day.png`
- `android/app/src/test/screenshots/dashboard_empty_day.png`
- `android/app/src/test/screenshots/dashboard_negative_change.png`
- `android/app/src/test/screenshots/dashboard_loading.png`
- `android/app/src/test/screenshots/dashboard_error.png`
- `android/app/src/test/screenshots/dashboard_offline.png`
- `android/app/src/test/screenshots/login_rate_limited.png`

All screenshots are light theme. The dark colours (`#121212` / `#1E1E1E`) show in the Android Studio previews (`LoginPreviews.kt`, `DashboardPreviews.kt`, dark versions).

## 4. What changed
- `ui/theme/Color.kt`: added `BackgroundLight #FFFFFF`, `CardLight #F2F4F7`, `BackgroundDark #121212`, `CardDark #1E1E1E` (D32).
- `ui/theme/Theme.kt`: both colour schemes set `background`, `surface` to the background colour and `surfaceVariant` + all `surfaceContainer*` to the card colour. Brand blue stays as `primary`.
- `app/build.gradle.kts`: release uses `isMinifyEnabled = true`, `isShrinkResources = true`. Removed the template's `optimization { packageScope = androidx/kotlin/kotlinx }` block, which only optimised libraries, not the app's own code.
- `src/main/keepRules/rules.keep`: template comments replaced with a note on why no app rules are needed.
- `src/test/screenshots/*.png`: 7 images re-recorded.
- `docs/reports/report-2.9.md`: filled in the commit hash.

## 5. Decisions I made
- All `surfaceContainer*` tones get the card colour (not only `surfaceContainerHighest`, which `Card` uses), so no other Material part keeps the purple tint.
- No custom keep rules: the libraries' own rules cover Retrofit, kotlinx.serialization and Hilt (see above).
- `primaryContainer` / `secondaryContainer` keep Material's defaults. The app doesn't use them now.

## 6. Questions for the owner
- Do the neutral backgrounds look right? Look at `dashboard_normal_day.png` (light) and the dark previews in Android Studio.
- To try the release build on the phone, it must be signed. Should we make a release signing key now (kept out of git), or wait until 3.6 (HTTPS) when the release URL is known?

## 7. Not checked / risks
- The release APK has not been run on a device. R8 is checked through the mapping files only.
- The release `API_BASE_URL` is still the placeholder `https://api.invalid/` (comes with 3.6 HTTPS).
- No dark-theme screenshot tests, only previews.
- `SetupTest` race from report 2.9: passed in every run this time.

## 8. Commit
See `docs/status/windows.md` (the hash is only known after this commit).
