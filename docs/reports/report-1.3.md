# Report 1.3

## 1. Goal
Task 1.3 — `GET /dashboard/today`

## 2. Status
DONE

## 3. Checks

All tests in `api/tests/test_dashboard.py` use small hand-made datasets (not the seed), with the clock fixed at
2026-10-20 15:42:10 Yangon.

| Done when | Result | Command |
|---|---|---|
| Normal day, exact numbers | PASS | `test_normal_day` |
| Empty day (all zeros, `change_percent` null, `by_payment_method` empty) | PASS | `test_empty_day` (compares the whole body) |
| Void sale excluded from totals, counted in `void_count` | PASS | `test_void_sale_excluded_from_totals_but_counted` |
| Sold yesterday, voided today → today's `void_count`, not yesterday's total | PASS | `test_sold_yesterday_voided_today` (+ `test_voided_yesterday_not_in_todays_void_count`) |
| `partial` sale under its method **and** in unpaid | PASS | `test_partial_sale_under_method_and_in_unpaid` |
| `sales` user sees only own sales | PASS | `test_sales_user_sees_only_own_sales` (every field, incl. void and yesterday; owner sees all) |
| Yesterday = 0 → `change_percent` null | PASS | `test_yesterday_zero_gives_null_change` |
| Negative change (-12.5) | PASS | `test_negative_change` (+ `test_change_percent_rounding`: half away from zero, e.g. -49.95 → -50.0) |
| Contract `normal_day` example rebuilt, response equals example (except `generated_at`, `date`) | PASS | `test_contract_normal_day_example` (reads the example straight from `docs/openapi.yaml`) |
| All tests pass | PASS | `.venv/bin/pytest` |

pytest:
```
48 passed in 14.53s
```

## 4. What changed
- `api/app/dashboard.py` (new): the endpoint. Three aggregate SQL queries (totals with `FILTER`, by category, by payment method), filtered on the Yangon day converted to a UTC range so the `sold_at` index is used.
- `api/app/main.py`: includes the dashboard router.
- `api/requirements.txt`: `PyYAML==6.0.3` (the contract test reads `openapi.yaml`).
- `api/tests/test_dashboard.py` (new).

## 5. Decisions I made
- The role filter uses the role stored in the DB (not the token claim), so a role change takes effect at once.
- `by_category` amounts come from `sale_items.line_total` (per category); totals come from `sales.total_amount`. They are equal because the seed and schema keep `total_amount` = sum of lines (no DB constraint enforces it).
- `by_payment_method` is ordered like the contract's enum: cash, bank, kbzpay, wavepay, other.
- The contract's normal_day example doesn't give yesterday's invoices or the voided invoice's details; I made up ones that give 3,050,000 and 1 void.
- INV-000103 "3 accessories 100,000": built as 2 × 30,000 + 1 × 40,000 (quantity 3, amount 100,000).

## 6. Questions for the owner
None.

## 7. Not checked / risks
- Performance on large data not measured (indexes on `sold_at` and `(user_id, sold_at)` exist; `voided_at` has no index, but the OR filter is small for one store).

## 8. Commit
See `git log -- docs/reports/report-1.3.md` (`task 1.3: dashboard today endpoint`).
