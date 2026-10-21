# Report 3.3

## 1. Goal
Task 3.3 — Login rate limiting (contract v0.1.1)

## 2. Status
DONE

## 3. Checks

| Check | Result | Command |
|---|---|---|
| Redocly lint passes | PASS (valid; the same 2 warnings as before: `example.com`-style server, `/health` has no 4xx) | `npx @redocly/cli lint docs/openapi.yaml` |
| Contract diff is only the 429 response, `Retry-After` header, `rate_limited` example, version 0.1.1 | PASS | `git diff docs/openapi.yaml` |
| 5 wrong passwords → 6th (right password) is 429 with `Retry-After` | PASS | `pytest tests/test_rate_limit.py::test_sixth_attempt_is_limited_even_with_right_password` |
| Another username still works | PASS | `…::test_other_username_still_works` |
| After the window (clock moved) login works again | PASS | `…::test_login_works_again_after_window` (1 s before: 429 `Retry-After: 1`; at 15 min: 200) |
| A success resets the counter | PASS | `…::test_success_resets_username_counter` |
| IP limit across different usernames | PASS | `…::test_ip_limit_across_usernames` |
| Counters shared between two app instances | PASS | `…::test_counters_shared_between_app_instances` (two real uvicorn processes on `aircon_test`, failures alternated A/B/A/B/A, 6th on B → 429) |
| Schemathesis passes with the new contract | PASS | `pytest tests/test_contract.py` |
| All tests pass | PASS — 73 passed in 60 s | `cd api && .venv/bin/pytest -q` |

Extra: proxy header ignored unless the peer is trusted, trusted proxy gives the right client IP, old rows deleted
(3 more tests). Models vs. migrations: `alembic compare_metadata` → no differences.
Live container rebuilt (`docker compose up -d --build`): migrated to `0002`, healthy; 5 × 401 then 429 with
`retry-after: 898` for a throwaway username (its rows deleted afterwards).

## 4. What changed
- `docs/openapi.yaml` — v0.1.1: `429` on `POST /auth/login` with `Retry-After` header and `rate_limited` example (D25/D30).
- `api/alembic/versions/0002_login_failures.py` — new table `login_failures` + 3 indexes.
- `api/app/models.py` — `LoginFailure` model.
- `api/app/auth.py` — check limits before the password, record failures, reset on success, clean old rows, `client_ip()`.
- `api/app/config.py`, `api/.env.example` — `TRUSTED_PROXIES` (comma-separated IPs, default empty = trust none).
- `api/docker/entrypoint.sh` — `--proxy-headers --forwarded-allow-ips '*'` → `--no-proxy-headers` (that setting let anyone fake their IP).
- `api/tests/test_rate_limit.py` — 9 tests.
- `docs/schema.md`, `api/README.md` — the new table, how the limit works, how to unlock a user.

## 5. Decisions I made
- Stored one row per failure (a log) rather than a counter per key: a sliding 15-minute window falls out of a `count`, no reset job.
- Attempts refused with 429 are **not** recorded, so a locked user is free exactly 15 minutes after the failure that
  started the lock, not "15 minutes after they last tried". `Retry-After` is computed from that.
- Unknown usernames count too (keyed by the typed name), so guessing names is limited the same way.
- The username key drops NUL and is cut to 200 chars (Postgres text can't hold NUL; huge keys would overflow the index).
- Inactive user + right password counts as a failure (it's a 401 to the client anyway).
- `TRUSTED_PROXIES` is exact IPs, no CIDR ranges. Takes the **last** `X-Forwarded-For` entry (the one our proxy added).
- The message is always "Try again in 15 minutes." (the contract's fixed text); the exact wait is in `Retry-After`.
- Two workers can race and let a 6th failure through at the same instant; no row lock. Harmless for this purpose.

## 6. Questions for the owner
None.

## 7. Not checked / risks
- **Every request through the published port comes from the Docker gateway `172.19.0.1`** (seen in the live table).
  With `TRUSTED_PROXIES` empty, all clients share one IP counter: 20 wrong passwords from anyone in 15 minutes lock
  everyone out. Fine today (only the SSH tunnel reaches it); 3.6 must set `TRUSTED_PROXIES` to the proxy's address
  (likely `172.19.0.1` for a proxy on this host) and make the proxy set `X-Forwarded-For`.
- The test suite is ~20 s slower: IP-limit tests do 20 bcrypt checks at full cost on unknown users.

## 8. Commit
See `git log` (message: `task 3.3: login rate limiting (contract v0.1.1)`).
