# Report: Task 0.3

## 1. Goal
0.3: API contract — `docs/openapi.yaml` (OpenAPI 3.1) for the Phase 1 endpoints.

## 2. Status
**NEEDS REVIEW.** All checks pass; the task says stop for the owner's review.

## 3. Checks

| Check | Result | Command |
|---|---|---|
| Redocly lint passes with no errors | PASS | `npx @redocly/cli lint docs/openapi.yaml` → "Your API description is valid", 0 errors, 2 warnings (see section 7) |
| In every example, `total_amount` = sum of `by_category[].amount` | PASS | `npx @redocly/cli bundle docs/openapi.yaml --ext json -o <scratch>/openapi.json`, then a Node script that walks every object with `total_amount` + `by_category`, asserts the sum and the order aircon, accessory, service: `2026-10-20 3660000 3660000 OK`, `2026-10-21 0 0 OK`, `2 examples checked` |
| Report written, committed, pushed | PASS | `git push`; this file |

## 4. What changed
- `docs/openapi.yaml` (added): `GET /health`, `POST /auth/login`, `GET /dashboard/today`; shared `Error` shape and `Unauthorized` / `ValidationError` responses; one `bearerAuth` JWT scheme (global, turned off on `/health` and `/auth/login`); a `Money` schema (`integer`, `int64`, `minimum: 0`) used by every money field.
- `docs/reports/report-0.3.md` (added): this report.

## 5. Decisions I made
- **Two dashboard examples:** a normal day (5 invoices, 1 void, one `partial`, one `unpaid`) and an empty day (all zeros, `change_percent: null`, `by_payment_method: []`). The normal-day example's description lists the 5 invoices so the numbers can be checked by hand: categories 3,300,000 + 150,000 + 210,000 = 3,660,000; payment methods 1,600,000 + 1,870,000 + 70,000 = 3,540,000 = total − the one `unpaid` invoice (120,000); `unpaid_amount` 1,870,000 + 120,000 = 1,990,000; change (3,660,000 − 3,050,000) / 3,050,000 = 20.0 %.
- **`unpaid_amount` and `by_payment_method[].amount` use the invoice's full `total_amount`.** Per D16 there is no amount-owed tracking, so a `partial` invoice counts fully in both its payment method and the unpaid totals.
- **`void_count` counts sales whose `voided_at` falls on today (Yangon)**, not sales sold today and later voided.
- **`by_payment_method` leaves out methods with no sales** (unlike `by_category`, which always has 3 items).
- **`change_percent` formula** documented as `(today − yesterday) / yesterday × 100`, rounded to 1 decimal.
- **Error codes** used in examples: `invalid_credentials`, `unauthorized`, `validation_error`. The `422` uses the shared error shape, so the API must override FastAPI's default 422 body.
- **`expires_in: 86400`** (24 h) in the example only; the real lifetime is set in Task 1.2.
- **License** set to "Proprietary" to satisfy the lint's license rule.
- **`servers`** has only `http://localhost:8000`; the real server URL is added in Phase 3.

## 6. Questions for the owner
1. **Partial invoices:** in the dashboard, a `partial` invoice counts its full amount both under its payment method and under "unpaid". Is that how you want to read it, or should partial invoices appear only under "unpaid"?
2. **Voided today:** `void_count` counts sales *voided* today (even if sold on an earlier day). OK?

## 7. Not checked / risks
- Lint warnings left as is: `no-server-example.com` (server URL is localhost until Phase 3) and `operation-4xx-response` on `/health` (it has no 4xx case).
- Examples are validated against the schemas by Redocly's recommended rules; nothing has been tested against a running API yet (Task 1.5).
- Python is not installed on this PC, so the sum check used Node on a Redocly JSON bundle.

## 8. Commit
Message: `task 0.3: API contract`. Hash: the commit that adds this file (see `git log -- docs/reports/report-0.3.md`).
