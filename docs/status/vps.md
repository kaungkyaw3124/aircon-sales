# Status: VPS

Overwritten by Claude Code at the end of every `/next` run.

- **Last task:** 3.2 — Daily database backup + restore test
- **Status:** NEEDS REVIEW (all checks pass; the task says stop for review)
- **Commit:** 13ae0ec
- **Also done this run:** 3.1 production-ready container, DONE, `c1e530b`
- **Open questions (from report-3.2):**
  1. Off-server copy of backups? Dumps are only on the same VPS now. Google Drive / another server / owner's PC?
  2. Are 14 daily backups enough, or also keep monthly ones for a year?
  3. (report-3.2 "missing" list, item 8) 24 h tokens with no logout/revoke. OK?
- **Facts for the planner:**
  - **Before going public, see report-3.2 → "What is still missing".** Notably: `/docs`, `/redoc` and `/openapi.json` answer **without a token**
    today (breaks the CLAUDE.md security rule; fix for `APP_ENV=production`), there's no script to create real users, and there's no Docker log rotation.
  - Schemathesis found **two old login 500s** during 3.1 (password > 72 bytes, NUL in username). Both now give 401 `invalid_credentials`, with tests. No contract change.
  - Test deps moved to `api/requirements-dev.txt`. `CLAUDE.md` → Commands → API still says `pip install -r requirements.txt`; should be `requirements-dev.txt` for the venv (I didn't edit CLAUDE.md).
  - 64 tests pass (~40 s).
  - Container: migrates on start (exit 1 if migration fails), healthcheck on `/health`, 2 workers, `--proxy-headers` with `--forwarded-allow-ips '*'` (tighten in 3.4).
    Logs: `METHOD /path STATUS ms`, path only, `/health` not logged, timestamps UTC.
  - With 2 workers, 3.3's rate limiter must keep its counters in Postgres (in-memory is per worker).
  - Backups: `~/aircon-backups/`, cron `0 20 * * *` UTC = 02:30 Yangon (server clock is UTC, cron has no per-job TZ). Cron gets the `docker` group fine (proved with a test entry).
    Log at `~/aircon-backups/backup.log`. 3 dev dumps are there now.
  - The Docker CLI in an interactive session still needs `sg docker -c "…"`.
