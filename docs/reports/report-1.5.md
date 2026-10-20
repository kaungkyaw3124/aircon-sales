# Report 1.5

## 1. Goal
Task 1.5 — Contract tests

## 2. Status
NEEDS REVIEW (all checks pass; stopped for review at the end of Phase 1, as the task requires)

## 3. Checks

| Done when | Result | Command |
|---|---|---|
| Schemathesis run passes with no failures | PASS | `.venv/bin/pytest tests/test_contract.py`: in-process ASGI, loads `docs/openapi.yaml`, owner token, all default checks (status codes documented, response schemas, no 500s, …). 3 operations, 3 passed |
| Live `curl` sequence returns 200 and a body matching the contract | PASS | rebuilt with `docker compose up -d --build api`, then the two `curl`s below; both bodies validated against `LoginResponse` / `DashboardToday` from `openapi.yaml` (jsonschema), keys in contract order, `sum(by_category) == total_amount` |
| All tests pass | PASS | `.venv/bin/pytest` (run twice, since Schemathesis inputs are random) |

pytest:
```
61 passed in 39.92s
61 passed in 39.33s
```

Live: `curl -X POST localhost:8000/auth/login -d '{"username":"owner","password":"owner123"}'` → **HTTP 200**
```json
{"access_token":"eyJhbGciOiJIUzI1NiIs…7nrk","token_type":"bearer","expires_in":86400,"user":{"id":1,"username":"owner","full_name":"Shop Owner","role":"owner"}}
```

Live: `curl localhost:8000/dashboard/today -H "Authorization: Bearer <token>"` → **HTTP 200**
```json
{"date":"2026-10-21","currency":"MMK","total_amount":3570000,"invoice_count":3,"void_count":0,"yesterday_total_amount":318000,"change_percent":1022.6,"by_category":[{"category":"aircon","amount":2590000,"quantity":2},{"category":"accessory","amount":750000,"quantity":7},{"category":"service","amount":230000,"quantity":4}],"by_payment_method":[{"payment_method":"cash","amount":370000,"invoice_count":1},{"payment_method":"bank","amount":1965000,"invoice_count":1},{"payment_method":"wavepay","amount":1235000,"invoice_count":1}],"unpaid_count":0,"unpaid_amount":0,"generated_at":"2026-10-21T01:35:52+06:30"}
```

## 4. What changed
- `api/tests/test_contract.py` (new): the Schemathesis test. Builds a small dataset (today's partial + unpaid + voided sale, a sale yesterday) and an owner whose password matches the contract's login example, so the 200 login path is also exercised.
- `api/app/errors.py`: two bugs Schemathesis found:
  - the error handler dropped the exception's headers, so 405 had no `Allow` header (RFC 9110) and 401 had no `WWW-Authenticate`. Headers are now passed through.
  - a body that isn't valid UTF-8 gave FastAPI's `400` (not in the contract). It now gives `422 validation_error`, like any other bad body.
- `api/tests/test_errors.py`: tests for both fixes (`Allow: GET` on 405; undecodable body → 422). Both fail without the fix.
- `api/tests/test_auth.py`: missing-token test also checks `WWW-Authenticate: Bearer`.
- `api/requirements.txt`: `schemathesis==4.32.2`.

## 5. Decisions I made
- Turned off one Hypothesis health check (`function_scoped_fixture`) on the new contract test only: the endpoints only read data, so one dataset shared across the generated inputs is fine.
- Mapped every plain 400 to 422: our code never raises 400 itself, and FastAPI uses it only for an unparseable body.
- Test-only packages (pytest, httpx, schemathesis) are still in the single `requirements.txt`, so they're in the API image too (same as before this task). They could move to `requirements-dev.txt` later.

## 6. Questions for the owner
None.

## 7. Not checked / risks
- The live numbers come from the seed (D20): at 01:35 Yangon it already shows 3 sales "today" between 09:00 and 19:00, and "yesterday" is small because the seed was run on 10-20. Expected for dev data; reseeding fixes it.
- Schemathesis ran in-process (ASGI), not against the container. The container was checked with the curl sequence only.
- No login rate limiting yet (noted in 1.2), needed before Phase 3 exposes the API.

## 8. Commit
See `git log -- docs/reports/report-1.5.md` (`task 1.5: contract tests`).
