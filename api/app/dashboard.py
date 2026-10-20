from datetime import date, datetime, time, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.clock import now
from app.config import settings
from app.db import get_db
from app.models import User

router = APIRouter()

TZ = ZoneInfo(settings.business_tz)
CATEGORIES = ["aircon", "accessory", "service"]
METHODS = ["cash", "bank", "kbzpay", "wavepay", "other"]

# :t0/:t1 = today's Yangon day as a UTC range, :y0 = start of yesterday; :uid = NULL for owner (all sales)
OWN = "(CAST(:uid AS bigint) IS NULL OR s.user_id = :uid)"
TODAY = "s.status = 'completed' AND s.sold_at >= :t0 AND s.sold_at < :t1"

TOTALS_SQL = text(f"""
SELECT
  coalesce(sum(s.total_amount) FILTER (WHERE {TODAY}), 0)::bigint AS total_amount,
  count(*) FILTER (WHERE {TODAY}) AS invoice_count,
  count(*) FILTER (WHERE s.status = 'void' AND s.voided_at >= :t0 AND s.voided_at < :t1) AS void_count,
  coalesce(sum(s.total_amount) FILTER (
    WHERE s.status = 'completed' AND s.sold_at >= :y0 AND s.sold_at < :t0), 0)::bigint AS yesterday_total_amount,
  count(*) FILTER (WHERE {TODAY} AND s.payment_status IN ('unpaid', 'partial')) AS unpaid_count,
  coalesce(sum(s.total_amount) FILTER (
    WHERE {TODAY} AND s.payment_status IN ('unpaid', 'partial')), 0)::bigint AS unpaid_amount
FROM sales s
WHERE {OWN} AND ((s.sold_at >= :y0 AND s.sold_at < :t1) OR (s.voided_at >= :t0 AND s.voided_at < :t1))
""")

CATEGORY_SQL = text(f"""
SELECT p.category, sum(i.line_total)::bigint AS amount, sum(i.quantity)::bigint AS quantity
FROM sales s JOIN sale_items i ON i.sale_id = s.id JOIN products p ON p.id = i.product_id
WHERE {OWN} AND {TODAY}
GROUP BY p.category
""")

METHOD_SQL = text(f"""
SELECT s.payment_method, sum(s.total_amount)::bigint AS amount, count(*) AS invoice_count
FROM sales s
WHERE {OWN} AND {TODAY} AND s.payment_status IN ('paid', 'partial')
GROUP BY s.payment_method
""")


def day_start(day: date) -> datetime:
    """Midnight in Yangon; Postgres compares it as an absolute instant."""
    return datetime.combine(day, time(), TZ)


def change_percent(today: int, yesterday: int) -> float | None:
    if yesterday == 0:
        return None
    # ROUND_HALF_UP on Decimal rounds half away from zero
    return float((Decimal(today - yesterday) * 100 / yesterday).quantize(Decimal("0.1"), ROUND_HALF_UP))


@router.get("/dashboard/today")
def dashboard_today(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    at: Annotated[datetime, Depends(now)],
):
    local_now = at.astimezone(TZ)
    today = local_now.date()
    params = {"uid": None if user.role == "owner" else user.id,
              "y0": day_start(today - timedelta(days=1)), "t0": day_start(today), "t1": day_start(today + timedelta(days=1))}
    totals = db.execute(TOTALS_SQL, params).mappings().one()
    categories = {r.category: r for r in db.execute(CATEGORY_SQL, params)}
    methods = {r.payment_method: r for r in db.execute(METHOD_SQL, params)}
    return {
        "date": today.isoformat(),
        "currency": "MMK",
        "total_amount": totals["total_amount"],
        "invoice_count": totals["invoice_count"],
        "void_count": totals["void_count"],
        "yesterday_total_amount": totals["yesterday_total_amount"],
        "change_percent": change_percent(totals["total_amount"], totals["yesterday_total_amount"]),
        "by_category": [
            {"category": c, "amount": categories[c].amount if c in categories else 0,
             "quantity": categories[c].quantity if c in categories else 0}
            for c in CATEGORIES
        ],
        "by_payment_method": [
            {"payment_method": m, "amount": methods[m].amount, "invoice_count": methods[m].invoice_count}
            for m in METHODS if m in methods
        ],
        "unpaid_count": totals["unpaid_count"],
        "unpaid_amount": totals["unpaid_amount"],
        "generated_at": local_now.isoformat(timespec="seconds"),
    }
