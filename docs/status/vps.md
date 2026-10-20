# Status: VPS

Overwritten by Claude Code at the end of every `/next` run.

- **Last task:** 1.5 — Contract tests
- **Status:** NEEDS REVIEW (all checks pass; stopped for review at the end of Phase 1, as the task requires)
- **Commit:** a3c4d68
- **Also done this run (all DONE):** 1.1 error handling `b01f4c2`, 1.2 login with JWT `fcc36d8`,
  1.3 `/dashboard/today` `cd921d5`, 1.4 Yangon day boundaries `b3099f4`
- **Open questions (from report-1.5):** none.
- **Facts for the planner:**
  - 61 tests pass (`api/.venv/bin/pytest`, ~40 s; Schemathesis is most of it).
  - Live container `aircon-api` was rebuilt with Phase 1 and runs on `127.0.0.1:8000` (DB `127.0.0.1:5433`, D21).
    Login `owner` / `owner123` → `/dashboard/today` returns 200 and matches the contract.
  - Schemathesis found two real bugs, both fixed: error responses dropped headers (`Allow` on 405, `WWW-Authenticate` on 401),
    and a body that isn't valid UTF-8 gave an undocumented 400 (now 422 `validation_error`).
  - `JWT_SECRET` must be ≥ 32 chars or the API won't start; the VPS `.env` has 64. `.env.example` updated.
  - The Docker CLI works here only through `sg docker -c "…"` (the session doesn't pick up the `docker` group yet; a re-login fixes it).
  - New pinned deps: PyJWT 2.15.1, PyYAML 6.0.3, schemathesis 4.32.2. Test-only packages are still in the one `requirements.txt` (so they're in the image too).
  - The seeded "today" in `aircon` is from the 10-20 seed run (D20); reseed for fresh numbers.
  - Before exposing the API (Phase 3): add login rate limiting (not built yet).
