# Report 2.6

## 1. Goal
Task 2.6: Verify the planner's debug-URL change + "run on phone" guide

## 2. Status
DONE

## 3. Checks
| Check | Result | Command |
|---|---|---|
| `.\gradlew assembleDebug` | PASS (BUILD SUCCESSFUL) | `.\gradlew assembleDebug` |
| `.\gradlew test` | PASS (29 tests, 0 failures; `SetupTest` checks `http://127.0.0.1:8000/`) | `.\gradlew test` |
| No `10.0.2.2` outside build output | PASS (no matches) | `grep -rn "10.0.2.2" android --include=*.kt --include=*.kts --include=*.md \| grep -v /build/` |
| `run-on-phone.ps1` without a device prints "no device", non-zero exit | PASS: prints `No device connected. Plug in the phone ...`, exit code 2 | `powershell -ExecutionPolicy Bypass -File android\run-on-phone.ps1` |

## 4. What changed
- `android/README.md` (new): "Run on a phone or emulator" steps for the owner + common errors.
- `android/run-on-phone.ps1` (new): reads `sdk.dir` from `local.properties`, runs `adb devices` and `adb reverse tcp:8000 tcp:8000`, exits 2 when no device.

## 5. Decisions I made
- Planner's change (0ae1e5d) needed nothing more: no other file referred to `10.0.2.2`.
- Script exit codes: 2 = no device, 1 = setup problem (no `local.properties`, no adb, reverse failed).

## 6. Questions for the owner
- None.

## 7. Not checked / risks
- The script's "device connected" path was not run here (no phone attached to this PC during the run).
- Gradle needs `JAVA_HOME` = Android Studio's JBR when run from a plain shell.

## 8. Commit
See `git log` for `task 2.6: verify debug URL + run-on-phone guide`.
