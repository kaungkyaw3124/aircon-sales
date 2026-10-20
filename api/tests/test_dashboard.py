from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import text

from app.auth import make_token
from app.clock import now
from app.dashboard import change_percent
from app.main import app
from app.models import Product, Sale, SaleItem

YGN = ZoneInfo("Asia/Yangon")
NOW = datetime(2026, 10, 20, 15, 42, 10, tzinfo=YGN)


def ygn(s: str) -> datetime:
    """'2026-10-20 10:00' (or with seconds) in Yangon time."""
    fmt = "%Y-%m-%d %H:%M:%S" if s.count(":") == 2 else "%Y-%m-%d %H:%M"
    return datetime.strptime(s, fmt).replace(tzinfo=YGN)


class Shop:
    """Hand-made dataset builder on the test transaction."""

    def __init__(self, db, client, make_user):
        self.db, self.client = db, client
        self.owner = make_user()
        self.seller = make_user(username="sales1", role="sales", full_name="Ko Aung")
        self.products = {}
        for cat in ("aircon", "accessory", "service"):
            self.products[cat] = Product(sku=f"T-{cat}", name=cat, category=cat, price=1)
            db.add(self.products[cat])
        db.flush()

    def sale(self, at, lines, method="cash", pay="paid", user=None, voided_at=None):
        """lines: [(category, quantity, unit_price)]; at / voided_at: Yangon time strings."""
        no = self.db.execute(text("SELECT nextval('invoice_no_seq')")).scalar()
        sale = Sale(invoice_no=f"INV-{no:06d}", user_id=(user or self.owner).id, sold_at=ygn(at),
                    total_amount=sum(q * p for _, q, p in lines), payment_status=pay,
                    payment_method=None if pay == "unpaid" else method,
                    status="void" if voided_at else "completed",
                    voided_at=ygn(voided_at) if voided_at else None, void_reason="test" if voided_at else None)
        self.db.add(sale)
        self.db.flush()
        for cat, q, p in lines:
            self.db.add(SaleItem(sale_id=sale.id, product_id=self.products[cat].id, quantity=q, unit_price=p,
                                 line_total=q * p))
        self.db.flush()
        return sale

    def today(self, user=None, at=NOW):
        app.dependency_overrides[now] = lambda: at.astimezone(UTC)
        token = make_token(user or self.owner, datetime.now(UTC))
        resp = self.client.get("/dashboard/today", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200, resp.text
        return resp.json()


@pytest.fixture
def shop(db, client, make_user):
    return Shop(db, client, make_user)


def categories(body):
    return [(c["category"], c["amount"], c["quantity"]) for c in body["by_category"]]


def methods(body):
    return [(m["payment_method"], m["amount"], m["invoice_count"]) for m in body["by_payment_method"]]


def test_normal_day(shop):
    shop.sale("2026-10-19 11:00", [("aircon", 1, 1_000_000)])
    shop.sale("2026-10-20 09:30", [("aircon", 1, 1_200_000), ("service", 1, 50_000)], method="bank")
    shop.sale("2026-10-20 12:00", [("accessory", 4, 25_000)])
    shop.sale("2026-10-20 14:00", [("service", 2, 60_000)], method="kbzpay")
    body = shop.today()
    assert body["date"] == "2026-10-20"
    assert body["currency"] == "MMK"
    assert body["total_amount"] == 1_470_000
    assert body["invoice_count"] == 3
    assert body["void_count"] == 0
    assert body["yesterday_total_amount"] == 1_000_000
    assert body["change_percent"] == 47.0
    assert categories(body) == [("aircon", 1_200_000, 1), ("accessory", 100_000, 4), ("service", 170_000, 3)]
    assert methods(body) == [("cash", 100_000, 1), ("bank", 1_250_000, 1), ("kbzpay", 120_000, 1)]
    assert body["unpaid_count"] == 0 and body["unpaid_amount"] == 0
    assert body["generated_at"] == "2026-10-20T15:42:10+06:30"
    assert sum(c["amount"] for c in body["by_category"]) == body["total_amount"]


def test_empty_day(shop):
    body = shop.today()
    assert body == {
        "date": "2026-10-20", "currency": "MMK", "total_amount": 0, "invoice_count": 0, "void_count": 0,
        "yesterday_total_amount": 0, "change_percent": None,
        "by_category": [{"category": c, "amount": 0, "quantity": 0} for c in ("aircon", "accessory", "service")],
        "by_payment_method": [], "unpaid_count": 0, "unpaid_amount": 0,
        "generated_at": "2026-10-20T15:42:10+06:30",
    }


def test_void_sale_excluded_from_totals_but_counted(shop):
    shop.sale("2026-10-20 10:00", [("aircon", 1, 1_500_000)])
    shop.sale("2026-10-20 11:00", [("aircon", 1, 1_800_000)], method="bank", pay="partial",
              voided_at="2026-10-20 12:00")
    body = shop.today()
    assert body["total_amount"] == 1_500_000 and body["invoice_count"] == 1
    assert body["void_count"] == 1
    assert categories(body)[0] == ("aircon", 1_500_000, 1)
    assert methods(body) == [("cash", 1_500_000, 1)]
    assert body["unpaid_count"] == 0 and body["unpaid_amount"] == 0


def test_sold_yesterday_voided_today(shop):
    shop.sale("2026-10-19 10:00", [("aircon", 1, 1_000_000)])
    shop.sale("2026-10-19 15:00", [("aircon", 1, 2_000_000)], voided_at="2026-10-20 09:15")
    body = shop.today()
    assert body["void_count"] == 1
    assert body["yesterday_total_amount"] == 1_000_000
    assert body["total_amount"] == 0 and body["invoice_count"] == 0


def test_voided_yesterday_not_in_todays_void_count(shop):
    shop.sale("2026-10-19 10:00", [("aircon", 1, 2_000_000)], voided_at="2026-10-19 18:00")
    assert shop.today()["void_count"] == 0


def test_partial_sale_under_method_and_in_unpaid(shop):
    shop.sale("2026-10-20 10:00", [("aircon", 1, 1_800_000), ("service", 1, 70_000)], method="kbzpay", pay="partial")
    shop.sale("2026-10-20 11:00", [("accessory", 2, 25_000)], pay="unpaid")
    body = shop.today()
    assert methods(body) == [("kbzpay", 1_870_000, 1)]
    assert body["unpaid_count"] == 2
    assert body["unpaid_amount"] == 1_920_000
    assert body["total_amount"] == 1_920_000


def test_sales_user_sees_only_own_sales(shop):
    shop.sale("2026-10-19 10:00", [("aircon", 1, 1_000_000)], user=shop.seller)
    shop.sale("2026-10-19 11:00", [("aircon", 1, 5_000_000)])
    shop.sale("2026-10-20 10:00", [("accessory", 2, 30_000)], user=shop.seller, method="wavepay")
    shop.sale("2026-10-20 10:30", [("service", 1, 70_000)], user=shop.seller, pay="unpaid")
    shop.sale("2026-10-20 11:00", [("aircon", 1, 1_500_000)])
    shop.sale("2026-10-20 12:00", [("aircon", 1, 1_700_000)], pay="partial")
    shop.sale("2026-10-20 08:00", [("aircon", 1, 900_000)], voided_at="2026-10-20 09:00")
    shop.sale("2026-10-20 08:00", [("service", 1, 40_000)], user=shop.seller, voided_at="2026-10-20 09:30")

    mine = shop.today(user=shop.seller)
    assert mine["total_amount"] == 130_000 and mine["invoice_count"] == 2
    assert mine["void_count"] == 1
    assert mine["yesterday_total_amount"] == 1_000_000
    assert mine["change_percent"] == -87.0
    assert categories(mine) == [("aircon", 0, 0), ("accessory", 60_000, 2), ("service", 70_000, 1)]
    assert methods(mine) == [("wavepay", 60_000, 1)]
    assert mine["unpaid_count"] == 1 and mine["unpaid_amount"] == 70_000

    everything = shop.today()
    assert everything["total_amount"] == 3_330_000 and everything["invoice_count"] == 4
    assert everything["void_count"] == 2
    assert everything["yesterday_total_amount"] == 6_000_000
    assert everything["unpaid_count"] == 2 and everything["unpaid_amount"] == 1_770_000


def test_yesterday_zero_gives_null_change(shop):
    shop.sale("2026-10-20 10:00", [("aircon", 1, 1_500_000)])
    body = shop.today()
    assert body["yesterday_total_amount"] == 0
    assert body["change_percent"] is None


def test_negative_change(shop):
    shop.sale("2026-10-19 10:00", [("aircon", 1, 800_000)])
    shop.sale("2026-10-20 10:00", [("aircon", 1, 700_000)])
    assert shop.today()["change_percent"] == -12.5


@pytest.mark.parametrize("today, yesterday, expected", [
    (3_660_000, 3_050_000, 20.0),
    (1_001, 2_000, -50.0),   # -49.95 rounds away from zero
    (2_999, 2_000, 50.0),    # 49.95
    (1_000, 3_000, -66.7),
    (0, 1_000, -100.0),
    (5, 0, None),
])
def test_change_percent_rounding(today, yesterday, expected):
    assert change_percent(today, yesterday) == expected


def test_requires_token(client):
    resp = client.get("/dashboard/today")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "unauthorized"


def test_contract_normal_day_example(shop):
    """Rebuilds the 5 invoices described in openapi.yaml's normal_day example."""
    import yaml
    from tests.conftest import API_DIR
    spec = yaml.safe_load((API_DIR.parent / "docs" / "openapi.yaml").read_text())
    example = (spec["paths"]["/dashboard/today"]["get"]["responses"]["200"]["content"]["application/json"]
               ["examples"]["normal_day"]["value"])

    shop.sale("2026-10-19 13:00", [("aircon", 2, 1_500_000)])
    shop.sale("2026-10-19 16:00", [("accessory", 1, 50_000)], method="bank")
    shop.sale("2026-10-20 09:10", [("aircon", 1, 1_500_000)])                                    # INV-000101
    shop.sale("2026-10-20 10:20", [("aircon", 1, 1_800_000), ("service", 1, 70_000)],
              method="kbzpay", pay="partial")                                                     # INV-000102
    shop.sale("2026-10-20 11:30", [("accessory", 2, 30_000), ("accessory", 1, 40_000)])           # INV-000103
    shop.sale("2026-10-20 12:40", [("accessory", 2, 25_000), ("service", 1, 70_000)], pay="unpaid")  # INV-000104
    shop.sale("2026-10-20 14:00", [("service", 1, 70_000)], method="wavepay")                     # INV-000105
    shop.sale("2026-10-20 09:50", [("aircon", 1, 1_200_000)], voided_at="2026-10-20 10:05")       # the voided one

    body = shop.today()
    for key in ("date", "generated_at"):
        body.pop(key), example.pop(key)
    assert body == example
