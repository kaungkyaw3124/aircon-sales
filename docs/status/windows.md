# Status: Windows PC

Overwritten by Claude Code at the end of every `/next` run on the Windows PC.

- **Last task:** 2.8 — Previews in Android Studio
- **Status:** DONE, stopped for review
- **Commit:** b24bc1d `task 2.8: previews in Android Studio`
- **Tasks this run:** 2.6 (57e6ae2), 2.7 (d0c8945), 2.8 (b24bc1d). All DONE.

## Open questions for the owner
- Do the previews (`LoginPreviews.kt`, `DashboardPreviews.kt`, light + dark) show what you want to check? Look at the dark versions especially.
- Backgrounds and cards keep Material's default light grey with a faint purple tint. OK, or pure white/grey (or light blue)?

## Facts for the planner
- Planner's D26 change needed nothing more: no other `10.0.2.2` references. `android/README.md` + `android/run-on-phone.ps1` added (exit 2 = no device).
- Brand colours live in `ui/theme/Color.kt`. Dark theme uses lighter tints (`#9EC5FF`, `#7FD6F5`), not the exact brand hex values.
- `allowBackup="false"`; both backup rule files exclude every domain.
- `LoginScreen` now wraps a stateless `LoginContent` (for previews); no behaviour change, tests unchanged.
- Previews are in `app/src/debug/java/...` (same package as the screens) so they never ship: release has **no R8/minify** yet. Worth turning on before release (Phase 3.4?).
- Gradle from a plain shell needs `JAVA_HOME=C:\Program Files\Android\Android Studio\jbr`.
- Tests: 29 unit/Robolectric tests, 6 Roborazzi screenshots (re-recorded with brand colours). Lint: 0 errors.
- Unchanged from before: `ContractFixturesTest` fails on purpose when the contract gains examples (e.g. D25's `429`) until the fixture is added.
