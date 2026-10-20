# Report: Goal 0.2b

## 1. Goal
0.2b: Database design updated with the owner's decisions and the reviewer's fixes (docs only).

## 2. Status
**NEEDS REVIEW.** Committed and pushed. Goal 0.3 waits for the owner's approval.

## 3. Checks

| Check | Result | Command |
|---|---|---|
| `schema.md` lists every table, column, type, key and index | PASS | Script checking all 41 `table.column` names (including every new one) have a row in their table's section: `missing=0`. Types, keys and indexes were reviewed by hand. |
| No `branch` / `manager` / `CASCADE` left in the current design | PASS | `grep -n -i 'branch\|manager\|cascade' CLAUDE.md docs/schema.md docs/goals/phase-0.md`: the only hits are "no branches" notes and Goal 0.2's original request, kept and labeled as history. |
| Committed and pushed | PASS | `git push`; `git ls-remote origin main` matches local `HEAD` |
| Owner reviews and approves | PENDING | (owner) |

## 4. What changed
- `docs/schema.md` (changed): removed `branches` and every `branch_id`; roles are now `owner`/`sales`; added `customers`, `sale_item_serials`, the `sales` columns `customer_id`, `payment_method`, `status`, `voided_at`, `void_reason` and `created_at`; MMK, invoice number format, all FKs RESTRICT; updated indexes.
- `CLAUDE.md` (changed): business rules now say one store, MMK only, roles `owner`/`sales`, and void sales excluded from totals.
- `docs/goals/phase-0.md` (changed): 0.2 marked as updated, with a pointer to `schema.md`; 0.3 user object without `branch_id`; 0.4 lists the tables and the sequence; 0.5 seed data is 1 owner + 4 sales, customers, serials, payment methods, void sales.
- `docs/reports/report-0.2b.md` (added): this report.

## 5. Decisions I made
- **`payment_method` is nullable but required unless the sale is `unpaid`** (CHECK). An unpaid invoice has no payment method yet.
- **A void sale must have both `voided_at` and `void_reason`, and a completed sale must have neither** (CHECK).
- **Invoice numbers come from a Postgres sequence `invoice_no_seq`**, format `INV-` + at least 6 digits, with a CHECK on the format. After `INV-999999` it simply becomes `INV-1000000`.
- **`warranty_until` is nullable**, in case the warranty length isn't known when the sale is entered.
- **All foreign keys are `ON DELETE RESTRICT`**, not only `sale_items.sale_id`, because sales are never deleted.
- **Indexes are not partial on `status = 'completed'`**: void sales are few, so a plain index is simpler.
- **Kept Goal 0.2's original table list in `phase-0.md`**, labeled as the original request, with a note that `schema.md` is now the current design. I did this instead of rewriting history.
- **Removed the `sales (branch_id, sold_at)` index; added `sales (customer_id)` and `sale_item_serials (sale_item_id)`.**

## 6. Questions for the owner
1. **Serial number of a voided sale:** `serial_no` is UNIQUE across all rows, so if a sale is voided (e.g. a typo) and entered again, the same serial cannot be used. Options: (a) when voiding, the API deletes that sale's serial rows; (b) keep them and make the UNIQUE apply only to completed sales (needs a `status` copy on the serial row or a trigger); (c) allow editing instead of void + re-enter. Which do you prefer?
2. **Warranty length:** is it fixed per brand, per product, or written by hand on each sale? If it's per product, `products` could hold `warranty_months` and the API would fill `warranty_until`.
3. **Customer phone:** can two customers share a phone number (e.g. a family, or a company with one number)? `phone` is UNIQUE now, as you asked.
4. **Partial payments:** without a payments table, the app cannot show how much is still owed on `partial` invoices. Is "partial" as a label enough?

## 7. Not checked / risks
- No SQL was run; the design is first tested by the migration in Goal 0.4.
- The column check only confirms that the names are present; types and constraints were reviewed by hand.
- The openapi file doesn't exist yet (Goal 0.3), so there was nothing to update there.

## 8. Commit
Message: `goal 0.2b: schema update with owner decisions`. Hash: the commit that adds this file (see `git log -- docs/reports/report-0.2b.md`).
