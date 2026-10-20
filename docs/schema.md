# Database schema

PostgreSQL 16. Design only; the SQLAlchemy models and Alembic migration (Goal 0.4) must match this file.

## Conventions

- **Primary keys:** `id bigint GENERATED ALWAYS AS IDENTITY`.
- **Money:** `bigint`, in the smallest currency unit, never `float`/`numeric`. `bigint` because kyat
  totals overflow `integer` (max ~2.1 billion) quickly: one aircon is ~1,500,000 and yearly totals
  are far larger. Currency is not stored per row; see "Questions for the owner" in `reports/report-0.2.md`.
- **Enums:** `text` + `CHECK (... IN (...))`, not Postgres `ENUM` types, so adding a value is a one-line migration.
- **Timestamps:** `timestamptz`, always stored and compared in UTC.
- **Deletes:** rows that sales point to (branches, users, products) are never deleted; set `active = false`.
- Every foreign key column has an index (Postgres does not create one automatically).

## Tables

### `branches`

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | `bigint` identity | no | PK |
| `name` | `text` | no | UNIQUE |
| `address` | `text` | yes | |
| `active` | `boolean` | no | default `true` |

### `users`

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | `bigint` identity | no | PK |
| `username` | `text` | no | UNIQUE |
| `password_hash` | `text` | no | bcrypt/argon2 hash, never the password |
| `full_name` | `text` | no | |
| `role` | `text` | no | CHECK `role IN ('owner','manager','sales')` |
| `branch_id` | `bigint` | yes | FK → `branches.id` |
| `active` | `boolean` | no | default `true`; inactive users cannot log in |

Constraint: `CHECK (role = 'owner' OR branch_id IS NOT NULL)`: managers and sales staff must belong to a branch.

### `products`

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | `bigint` identity | no | PK |
| `sku` | `text` | no | UNIQUE |
| `name` | `text` | no | |
| `category` | `text` | no | CHECK `category IN ('aircon','accessory','service')` |
| `brand` | `text` | yes | null for services and unbranded accessories |
| `model` | `text` | yes | |
| `capacity_hp` | `numeric(3,1)` | yes | e.g. `1.5`; not money, so `numeric` is fine |
| `is_inverter` | `boolean` | yes | |
| `price` | `bigint` | no | current list price; CHECK `price >= 0` |
| `active` | `boolean` | no | default `true` |

Constraint: `CHECK (category = 'aircon' OR (capacity_hp IS NULL AND is_inverter IS NULL))`.

### `sales`

One row per invoice.

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | `bigint` identity | no | PK |
| `invoice_no` | `text` | no | UNIQUE |
| `branch_id` | `bigint` | no | FK → `branches.id` |
| `user_id` | `bigint` | no | FK → `users.id` (the salesperson) |
| `sold_at` | `timestamptz` | no | UTC |
| `total_amount` | `bigint` | no | CHECK `total_amount >= 0`; must equal the sum of its `sale_items.line_total` (enforced by the API, checked by a test in Goal 0.5) |
| `payment_status` | `text` | no | CHECK `payment_status IN ('paid','partial','unpaid')` |
| `note` | `text` | yes | |

`branch_id` is stored on the sale (not looked up through the user) so moving a salesperson to another
branch does not move their past sales.

### `sale_items`

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | `bigint` identity | no | PK |
| `sale_id` | `bigint` | no | FK → `sales.id` ON DELETE CASCADE |
| `product_id` | `bigint` | no | FK → `products.id` ON DELETE RESTRICT |
| `quantity` | `integer` | no | CHECK `quantity > 0` |
| `unit_price` | `bigint` | no | price at time of sale (copied, so later price changes don't rewrite history); CHECK `unit_price >= 0` |
| `line_total` | `bigint` | no | CHECK `line_total = quantity * unit_price` |

## Indexes

Besides the primary keys and the UNIQUE constraints above (`branches.name`, `users.username`,
`products.sku`, `sales.invoice_no`):

| Index | Used by |
|---|---|
| `sales (sold_at)` | sales by day / today / this week (owner, all branches) |
| `sales (branch_id, sold_at)` | sales by branch, and every manager query (own branch, date range) |
| `sales (user_id, sold_at)` | every `sales`-role query (own sales, date range) |
| `sale_items (sale_id)` | joining items to their sale; FK index |
| `sale_items (product_id)` | top products; FK index |
| `users (branch_id)` | FK index |

## Time zone: "today" in Asia/Yangon

`sold_at` is stored in UTC. Business days are calculated in `Asia/Yangon` (UTC+06:30, no daylight saving).

The API converts the Yangon day to a UTC range and filters on `sold_at` directly, so the index on
`sold_at` is used:

```sql
-- "today" for Yangon date D
WHERE sold_at >= (D::timestamp AT TIME ZONE 'Asia/Yangon')
  AND sold_at <  ((D + 1)::timestamp AT TIME ZONE 'Asia/Yangon')
```

Example: Yangon day 2026-10-20 is UTC `2026-10-19 17:30` up to `2026-10-20 17:30`.

Grouping by day uses `date(sold_at AT TIME ZONE 'Asia/Yangon')`. Never use `date(sold_at)`, which gives the UTC date.

## Future (Phase 4–5, not built yet)

- **Stock levels:** `stock (branch_id, product_id, quantity)` with PK `(branch_id, product_id)`, plus a
  `stock_movements` log (sale, purchase, transfer, adjustment) so stock can be audited. Services have no stock.
- **Daily summary:** `daily_sales_summary (business_date, branch_id, category, amount, quantity, invoice_count)`
  with PK `(business_date, branch_id, category)`, filled by a job for fast dashboards over long ranges.
  Only needed if live queries on `sales` get slow.
