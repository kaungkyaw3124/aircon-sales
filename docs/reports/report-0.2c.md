# Report: Task 0.2c

## 1. Goal
0.2c: Schema follow-ups (apply D13–D15 to `docs/schema.md`). Docs only.

## 2. Status
**DONE.**

## 3. Checks

| Check | Result | Command |
|---|---|---|
| `schema.md` contains `voided_sale_serials`, `warranty_months`, and `customers (phone)` as a plain index | PASS | `grep -n "voided_sale_serials\|warranty_months\|customers (phone)" docs/schema.md`: table section (line 112), column + constraint (53, 56), index row `customers (phone)` "plain, not unique" (146) |
| No UNIQUE on `customers.phone` | PASS | `grep -n "UNIQUE" docs/schema.md`: hits only on `users.username`, `products.sku`, `sales.invoice_no`, `sale_item_serials.serial_no` and the D13 note / index intro; none on `customers.phone` |
| Report written, committed, pushed | PASS | `git push`; this file |

## 4. What changed
- `docs/schema.md` (changed): `customers.phone` no longer UNIQUE (D15); `products.warranty_months` + CHECK, added to the aircon-only constraint (D14); how the API fills `warranty_until` (D14); new table `voided_sale_serials` and the void procedure (D13); indexes section updated (removed `customers.phone` from UNIQUE list, added `customers (phone)`, `voided_sale_serials (serial_no)`, `voided_sale_serials (original_sale_item_id)`).
- `docs/reports/report-0.2c.md` (added): this report.

## 5. Decisions I made
- **Added an FK index `voided_sale_serials (original_sale_item_id)`**, not listed in the task, to follow the "every FK column has an index" convention.
- **`voided_sale_serials.voided_at` takes the same value as the sale's `voided_at`**, so both agree.
- **`warranty_until` uses the sale's Yangon date** (`date(sold_at AT TIME ZONE 'Asia/Yangon')`) + `warranty_months` months, i.e. Postgres `date + interval 'N months'` semantics (Jan 31 + 1 month = Feb 28/29).

## 6. Questions for the owner
None.

## 7. Not checked / risks
- No SQL was run; the design is first exercised by the migration in Task 0.4.
- When a voided sale's serial is later re-entered, the old `warranty_until` in `voided_sale_serials` is history only; the new row's warranty is computed from the new sale's date.

## 8. Commit
Message: `task 0.2c: schema follow-ups`. Hash: the commit that adds this file (see `git log -- docs/reports/report-0.2c.md`).
