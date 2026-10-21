# Report 3.5

## 1. Goal
Task 3.5 — Go-live checklist

## 2. Status
NEEDS REVIEW (all checks pass; the task says stop for review)

## 3. Checks

| Check | Result | Command |
|---|---|---|
| `docs/GO-LIVE.md` exists | PASS | `ls docs/GO-LIVE.md` |
| Every command dry-run where safe | PASS (list below) | see below |
| All tests pass | PASS — 85 passed in 79 s | `cd api && .venv/bin/pytest -q` |
| Stop for review | — | stopping here |

**Dry-run (on the dev setup, nothing switched):**
- Step 1: `pytest -q` → 85 passed.
- Step 2: `backup.sh` → `backup OK`, `LAST_OK` written (moving the dumps aside was *not* run).
- Step 6: the secret-generation + `sed` lines on a **copy of `.env.example`** in the scratchpad: `APP_ENV=production`,
  new password in `POSTGRES_PASSWORD` and both URLs (3 matches), new `JWT_SECRET`; copy deleted.
- Step 8: `docker compose config --quiet` ok; `/health`, `/docs` curl and the `psql` count query on dev (dev gives `docs 200`, 5 users, 499 sales, migration `0002`).
- Step 9: `APP_ENV=production seed.py --reset` → refused, exit 1.
- Step 10: `docker exec aircon-api python scripts/create_user.py --help` (the create itself is covered by pytest in 3.4).
- Step 11: the `printf … | curl --data @-` login with the dev `owner` account → `login 200`.
- Step 12: `crontab -l | grep backup.sh` → the 20:00 UTC line.
- Step 13: `restore_check.sh <newest dump>` → `restore check OK: all row counts match`.
- Step 14: ran `APP_ENV=production pytest` once to see what happens: 3 docs tests fail and 5 seed tests refuse to set up
  (the safety works). Hence the `APP_ENV=development` prefix in step 14, which only affects the test process.
- Ports: `ss -ltn` → 80 and 443 free on the VPS (for the 3.6 section).

**Not dry-run (destructive or changes the live setup):** step 2's `mv`, step 3 (copy of real `.env`), 4 (`compose down`),
5 (`volume rm`), 6 on the real `.env`, 7, 8 `up` in production, 10 real users, and the roll-back.

## 4. What changed
- `docs/GO-LIVE.md` — new: before-the-day list, 15 numbered go-live steps with expected output, roll-back, and
  "Before exposing to the internet" (what 3.6 needs from the owner).

## 5. Decisions I made
- Empty database = **delete the Docker volume** and let Postgres re-initialise with the new password. Simpler than
  `ALTER USER` + dropping tables, and the init script recreates `aircon_test` too. The fake data is backed up first.
- Fake-data dumps are moved to `~/aircon-backups/dev-before-golive/`, otherwise monthly retention would keep a fake
  dump as October's monthly backup.
- The roll-back copy of `.env` goes to `~/aircon-backups/env.dev-backup`, **not** `api/.env.dev-backup`:
  `.gitignore` and `.dockerignore` only exclude `.env` exactly, so a copy in `api/` could be committed or baked into the image.
- Passwords for the login check are read with `read -s` and piped into curl, so they stay out of history and `ps`.
- The owner saves the new Postgres password in a password manager; the JWT secret isn't saved (losing it only logs everyone out).

## 6. Questions for the owner
1. Who are the real users (username, full name, role)? Needed for step 10.
2. For 3.6: domain name, and Cloudflare Tunnel or Nginx + Let's Encrypt? (Details in GO-LIVE.md, last section.)
3. For 3.7: where should the off-site backup copy go? (still open from D31)

## 7. Not checked / risks
- The full go-live run itself was not done (by design). Steps 4–8 together were never run end-to-end; the first real run
  is the test. Roll-back before real data is cheap (fake data is backed up), so that's acceptable.
- `.gitignore`/`.dockerignore` only cover `.env` exactly; I didn't widen them (out of scope). Suggest `.env.*` + `!.env.example`.
- After go-live nothing alerts on `LAST_FAILED`; someone has to look.

## 8. Commit
See `git log` (message: `task 3.5: go-live checklist`).
