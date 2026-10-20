# Report 2.1

## 1. Goal
Task 2.1: App foundation

## 2. Status
DONE

## 3. Checks
| Check | Result | Command |
|---|---|---|
| Debug build | PASS (BUILD SUCCESSFUL) | `.\gradlew assembleDebug` |
| Unit tests incl. one Robolectric test | PASS (1 test: `SetupTest.appStartsWithLabel`) | `.\gradlew test` |

## 4. What changed
- `android/gradle/libs.versions.toml`: added Hilt, KSP, Retrofit + kotlinx-serialization converter, OkHttp + MockWebServer, kotlinx-serialization, DataStore, Navigation Compose, lifecycle-viewmodel-compose, hilt-lifecycle-viewmodel-compose, Robolectric, Roborazzi, coroutines-test, Turbine, SnakeYAML (test), androidx-test-core. Kotlin 2.2.10 → 2.4.21.
- `android/build.gradle.kts`: declares the new plugins.
- `android/app/build.gradle.kts`: plugins, dependencies, `BuildConfig.API_BASE_URL` (debug `http://10.0.2.2:8000/`), Robolectric resources, JDK 25 test JVM flags, `docs/openapi.yaml` declared as a test input (for task 2.2).
- `app/src/debug/AndroidManifest.xml` + `app/src/debug/res/xml/network_security_config.xml`: cleartext HTTP allowed only in debug.
- `AndroidManifest.xml`: `INTERNET` permission, `AirconApp` application.
- `res/values/strings.xml`: app label "Aircon Sales".
- `AirconApp.kt` (`@HiltAndroidApp`), `MainActivity.kt` (`@AndroidEntryPoint`, placeholder screen), `di/ConfigModule.kt` (base URL provider, replaceable in tests).
- `test/.../SetupTest.kt`: Robolectric boots the real Hilt activity. `robolectric.properties`: `sdk=36`.
- Deleted `ExampleUnitTest.kt` (template 2+2 test, replaced by `SetupTest`).

## 5. Decisions I made
- Kotlin bumped to 2.4.21: current androidx/Hilt/serialization libraries need a newer Kotlin compiler than 2.2.10.
- OkHttp pinned to 4.12.0 because Retrofit 3.0.0 depends on it; MockWebServer must match.
- Robolectric runs at SDK 36 (`robolectric.properties`): Robolectric 4.17 has no SDK 37 image yet. The app still compiles/targets 37.
- Release `API_BASE_URL` is a placeholder `https://api.invalid/` until task 3.4.
- `data/` and `ui/login`, `ui/dashboard` packages are created by tasks 2.2–2.4 (git does not keep empty folders).

## 6. Questions for the owner
None.

## 7. Not checked / risks
- AGP 9 only creates unit tests for the debug build type, so `.\gradlew test` runs `testDebugUnitTest` only.
- Robolectric on JDK 25 needs `--add-exports java.base/jdk.internal.access`; a future JDK could break that again.

## 8. Commit
See `git log` (message `task 2.1: app foundation`).
