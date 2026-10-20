# Report 0.5

## 1. Goal
Task 0.5 — Fake data generator

## 2. Status
NEEDS REVIEW (all checks pass; stopped for review at the end of Phase 0, as the task requires)

## 3. Checks

| Done when | Result | Command |
|---|---|---|
| Seed runs, prints row counts | PASS | `.venv/bin/python scripts/seed.py --reset` |
| Twice → identical counts and totals | PASS | ran it twice; both printed the output below |
| `APP_ENV=production` + `--reset` exits non-zero, data untouched | PASS | `test_production_reset_refuses_and_leaves_data` |
| `total_amount` = sum of `line_total` | PASS | `test_total_amount_equals_sum_of_line_totals` |
| Aircon lines have `quantity` serials, others none | PASS | `test_aircon_lines_have_quantity_serials_others_none` (also checks `warranty_until` = Yangon sale date + `warranty_months`) |
| Void sales' serials only in `voided_sale_serials` | PASS | `test_void_sales_have_serials_only_in_voided_table` (also checks that a voided serial was re-sold, D13) |
| No sale outside 09:00–19:00 Yangon; last day = today Yangon | PASS | `test_sales_within_opening_hours_and_end_today` |
| All tests pass (incl. 0.4) | PASS | `.venv/bin/pytest` |

Seed output (identical on both runs):
```
users                       5
customers                  60
products                   41
sales                     499
sale_items               1051
sale_item_serials         181
voided_sale_serials         3
completed sales total  409,679,000 MMK
```

pytest:
```
..........                                                               [100%]
10 passed in 6.75s
```

Data shape (checked with SQL): 40.1% walk-in, 10 void sales (2%), paid 426 / partial 51 / unpaid 22.
Unpaid invoices have no method; the others use all five methods. Aircon prices 900,000–3,432,000.
19 of 60 customers have no phone, and two share `09420001111`. Serials `LG0000001` and `LG0000002` were on voided
`INV-000002` and were re-sold on `INV-000007` the next day.

## 4. What changed
- `api/scripts/seed.py` — the generator. `build()` makes the data in memory with a fixed seed. `main()` checks `APP_ENV` before importing or connecting to the DB, then inserts the data in time order. Voids use the schema.md void procedure.
- `api/tests/test_seed.py` — seeds `aircon_test` (subprocess, `DATABASE_URL` set to the test DB), then runs the checks above.
- `api/README.md` — how to run, plus the dev-only logins warning.
- `docs/reports/report-0.4.md` — filled in the commit hash.

## 5. Decisions I made
- **Today's sales cover the whole day 09:00–19:00, even hours that haven't happened yet.** Cutting at "now" would change the data on every run, and a run before 09:00 would have no sales today. So right after seeding, some of today's sales have `sold_at` later than now.
- Without `--reset`, the script refuses if `users` already has rows, so it never adds duplicates on top of existing data.
- Product lineup: 4 brands (Daikin 36-month warranty, Mitsubishi 24, Panasonic 24, LG 12) × 1/1.5/2/2.5 HP × inverter/standard = 32 aircons, 6 accessories, 3 services = 41 products. Inverter models cost +30%.
- About 3–8 sales per day (5–11 in Mar–May). The current 90-day window has no Mar–May days, so the hot-month rule exists but has no effect on today's data.
- Sales are made by `sales1`..`sales4` only. The owner has no sales.
- The voided-and-resold sale is a real "wrong entry, corrected next day" case: voided within an hour, then re-entered with the same serials the next day.
- Running the seed in pytest uses the subprocess path (the real CLI), with `DATABASE_URL` set to `aircon_test`.

## 6. Questions for the owner
- None that block. Question 1: is "today's sales already include later hours right after a seed" fine for dev data? (The alternative is to regenerate relative to the current time, but then the numbers change on every run.)

## 7. Not checked / risks
- Passwords are hashed with bcrypt. The login (Phase 1.2) must use bcrypt to check them.
- Running `pytest` re-creates the `aircon_test` schema each time (downgrade → upgrade). It never touches `aircon`; the fixture refuses any DB not named `*_test`.
- The test that "last sale day = today" could fail if pytest runs exactly over Yangon midnight between seeding and checking (seconds apart). Very unlikely.

## End of Phase 0

Today's totals from the seeded `aircon` DB, Yangon day **2026-10-21** (seeded at 01:15 Yangon), with the `schema.md` SQL
(`status = 'completed'`, `sold_at` in the Yangon-day UTC range):

| Measure | Value |
|---|---|
| Invoices | 3 |
| Total | 3,570,000 MMK |
| By method | bank 1,965,000 · wavepay 1,235,000 · cash 370,000 |
| By category | aircon 2 units 2,590,000 · accessory 7 items 750,000 · service 4 items 230,000 |
| Not fully paid (partial + unpaid, D17) | 0 |
| Voided today (by `voided_at`, D18) | 0 |

The three categories add up to the total (2,590,000 + 750,000 + 230,000 = 3,570,000), and so do the methods.
All three of today's sales are later than the seed time (see Decisions).

## 8. Commit
See `git log -- docs/reports/report-0.5.md` (`task 0.5: fake data generator`).
