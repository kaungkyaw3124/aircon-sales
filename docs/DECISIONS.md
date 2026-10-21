# Owner decisions

Business decisions made by the owner. Newest at the bottom. These win over anything older in other docs.
Written by the planner. Claude Code reads this but does not edit it.

## 2026-10-20 — Database design review (Goal 0.2)

| # | Topic | Decision |
|---|---|---|
| D1 | Stores | **One store only.** No branches. |
| D2 | Roles | `owner` (sees everything) and `sales` (sees only own sales). No manager role. |
| D3 | Installments | No installments. No payments table. `payment_status` is a label only. |
| D4 | Payment method | Recorded per sale: cash / bank / kbzpay / wavepay / other. |
| D5 | Prices | One price per product. |
| D6 | Serial numbers | Yes, one serial per aircon unit sold, for warranty. |
| D7 | Discounts | None. |
| D8 | Returns | Sales are voided (status `void`), never deleted. Void sales are excluded from every total. |
| D9 | Currency | MMK only. Smallest unit 1 kyat. |
| D10 | Invoice numbers | One sequence: `INV-000123`. |
| D11 | Tax | None shown separately. |
| D12 | Customers | Recorded (name, phone, address). Optional on a sale (walk-in buyers). |

## 2026-10-21 — Follow-up questions from report 0.2b

Planner defaults, accepted unless the owner changes them:

| # | Topic | Decision |
|---|---|---|
| D13 | Serial of a voided sale | When a sale is voided, its serial rows are **moved** to `voided_sale_serials` (kept for history), so the same serial can be entered again on the corrected sale. `sale_item_serials.serial_no` stays UNIQUE. |
| D14 | Warranty length | Per product: `products.warranty_months` (nullable; aircons only). The API fills `warranty_until` = sale date (Yangon) + warranty_months. |
| D15 | Customer phone | **Not unique** (families and companies share numbers). Plain index on `phone` for search. |
| D16 | Partial payments | The `partial` label is enough. No amount-owed tracking. |

## 2026-10-21 — API contract review (Task 0.3)

Planner defaults, accepted unless the owner changes them:

| # | Topic | Decision |
|---|---|---|
| D17 | Partial invoices on the dashboard | Counted in **both** places: under their payment method (money method used) and in `unpaid_count` / `unpaid_amount`, which the app labels **"Not fully paid"**. |
| D18 | `void_count` | Counts sales **voided** today (by `voided_at`, Yangon day), even if sold earlier. |
| D19 | API contract | `docs/openapi.yaml` v0.1.0 (commit 15077b6) is **approved**. Changes need the owner's OK. |

## 2026-10-21 — End of Phase 0 review (Tasks 0.4, 0.5)

| # | Topic | Decision |
|---|---|---|
| D20 | Seed data for "today" | OK that seeded sales cover all of today 09:00–19:00, even hours not reached yet. Dev data only. |
| D21 | VPS ports | Our Postgres `127.0.0.1:5433`, API `127.0.0.1:8000`. Port 5432 and 8080 belong to other projects: never touch them. |
| D22 | Python | 3.14 on the VPS and in the API image (spec said 3.12+). |
| D23 | Role filter | Implement the `sales` role filter on `/dashboard/today` now in Phase 1 (cheap now, as the contract describes). |

## 2026-10-21 — End of Phase 1 review (Tasks 1.1–1.5)

| # | Topic | Decision |
|---|---|---|
| D24 | Phase 1 | Approved. 61 tests, Schemathesis clean, live container answers login + dashboard per the contract. |
| D25 | Login rate limiting | Needed before the API is exposed. Will add `429 rate_limited` to `/auth/login` in the contract (v0.1.1), **after** the Windows PC finishes Phase 2, so its contract tests don't break mid-run. |

## 2026-10-21 — Owner testing the app (Task 2.6)

| # | Topic | Decision |
|---|---|---|
| D26 | Debug API address | Debug build uses `http://127.0.0.1:8000/` + `adb reverse tcp:8000 tcp:8000` instead of `10.0.2.2` (the emulator route failed on the owner's PC). Works for the emulator and a USB phone. PC → VPS via `ssh -p 10066 -N -L 127.0.0.1:8000:127.0.0.1:8000 administrator@93.127.132.69`. Changed directly by the planner (commit message says so); Windows: verify `.\gradlew test` on the next run. |
| D27 | Phase 2 | Approved: owner ran the app on a Xiaomi phone over USB against the VPS API. |
| D28 | App colours | Fixed brand colours, no wallpaper colours. Primary `#0057B8`, secondary `#00A3E0`. Owner can change them later. |
| D29 | Android backup | `allowBackup="false"`; the saved login token is never copied into backups. |

## 2026-10-21 — Review of 2.6–2.8 and 3.1–3.2

| # | Topic | Decision |
|---|---|---|
| D30 | Login rate limit | 5 failed logins per username or 20 per IP in 15 minutes → `429 rate_limited` with `Retry-After`. Counters in Postgres. Contract becomes v0.1.1. |
| D31 | Backup retention | 14 daily + first dump of each month for 12 months. Off-site copy: **waiting for owner** (where?). |
| D32 | App backgrounds | Neutral: white / `#F2F4F7` cards (light), `#121212` / `#1E1E1E` (dark). Brand blue stays for buttons and accents. |
| D33 | Token lifetime | Keep 24 h for now; logout only clears the phone. Revisit if staff phones get lost. |
