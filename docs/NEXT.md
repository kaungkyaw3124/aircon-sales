# Next tasks

Status: READY
Written by the planner on 2026-10-21. Run with `/next`. Do tasks in order.

---

## Task 0.2c — Schema follow-ups

- **Machine:** either (docs only)
- **Stop for review:** no (continue to 0.3 when done)

Apply decisions D13–D15 from `docs/DECISIONS.md` to `docs/schema.md`:

- **D13:** add table `voided_sale_serials` (id, original_sale_item_id FK RESTRICT, serial_no text NOT NULL,
  warranty_until date null, voided_at timestamptz NOT NULL). No UNIQUE on serial_no here (a serial may be
  voided more than once). Document the void procedure: in one transaction, copy the sale's serial rows into
  `voided_sale_serials`, delete them from `sale_item_serials`, then set the sale to `void`.
  Add index on `voided_sale_serials (serial_no)` for warranty lookups.
- **D14:** add `products.warranty_months integer null`, CHECK `warranty_months > 0`, and include it in the
  existing "only aircons" product constraint. Document how the API fills `warranty_until`.
- **D15:** remove UNIQUE from `customers.phone`; add a plain index `customers (phone)`.
- Update the indexes section to match.

### Done when
- `schema.md` contains `voided_sale_serials`, `warranty_months`, and `customers (phone)` as a plain index.
- `grep -n "UNIQUE" docs/schema.md` shows no UNIQUE on `customers.phone`.
- Report written, committed, pushed.

---

## Task 0.3 — API contract

- **Machine:** Windows PC (needs `npx` for the lint check)
- **Stop for review:** **yes**

Write `docs/openapi.yaml` (OpenAPI 3.1) for the Phase 1 endpoints only.
This task is the one allowed exception to "never change openapi.yaml without asking": the file is created here.

### Endpoints
- `GET /health` — no auth. `200 { "status": "ok" }`.
- `POST /auth/login` — body `{ username, password }`.
  `200 { access_token, token_type: "bearer", expires_in, user: { id, username, full_name, role } }`.
  `401` wrong credentials or inactive user. `422` missing fields.
- `GET /dashboard/today` — bearer auth. `401` without a valid token. `200`:
  - `date` — YYYY-MM-DD, business day in Asia/Yangon
  - `currency` — always `"MMK"`
  - `total_amount` — integer kyat, completed sales only (void excluded)
  - `invoice_count` — completed sales only
  - `void_count` — number of sales voided today (so the owner sees them)
  - `yesterday_total_amount` — integer
  - `change_percent` — number with 1 decimal, `null` when yesterday was 0
  - `by_category` — always exactly 3 items, in order aircon, accessory, service:
    `{ category, amount, quantity }` (zeros when nothing sold)
  - `by_payment_method` — list of `{ payment_method, amount, invoice_count }` for completed paid/partial sales
  - `unpaid_count`, `unpaid_amount` — completed sales today with status `unpaid` or `partial`
  - `generated_at` — timestamp with offset
  - For `sales` role users the same shape is returned, filtered to their own sales (document this; enforced in Phase 5).

### Rules
- snake_case field names. All money fields are `integer` (`format: int64`), never `number`.
- Every response has an example. Examples must be consistent (totals add up).
- Shared error shape for all 4xx/5xx: `{ "error": { "code": "string", "message": "string" } }`.
- One `securitySchemes` entry: bearer JWT.

### Done when
- `npx @redocly/cli lint docs/openapi.yaml` passes with no errors.
- In every example, `total_amount` equals the sum of `by_category[].amount`.
- Report written, committed, pushed.
- **Stop for the owner's review.**
