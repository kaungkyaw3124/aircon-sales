# Report 1.2

## 1. Goal
Task 1.2 — Login with JWT

## 2. Status
DONE

## 3. Checks

| Done when | Result | Command |
|---|---|---|
| Correct login: 200, fields match contract, `expires_in` matches config | PASS | `test_correct_login` (also checks claims `sub`/`role`/`exp` and that the token works) |
| Wrong password / unknown user / inactive user → identical 401 body | PASS | `test_wrong_password_unknown_user_inactive_user_give_identical_401` |
| Missing fields → 422 | PASS | `test_missing_fields_give_422` (4 cases, incl. empty username) |
| Expired token → 401 | PASS | `test_expired_token_gives_401` |
| Token signed with another secret → 401 | PASS | `test_token_signed_with_another_secret_gives_401` |
| User deactivated after token issued → 401 | PASS | `test_user_deactivated_after_token_issued_gives_401` |
| Short `JWT_SECRET` refuses to start | PASS | `test_short_jwt_secret_refuses_to_start` (`""`, `short`, 31 chars), plus `test_32_char_jwt_secret_starts` as control |
| All tests pass | PASS | `.venv/bin/pytest` |

pytest:
```
31 passed in 13.71s
```

## 4. What changed
- `api/app/auth.py` (new): `POST /auth/login`, `make_token`, `get_current_user` dependency.
- `api/app/clock.py` (new): `now()` dependency (UTC), overridable in tests.
- `api/app/config.py`: `JWT_SECRET` shorter than 32 chars fails settings validation, so `import app.main` (and uvicorn) exits.
- `api/app/db.py`: `get_db` session dependency.
- `api/app/main.py`: includes the auth router.
- `api/requirements.txt`: `PyJWT==2.15.1`.
- `api/.env.example`: `JWT_SECRET` placeholder is now 32+ chars, with a comment on how to generate one.
- `api/tests/conftest.py`: `db` (session inside the rolled-back test transaction), `client` (overrides `get_db`), `make_user`.
- `api/tests/test_auth.py` (new).

## 5. Decisions I made
- Unknown username still runs one bcrypt check (against a dummy hash) so response time doesn't reveal whether the user exists.
- `get_current_user` reads the user from the DB on every request (needed for "deactivated after login"); role is taken from the DB user, the `role` claim is informational.
- 401 `unauthorized` responses include `WWW-Authenticate: Bearer`.
- PyJWT checks `exp` against real time; `make_token` takes the issue time so tests can make expired tokens.
- The VPS `.env` already has a 64-char secret, so nothing to change there.

## 6. Questions for the owner
None.

## 7. Not checked / risks
- A completely absent `JWT_SECRET` also refuses to start (pydantic required field), but isn't a separate test because `api/.env` always provides one; the empty-string case is tested.
- No login rate limiting (not asked). Worth adding before the API is exposed (Phase 3).

## 8. Commit
See `git log -- docs/reports/report-1.2.md` (`task 1.2: login with JWT`).
