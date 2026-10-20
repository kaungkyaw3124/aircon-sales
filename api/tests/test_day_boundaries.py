import time
from datetime import UTC, datetime

import pytest
from sqlalchemy import text

from tests.test_dashboard import Shop, ygn


@pytest.fixture
def shop(db, client, make_user):
    return Shop(db, client, make_user)


def test_sale_at_235959_counts_today(shop):
    shop.sale("2026-10-20 23:59:59", [("aircon", 1, 1_000)])
    body = shop.today(at=ygn("2026-10-20 23:59:59"))
    assert body["date"] == "2026-10-20" and body["total_amount"] == 1_000


def test_sale_at_next_midnight_not_today(shop):
    shop.sale("2026-10-21 00:00:00", [("aircon", 1, 1_000)])
    body = shop.today(at=ygn("2026-10-20 23:59:59"))
    assert body["total_amount"] == 0
    # ...and it is the first sale of the next day, where 10-20 is now "yesterday"
    shop.sale("2026-10-20 12:00", [("aircon", 1, 500)])
    body = shop.today(at=ygn("2026-10-21 00:00:00"))
    assert body["date"] == "2026-10-21" and body["total_amount"] == 1_000 and body["yesterday_total_amount"] == 500


def test_sale_at_midnight_counts_today(shop):
    shop.sale("2026-10-20 00:00:00", [("aircon", 1, 1_000)])
    shop.sale("2026-10-19 23:59:59", [("aircon", 1, 7)])
    body = shop.today(at=ygn("2026-10-20 15:00"))
    assert body["total_amount"] == 1_000 and body["yesterday_total_amount"] == 7


def test_sale_at_2359_utc_is_tomorrow_in_yangon(shop):
    # 2026-10-20 23:59 UTC = 2026-10-21 06:29 Yangon
    shop.sale(datetime(2026, 10, 20, 23, 59, tzinfo=UTC), [("aircon", 1, 1_000)])
    assert shop.today(at=ygn("2026-10-20 15:00"))["total_amount"] == 0
    assert shop.today(at=ygn("2026-10-21 08:00"))["total_amount"] == 1_000


def test_today_is_the_yangon_date_not_the_utc_date(shop):
    # clock at 2026-10-19 23:59 UTC = 2026-10-20 06:29 Yangon
    shop.sale("2026-10-20 06:00", [("aircon", 1, 1_000)])
    body = shop.today(at=datetime(2026, 10, 19, 23, 59, tzinfo=UTC))
    assert body["date"] == "2026-10-20" and body["total_amount"] == 1_000


def test_void_at_midnight_boundaries(shop):
    shop.sale("2026-10-19 10:00", [("aircon", 1, 1_000)], voided_at="2026-10-19 23:59:59")
    shop.sale("2026-10-19 10:00", [("aircon", 1, 1_000)], voided_at="2026-10-20 00:00:00")
    shop.sale("2026-10-19 10:00", [("aircon", 1, 1_000)], voided_at="2026-10-21 00:00:00")
    assert shop.today(at=ygn("2026-10-20 23:59:59"))["void_count"] == 1


@pytest.mark.parametrize("tz", ["UTC", "America/New_York", "Asia/Tokyo"])
def test_result_does_not_depend_on_server_timezone(shop, db, monkeypatch, tz):
    monkeypatch.setenv("TZ", tz)
    time.tzset()
    db.execute(text(f"SET LOCAL TIME ZONE '{tz}'"))  # database session timezone too
    try:
        shop.sale("2026-10-19 23:59:59", [("aircon", 1, 1)])
        shop.sale("2026-10-20 00:00:00", [("aircon", 1, 10)])
        shop.sale("2026-10-20 23:59:59", [("aircon", 1, 100)])
        shop.sale("2026-10-21 00:00:00", [("aircon", 1, 1_000)])
        body = shop.today(at=ygn("2026-10-20 23:59:59"))
        assert (body["date"], body["total_amount"], body["yesterday_total_amount"]) == ("2026-10-20", 110, 1)
        assert body["generated_at"] == "2026-10-20T23:59:59+06:30"
    finally:
        monkeypatch.undo()
        time.tzset()
