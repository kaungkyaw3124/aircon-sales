# Status: VPS

Overwritten by Claude Code at the end of every `/next` run.

- **Last task:** 3.5 — Go-live checklist (`docs/GO-LIVE.md`)
- **Status:** NEEDS REVIEW (all checks pass; the task says stop for review)
- **Commit:** 55bba84
- **Also done this run:**
  - 3.3 login rate limiting, contract v0.1.1, DONE, `9306a67` → **Windows 2.9 can run now**
  - 3.4 production hardening, DONE, `4371647`
- **Open questions (from report-3.5):**
  1. Who are the real users (username, full name, role)? Needed for GO-LIVE step 10.
  2. For 3.6: domain name, and Cloudflare Tunnel or Nginx + Let's Encrypt?
  3. For 3.7: where does the off-site backup copy go? (open since D31)
- **Facts for the planner:**
  - Contract is now **v0.1.1**: `POST /auth/login` has `429` with `Retry-After` (integer seconds, ≥ 1) and the `rate_limited` example. Nothing else changed.
  - Rate limit state is the `login_failures` table (migration `0002`), one row per failed login. Refused (429) attempts are
    not recorded, so a lock ends 15 min after the failure that started it. The 429 message is always the fixed contract text;
    the real wait is `Retry-After`.
  - **All requests reach the container from the Docker gateway `172.19.0.1`.** With `TRUSTED_PROXIES` empty (default),
    every client shares one IP counter (20 wrong passwords from anyone → everyone locked 15 min). Fine behind the SSH tunnel;
    **3.6 must set `TRUSTED_PROXIES`** to the proxy's address and have the proxy send `X-Forwarded-For`.
  - Uvicorn now runs `--no-proxy-headers` (the old `--forwarded-allow-ips '*'` let anyone fake their IP); the app reads the header itself.
  - `APP_ENV=production`: `/docs`, `/redoc`, `/openapi.json` → 404. Log rotation (10m × 5) on both containers; containers were
    recreated for it (Postgres restarted, dev data kept).
  - `scripts/create_user.py` runs inside the image: `docker exec -it aircon-api python scripts/create_user.py …`.
  - Backups: 14 daily + first-of-month for 12 months; `~/aircon-backups/LAST_OK` / `LAST_FAILED`. Nothing alerts on failure yet.
  - On a production `.env`, run tests as `APP_ENV=development pytest` (tests only touch `aircon_test`; otherwise the seed safety refuses them).
  - `.gitignore` / `.dockerignore` exclude `.env` exactly, not `.env.*`. GO-LIVE keeps its `.env` copy outside the repo because of that. Suggest widening.
  - Ports 80 and 443 are free on the VPS.
  - 85 tests pass (~80 s; the IP-limit tests do 20 full-cost bcrypt checks each).
