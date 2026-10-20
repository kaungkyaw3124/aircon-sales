import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError

TABLES = {"users", "customers", "products", "sales", "sale_items", "sale_item_serials", "voided_sale_serials"}


def test_all_tables_and_invoice_sequence_exist(engine):
    assert TABLES <= set(inspect(engine).get_table_names())
    assert "invoice_no_seq" in inspect(engine).get_sequence_names()


@pytest.fixture
def sale_item(conn):
    """One user, product, sale and sale item; returns their ids."""
    user = conn.execute(text(
        "INSERT INTO users (username, password_hash, full_name, role) VALUES ('u', 'x', 'U', 'sales') RETURNING id"
    )).scalar()
    product = conn.execute(text(
        "INSERT INTO products (sku, name, category, price, warranty_months)"
        " VALUES ('AC-1', 'Aircon', 'aircon', 1500000, 12) RETURNING id"
    )).scalar()
    sale = new_sale(conn, user)
    item = conn.execute(text(
        "INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, line_total)"
        " VALUES (:s, :p, 1, 1500000, 1500000) RETURNING id"
    ), {"s": sale, "p": product}).scalar()
    return {"user": user, "product": product, "sale": sale, "item": item}


def new_sale(conn, user, **cols):
    row = {"invoice_no": f"INV-{conn.execute(text('SELECT nextval(\'invoice_no_seq\')')).scalar():06d}",
           "user_id": user, "total_amount": 1500000, "payment_status": "paid", "payment_method": "cash",
           "status": "completed", "voided_at": None, "void_reason": None} | cols
    return conn.execute(text(
        "INSERT INTO sales (invoice_no, user_id, sold_at, total_amount, payment_status, payment_method,"
        " status, voided_at, void_reason)"
        " VALUES (:invoice_no, :user_id, now(), :total_amount, :payment_status, :payment_method,"
        " :status, :voided_at, :void_reason) RETURNING id"
    ), row).scalar()


def rejected(conn, sql, params=None):
    """True if the statement raises IntegrityError; keeps the outer transaction usable."""
    try:
        with conn.begin_nested():
            conn.execute(text(sql), params or {})
    except IntegrityError:
        return True
    return False


def test_line_total_must_equal_quantity_times_unit_price(conn, sale_item):
    assert rejected(conn,
        "INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, line_total) VALUES (:s, :p, 2, 100, 150)",
        {"s": sale_item["sale"], "p": sale_item["product"]})


def test_void_sale_without_reason_is_rejected(conn, sale_item):
    assert rejected(conn, "UPDATE sales SET status = 'void', voided_at = now() WHERE id = :s",
                    {"s": sale_item["sale"]})
    # control: with a reason it is accepted
    assert not rejected(conn, "UPDATE sales SET status = 'void', voided_at = now(), void_reason = 'test' WHERE id = :s",
                        {"s": sale_item["sale"]})


def test_duplicate_serial_is_rejected(conn, sale_item):
    sql = "INSERT INTO sale_item_serials (sale_item_id, serial_no) VALUES (:i, 'SN-1')"
    assert not rejected(conn, sql, {"i": sale_item["item"]})
    assert rejected(conn, sql, {"i": sale_item["item"]})


def test_deleting_product_used_by_sale_item_is_rejected(conn, sale_item):
    assert rejected(conn, "DELETE FROM products WHERE id = :p", {"p": sale_item["product"]})
