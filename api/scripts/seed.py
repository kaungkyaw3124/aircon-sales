"""Fake data generator (dev only). Usage: python scripts/seed.py [--reset]

Fills users, products, customers and 90 days of sales ending today (Asia/Yangon).
Same random seed every run, so the same data for the same "today".
"""
import argparse
import calendar
import random
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings  # noqa: E402

TABLES = ["voided_sale_serials", "sale_item_serials", "sale_items", "sales", "products", "customers", "users"]
YANGON = ZoneInfo("Asia/Yangon")
DAYS = 90

BRANDS = {"Daikin": (1.10, 36), "Mitsubishi": (1.08, 24), "Panasonic": (1.00, 24), "LG": (1.00, 12)}
HP_PRICE = {1.0: 900_000, 1.5: 1_300_000, 2.0: 1_800_000, 2.5: 2_400_000}
ACCESSORIES = {
    "ACC-BRACKET": ("Wall bracket", 45_000),
    "ACC-PIPE": ("Copper pipe set (3 m)", 60_000),
    "ACC-REMOTE": ("Universal remote", 25_000),
    "ACC-STABILIZER": ("Voltage stabilizer", 150_000),
    "ACC-DRAIN": ("Drain pipe", 8_000),
    "ACC-GAS": ("Gas refill R32", 80_000),
}
SERVICES = {"SVC-INSTALL": ("Installation", 80_000), "SVC-CLEAN": ("Cleaning", 35_000), "SVC-REPAIR": ("Repair", 50_000)}
NAMES = ["Aung", "Kyaw", "Zaw", "Htun", "Min", "Thura", "Hla", "Mya", "Su", "Thida", "Khin", "Nilar", "Ei", "Phyo",
         "Wai", "Yadanar", "Soe", "Naing", "Myint", "Win"]
TOWNSHIPS = ["Kamayut", "Sanchaung", "Bahan", "Hlaing", "Insein", "Mayangone", "Tamwe", "Yankin", "Thingangyun"]
METHODS = (["cash", "kbzpay", "bank", "wavepay", "other"], [40, 25, 15, 15, 5])


def add_months(d: date, months: int) -> date:
    y, m = divmod(d.month - 1 + months, 12)
    y, m = d.year + y, m + 1
    return date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def yangon_dt(day: date, rng: random.Random) -> datetime:
    """Random moment between 09:00 and 18:59 Yangon on `day`, as aware UTC."""
    local = datetime.combine(day, time(9), YANGON) + timedelta(minutes=rng.randrange(600))
    return local.astimezone(ZoneInfo("UTC"))


