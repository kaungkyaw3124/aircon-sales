# Status: Windows PC

Overwritten by Claude Code at the end of every `/next` run on the Windows PC.

- **Last task:** 2.5 — Loading, error and offline states
- **Status:** DONE, stopped for review (end of Phase 2 build)
- **Commit:** 4ac405c `task 2.5: loading, error and offline states`
- **Tasks this run:** 2.1 (1555c48), 2.2 (657f1c6), 2.3 (204f5f2), 2.4 (6a1410c), 2.5 (4ac405c). All DONE.

## Open questions for the owner
- Look at the 6 screenshots in `android/app/src/test/screenshots/` (normal day, empty day, negative change, loading, error, offline). Are layout, wording and colours OK?
- Fixed brand colours, or follow the phone's wallpaper colours on Android 12+ (current, template default)?

## Facts for the planner
- JDK: Android Studio's JBR 25 (`JAVA_HOME` = `C:\Program Files\Android\Android Studio\jbr`). Robolectric needs `--add-exports java.base/jdk.internal.access` on JDK 25 (set in `app/build.gradle.kts`).
- AGP 9.4.1, Gradle 9.6.0, Kotlin bumped 2.2.10 → 2.4.21, KSP 2.3.12, Hilt 2.60.1, Retrofit 3.0.0, OkHttp 4.12.0, Robolectric 4.17 (runs at SDK 36; app targets 37), Roborazzi 1.76.0.
- AGP 9 only runs debug unit tests: `.\gradlew test` = `testDebugUnitTest` (29 tests).
- Contract: `ContractFixturesTest` compares `android/app/src/test/resources/contract/*.json` with every response example in `docs/openapi.yaml` (example name = file name). **When the contract changes (e.g. D25's `429 rate_limited` example), this test fails until the fixture is added**. That's on purpose, and the Android follow-up is to add the fixture.
- Screenshots: record with `.\gradlew recordRoborazziDebug`, check with `.\gradlew verifyRoborazziDebug`.
- Release `API_BASE_URL` is a placeholder (`https://api.invalid/`) until task 3.4.
- Lint: 0 errors, 21 warnings (old template library versions, unused template colours, debug-only cleartext).
- `android:allowBackup="true"` (template) could put the saved token in Android backups; worth a decision before release.
