# Database schema

PostgreSQL 16. Design only; the SQLAlchemy models and Alembic migration (Goal 0.4) must match this file.
One store only: there are no branches.

## Conventions

- **Primary keys:** `id bigint GENERATED ALWAYS AS IDENTITY`.
- **Money:** `bigint`, in Myanmar kyat (MMK only; the smallest unit is 1 kyat), never `float`/`numeric`.
  `bigint` because kyat totals overflow `integer` (max ~2.1 billion) quickly: one aircon is ~1,500,000.
- **Enums:** `text` + `CHECK (... IN (...))`, not Postgres `ENUM` types, so adding a value is a one-line migration.
- **Timestamps:** `timestamptz`, always stored and compared in UTC.
- **Deletes:** nothing that a sale points to is ever deleted, and sales are never deleted (they are voided).
  Users and products are deactivated with `active = false`. Every foreign key is `ON DELETE RESTRICT`.
- Every foreign key column has an index (Postgres does not create one automatically).

## Tables

### `users`

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | `bigint` identity | no | PK |
| `username` | `text` | no | UNIQUE |
| `password_hash` | `text` | no | bcrypt/argon2 hash, never the password |
| `full_name` | `text` | no | |
| `role` | `text` | no | CHECK `role IN ('owner','sales')`. `owner` sees everything; `sales` sees only their own sales |
| `active` | `boolean` | no | default `true`; inactive users cannot log in |

### `customers`

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | `bigint` identity | no | PK |
| `name` | `text` | no | |
| `phone` | `text` | yes | UNIQUE (Postgres allows many NULLs) |
| `address` | `text` | yes | |
| `created_at` | `timestamptz` | no | default `now()` |

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
| `price` | `bigint` | no | the one list price; CHECK `price >= 0` |
| `active` | `boolean` | no | default `true` |

Constraint: `CHECK (category = 'aircon' OR (capacity_hp IS NULL AND is_inverter IS NULL))`.

### `sales`

One row per invoice.

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | `bigint` identity | no | PK |
| `invoice_no` | `text` | no | UNIQUE; `INV-` + 6-digit zero-padded number from sequence `invoice_no_seq`, e.g. `INV-000123`; CHECK `invoice_no ~ '^INV-[0-9]{6,}$'` |
| `customer_id` | `bigint` | yes | FK → `customers.id`; null for walk-in buyers |
| `user_id` | `bigint` | no | FK → `users.id` (the salesperson) |
| `sold_at` | `timestamptz` | no | UTC |
| `total_amount` | `bigint` | no | CHECK `total_amount >= 0`; must equal the sum of its `sale_items.line_total` (enforced by the API, checked by a test in Goal 0.5) |
| `payment_status` | `text` | no | CHECK `payment_status IN ('paid','partial','unpaid')` |
| `payment_method` | `text` | yes | CHECK `payment_method IN ('cash','bank','kbzpay','wavepay','other')`; required unless `unpaid` (see constraint) |
| `status` | `text` | no | CHECK `status IN ('completed','void')`, default `'completed'` |
| `voided_at` | `timestamptz` | yes | set when voided |
| `void_reason` | `text` | yes | set when voided |
| `note` | `text` | yes | |
| `created_at` | `timestamptz` | no | default `now()`; when the row was entered (may differ from `sold_at`) |

Constraints:
- `CHECK (payment_status = 'unpaid' OR payment_method IS NOT NULL)`
- `CHECK ((status = 'completed' AND voided_at IS NULL AND void_reason IS NULL) OR (status = 'void' AND voided_at IS NOT NULL AND void_reason IS NOT NULL))`

**Void sales are excluded from every total.** Every report query filters `status = 'completed'`.

### `sale_items`

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | `bigint` identity | no | PK |
| `sale_id` | `bigint` | no | FK → `sales.id` ON DELETE RESTRICT |
| `product_id` | `bigint` | no | FK → `products.id` ON DELETE RESTRICT |
| `quantity` | `integer` | no | CHECK `quantity > 0` |
| `unit_price` | `bigint` | no | price at time of sale (copied, so later price changes don't rewrite history); CHECK `unit_price >= 0` |
| `line_total` | `bigint` | no | CHECK `line_total = quantity * unit_price` |

### `sale_item_serials`

Serial numbers of aircon units sold, for warranty.

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | `bigint` identity | no | PK |
| `sale_item_id` | `bigint` | no | FK → `sale_items.id` ON DELETE RESTRICT |
| `serial_no` | `text` | no | UNIQUE |
| `warranty_until` | `date` | yes | last day of warranty (a calendar date, no time zone) |

Enforced by the API, not the database:
- serials are only allowed on `sale_items` whose product has `category = 'aircon'`;
- the number of serials for a line equals its `quantity`.

## Indexes

Besides the primary keys and the UNIQUE constraints above (`users.username`, `customers.phone`,
`products.sku`, `sales.invoice_no`, `sale_item_serials.serial_no`):

| Index | Used by |
|---|---|
| `sales (sold_at)` | sales by day / today / this week (owner) |
| `sales (user_id, sold_at)` | every `sales`-role query (own sales, date range); FK index |
| `sales (customer_id)` | a customer's purchase history; FK index |
| `sale_items (sale_id)` | joining items to their sale; FK index |
| `sale_items (product_id)` | top products; FK index |
| `sale_item_serials (sale_item_id)` | serials of a line; FK index |

Void sales are few, so the indexes are not partial; the `status = 'completed'` filter is applied on the rows found.

## Time zone: "today" in Asia/Yangon

`sold_at` is stored in UTC. Business days are calculated in `Asia/Yangon` (UTC+06:30, no daylight saving).

The API converts the Yangon day to a UTC range and filters on `sold_at` directly, so the index on
`sold_at` is used:

```sql
-- total for Yangon date D
SELECT sum(total_amount) FROM sales
WHERE status = 'completed'
  AND sold_at >= (D::timestamp AT TIME ZONE 'Asia/Yangon')
  AND sold_at <  ((D + 1)::timestamp AT TIME ZONE 'Asia/Yangon')
```

Example: Yangon day 2026-10-20 is UTC `2026-10-19 17:30` up to `2026-10-20 17:30`.

Grouping by day uses `date(sold_at AT TIME ZONE 'Asia/Yangon')`. Never use `date(sold_at)`, which gives the UTC date.

## Future (Phase 4–5, not built yet)

- **Stock levels:** `stock (product_id PK, quantity)` plus a `stock_movements` log (sale, purchase,
  adjustment, void) so stock can be audited. Services have no stock.
- **Daily summary:** `daily_sales_summary (business_date, category, amount, quantity, invoice_count)`
  with PK `(business_date, category)`, filled by a job for fast dashboards over long ranges.
  Only needed if live queries on `sales` get slow.
