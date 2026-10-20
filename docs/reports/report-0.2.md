# Report: Goal 0.2

## 1. Goal
0.2: Database design (`docs/schema.md`, docs only).

## 2. Status
**NEEDS REVIEW.** The schema is written, committed and pushed. Goal 0.3 waits for the owner's approval.

## 3. Checks

| Check | Result | Command |
|---|---|---|
| `schema.md` lists every table, column, type, key and index | PASS | Script checking each of the 28 required `table.column` names has a row in that table's section: `missing=0`. Types, PK/FK/UNIQUE and the index table were reviewed by hand. |
| Committed and pushed | PASS | `git push`; `git ls-remote origin` matches local `HEAD` |
| Owner reviews and approves | PENDING | (owner) |

## 4. What changed
- `docs/schema.md` (added): the database design for Goal 0.2.
- `docs/reports/report-0.2.md` (added): this report.
- `CLAUDE.md` (changed): added the "Reports" section under "How we work: goal loops", as the owner asked.

## 5. Decisions I made
- **`bigint` for money**, not `integer`: totals in kyat go past `integer`'s maximum of about 2.1 billion.
- **Enums as `text` + CHECK** instead of Postgres `ENUM` types, so adding a value is easy.
- **No deletes** for branches, users and products; they are deactivated (`active = false`) so old sales keep their links.
- **`branch_id` stored on each sale**, so moving a salesperson to another branch doesn't move their past sales.
- **`unit_price` copied into `sale_items`**, so changing a product's price doesn't change old invoices.
- **Database CHECK constraints:** `line_total = quantity * unit_price`; non-owner users must have a branch; only aircons have `capacity_hp` / `is_inverter`.
- **`total_amount` = sum of the lines is not a database constraint.** The API enforces it and a test checks it (Goal 0.5), because it would need a trigger.
- **`brand` and `model` are nullable**: services and some accessories have none.
- **`capacity_hp numeric(3,1)`**: it isn't money, and it allows 1.5 / 2.5.
- **No `created_at` / `updated_at` columns**, because the goal doesn't need them. Easy to add later.
- **Extra index `sales (user_id, sold_at)`** for the `sales` role (own sales only), since roles are to be designed in from the start.

## 6. Questions for the owner
1. **Installment payments:** do customers pay in installments? If yes, we need a `payments` table (sale, date, amount, method), and "partial" / "unpaid" would be calculated from it. Right now `payment_status` is only a label, with no record of how much was paid.
2. **Payment method:** should we record cash / bank transfer / KBZPay / etc.?
3. **Different prices per branch:** can the same product cost different amounts at different branches? Today there is one `products.price`, and each sale stores its own `unit_price`, so a per-branch price would only affect the default price.
4. **Aircon serial numbers for warranty:** do you need to record the serial number of each aircon sold (and the warranty end date)? That would be a `sale_item_serials` table, one row per unit.
5. **Discounts:** are discounts given per line, per invoice, or both? Should the dashboard show amounts before or after the discount?
6. **Returns / refunds:** can a sale be returned or cancelled? Options: mark the sale as `void` (kept but excluded from totals), or add separate return records. Sales should never just be deleted.
7. **Currency:** is everything in Myanmar kyat (MMK)? Kyat has no coins in practice, so the "smallest unit" would be 1 kyat. Do you ever sell in USD?
8. **Invoice numbers:** does each branch have its own sequence (e.g. `YGN1-000123`), or is there one shared sequence? This affects whether `invoice_no` is unique overall or per branch.
9. **Tax:** do invoices include commercial tax that needs to be shown separately?
10. **Customers:** should a sale record the customer (name, phone) for warranty and service follow-up?

## 7. Not checked / risks
- No SQL was run; the design isn't tested until the migration in Goal 0.4.
- The "every column/type/key/index" check is part script, part manual review; the script only checks that the column names are present.
- Answers to questions 1, 4, 5, 6 and 8 may add tables or columns. Better to decide before Goal 0.4 creates the migration.

## 8. Commit
Message: `goal 0.2: database design`. Hash: the commit that adds this file (a commit can't contain its own hash; see `git log -- docs/reports/report-0.2.md`).
