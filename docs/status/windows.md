# Status: Windows PC

Overwritten by Claude Code at the end of every `/next` run on the Windows PC.

- **Last task:** 2.10: Neutral backgrounds + release build hardening
- **Status:** DONE, stopped for review
- **Commit:** aa7d8f1 `task 2.10: neutral backgrounds + release build hardening`
- **Tasks this run:** 2.9 (8510d86), 2.10 (aa7d8f1). Both DONE.

## Open questions for the owner
- Do the neutral backgrounds look right? See `android/app/src/test/screenshots/dashboard_normal_day.png` (light) and the dark previews in Android Studio.
- To try the release build on the phone it must be signed. Make a release signing key now (kept out of git), or wait for 3.6 (HTTPS) when the release URL is known?

## Facts for the planner
- 2.9: the app reads `Retry-After` (seconds) on any API error. With a 429 it shows the API message plus "Try again in m:ss" and keeps Log in disabled until 0. A 429 without the header shows the message but doesn't lock. The countdown resets if the app is restarted (the server still enforces the limit).
- 2.10: R8 is on for release (`isMinifyEnabled`, `isShrinkResources`); release APK is 1.66 MB. No app keep rules were needed: Retrofit 3.0.0, kotlinx-serialization 1.12.0 and Hilt 2.60.1 ship their own. This was checked in `seeds.txt` / `configuration.txt`, **not** by running the release APK (no device, and the APK is unsigned).
- The project template had an `optimization { packageScope = androidx/kotlin/kotlinx }` block that only optimised libraries. It is replaced.
- Release `API_BASE_URL` is still `https://api.invalid/` (placeholder until 3.6).
- **Flaky test (pre-existing):** `SetupTest.appStartsWithLabel` failed once out of about 6 full runs. It checks for the login screen right after launch, before DataStore has loaded. Not changed (hard rule). Suggest allowing a change to `compose.waitForText("Aircon Sales")`.
- Tests: 32 unit/Robolectric tests, 7 Roborazzi screenshots (all re-recorded with neutral colours). Lint: 0 errors, 21 warnings.
- Gradle from a plain shell still needs `JAVA_HOME=C:\Program Files\Android\Android Studio\jbr`.
