# Report 1.4

## 1. Goal
Task 1.4 — Yangon day boundaries

## 2. Status
DONE

## 3. Checks

| Done when | Result | Command |
|---|---|---|
| Sale at 23:59:59 Yangon counts today | PASS | `test_sale_at_235959_counts_today` |
| Sale at 00:00:00 the next day doesn't | PASS | `test_sale_at_next_midnight_not_today` (and it counts on the next day) |
| Sale at 00:00:00 Yangon counts | PASS | `test_sale_at_midnight_counts_today` (23:59:59 the day before goes to yesterday) |
| Sale at 23:59 UTC that is already "tomorrow" in Yangon is not today | PASS | `test_sale_at_2359_utc_is_tomorrow_in_yangon` |
| Result doesn't depend on server timezone (`TZ=UTC`, `TZ=America/New_York`) | PASS | `test_result_does_not_depend_on_server_timezone[UTC / America/New_York / Asia/Tokyo]` sets `TZ` + `time.tzset()` **and** the Postgres session time zone; also ran `TZ=UTC pytest …` and `TZ=America/New_York pytest …` on the dashboard + boundary tests (26 passed each) |
| All tests pass | PASS | `.venv/bin/pytest` |

pytest:
```
57 passed in 15.02s
TZ=UTC              tests/test_day_boundaries.py tests/test_dashboard.py → 26 passed in 2.92s
TZ=America/New_York tests/test_day_boundaries.py tests/test_dashboard.py → 26 passed in 3.01s
```

## 4. What changed
- `api/tests/test_day_boundaries.py` (new): the boundary tests above, plus two extras: the clock at 23:59 UTC is already the next Yangon day (`date` follows Yangon), and `void_count` at the midnight edges.
- `api/tests/test_dashboard.py`: the `Shop.sale` helper also accepts an aware `datetime` (for the UTC case).
- No app code changed: 1.3's implementation already passed every edge.

## 5. Decisions I made
- Also varied the database session's time zone, since a `date(sold_at)` mistake in SQL would depend on it, not on Python's `TZ`.

## 6. Questions for the owner
None.

## 7. Not checked / risks
None known.

## 8. Commit
See `git log -- docs/reports/report-1.4.md` (`task 1.4: Yangon day boundaries`).