def build(today: date) -> tuple[list, list, list, list]:
    """Pure data generation: users, products, customers, events (sorted by time)."""
    rng = random.Random(20261020)
    users = [("owner", "owner123", "Shop Owner", "owner")] + [
        (f"sales{i}", "sales123", f"Salesperson {i}", "sales") for i in range(1, 5)]

    products = []  # dicts
    for brand, (factor, warranty) in BRANDS.items():
        for hp, base in HP_PRICE.items():
            for inverter in (False, True):
                price = round(base * factor * (1.3 if inverter else 1.0), -3)
                products.append(dict(
                    sku=f"AC-{brand.upper()}-{hp}-{'INV' if inverter else 'STD'}",
                    name=f"{brand} {hp} HP {'Inverter' if inverter else 'Standard'}", category="aircon",
                    brand=brand, model=f"{brand[:3].upper()}{int(hp * 10)}{'I' if inverter else 'S'}",
                    capacity_hp=hp, is_inverter=inverter, price=int(price), warranty_months=warranty))
    for cat, items in (("accessory", ACCESSORIES), ("service", SERVICES)):
        for sku, (name, price) in items.items():
            products.append(dict(sku=sku, name=name, category=cat, brand=None, model=None, capacity_hp=None,
                                 is_inverter=None, price=price, warranty_months=None))
    by_sku = {p["sku"]: p for p in products}
    aircons = [p for p in products if p["category"] == "aircon"]
    small = [p for p in products if p["category"] != "aircon"]

    customers = []
    for i in range(60):
        phone = None if rng.random() < 0.3 else f"09{rng.randrange(10**8, 10**9)}"
        addr = None if rng.random() < 0.2 else f"No. {rng.randrange(1, 300)}, {rng.choice(TOWNSHIPS)} Township, Yangon"
        customers.append(dict(name=f"{rng.choice(NAMES)} {rng.choice(NAMES)}", phone=phone, address=addr))
    customers[0]["phone"] = customers[1]["phone"] = "09420001111"  # D15: shared phone

    sales = []
    serial_no = 0
    for offset in range(DAYS - 1, -1, -1):
        day = today - timedelta(days=offset)
        hot = day.month in (3, 4, 5)
        for _ in range(rng.randint(5, 11) if hot else rng.randint(3, 8)):
            walk_in = rng.random() < 0.4
            customer = None if walk_in else rng.randrange(len(customers))
            lines = []  # (product, qty)
            if rng.random() < (0.1 if walk_in else 0.75 if hot else 0.5):
                ac = rng.choice(aircons)
                qty = 2 if rng.random() < 0.15 else 1
                lines.append((ac, qty))
                for sku, p in (("SVC-INSTALL", 0.85), ("ACC-BRACKET", 0.7), ("ACC-PIPE", 0.6), ("ACC-STABILIZER", 0.25)):
                    if rng.random() < p:
                        lines.append((by_sku[sku], qty))
            else:
                for p in rng.sample(small, rng.randint(1, 2)):
                    lines.append((p, rng.randint(1, 2)))
            r = rng.random()
            status = "paid" if r < 0.85 else "partial" if r < 0.95 else "unpaid"
            sold_at = yangon_dt(day, rng)
            serials = []
            for p, qty in lines:
                if p["category"] == "aircon":
                    for _ in range(qty):
                        serial_no += 1
                        serials.append((p, f"{p['brand'][:3].upper()}{serial_no:07d}"))
            sales.append(dict(
                sold_at=sold_at, customer=customer, user=rng.randint(1, 4), lines=lines, serials=serials,
                payment_status=status,
                payment_method=None if status == "unpaid" else rng.choices(*METHODS)[0]))

    # ~2% void. The first void is an aircon sale whose serials are re-sold the next day (D13).
    events = [("sale", s["sold_at"], s) for s in sales]
    candidates = [s for s in sales if s["sold_at"].astimezone(YANGON).date() < today - timedelta(days=2)]
    redo = next(s for s in candidates if s["serials"] and s["customer"] is not None)
    others = rng.sample([s for s in candidates if s is not redo], round(len(sales) * 0.02) - 1)
    for s in [redo] + others:
        # redo is voided within the hour, so before its corrected sale the next morning
        voided_at = s["sold_at"] + timedelta(minutes=rng.randrange(10, 60) if s is redo else rng.randrange(30, 24 * 60))
        reason = "Wrong model entered" if s is redo else rng.choice(["Customer cancelled", "Entered twice"])
        events.append(("void", voided_at, dict(sale=s, reason=reason)))
    corrected = dict(redo, sold_at=yangon_dt(redo["sold_at"].astimezone(YANGON).date() + timedelta(days=1), rng))
    events.append(("sale", corrected["sold_at"], corrected))
    events.sort(key=lambda e: (e[1], e[0] == "sale"))
    return users, products, customers, events


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true", help="empty our tables and reset sequences first")
    args = parser.parse_args()
    if args.reset and settings.app_env == "production":
        print("Refusing --reset with APP_ENV=production.", file=sys.stderr)
        return 1

    import bcrypt
    from sqlalchemy import create_engine, insert, text

    from app.models import Customer, Product, Sale, SaleItem, SaleItemSerial, User

    today = datetime.now(YANGON).date()
    users, products, customers, events = build(today)
    engine = create_engine(settings.database_url)
    with engine.begin() as conn:
        if args.reset:
            conn.execute(text(f"TRUNCATE {', '.join(TABLES)} RESTART IDENTITY"))
            conn.execute(text("ALTER SEQUENCE invoice_no_seq RESTART"))
        elif conn.execute(text("SELECT EXISTS (SELECT 1 FROM users)")).scalar():
            print("Database already has data; use --reset.", file=sys.stderr)
            return 1

        hashes = {pw: bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode() for pw in {u[1] for u in users}}
        user_ids = conn.execute(insert(User).returning(User.id), [
            dict(username=u, password_hash=hashes[pw], full_name=n, role=r) for u, pw, n, r in users]).scalars().all()
        product_ids = conn.execute(insert(Product).returning(Product.id, Product.sku), products).all()
        product_id = {sku: pid for pid, sku in product_ids}
        customer_ids = conn.execute(insert(Customer).returning(Customer.id), customers).scalars().all()

        item_ids = {}  # id(sale dict) -> sale_item ids, for voiding
        sale_ids = {}
        for kind, at, e in events:
            if kind == "void":
                sid, items = sale_ids[id(e["sale"])], item_ids[id(e["sale"])]
                # void procedure from docs/schema.md
                conn.execute(text(
                    "INSERT INTO voided_sale_serials (original_sale_item_id, serial_no, warranty_until, voided_at)"
                    " SELECT sale_item_id, serial_no, warranty_until, :at FROM sale_item_serials"
                    " WHERE sale_item_id = ANY(:items)"), {"at": at, "items": items})
                conn.execute(text("DELETE FROM sale_item_serials WHERE sale_item_id = ANY(:items)"), {"items": items})
                conn.execute(text("UPDATE sales SET status = 'void', voided_at = :at, void_reason = :r WHERE id = :id"),
                             {"at": at, "r": e["reason"], "id": sid})
                continue
            seq = conn.execute(text("SELECT nextval('invoice_no_seq')")).scalar()
            sid = conn.execute(insert(Sale).returning(Sale.id), dict(
                invoice_no=f"INV-{seq:06d}",
                customer_id=None if e["customer"] is None else customer_ids[e["customer"]],
                user_id=user_ids[e["user"]], sold_at=at,
                total_amount=sum(p["price"] * q for p, q in e["lines"]),
                payment_status=e["payment_status"], payment_method=e["payment_method"])).scalar()
            ids = conn.execute(insert(SaleItem).returning(SaleItem.id), [
                dict(sale_id=sid, product_id=product_id[p["sku"]], quantity=q, unit_price=p["price"],
                     line_total=p["price"] * q) for p, q in e["lines"]]).scalars().all()
            sale_ids[id(e)], item_ids[id(e)] = sid, ids
            line_of = {p["sku"]: i for (p, _), i in zip(e["lines"], ids)}
            sale_day = at.astimezone(YANGON).date()
            if e["serials"]:
                conn.execute(insert(SaleItemSerial), [
                    dict(sale_item_id=line_of[p["sku"]], serial_no=sn,
                         warranty_until=add_months(sale_day, p["warranty_months"])) for p, sn in e["serials"]])

        for table in TABLES[::-1]:
            print(f"{table:22} {conn.execute(text(f'SELECT count(*) FROM {table}')).scalar():>6}")
        total = conn.execute(text("SELECT coalesce(sum(total_amount), 0) FROM sales WHERE status = 'completed'")).scalar()
        print(f"{'completed sales total':22} {total:>,} MMK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
