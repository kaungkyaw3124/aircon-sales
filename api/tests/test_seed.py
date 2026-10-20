import os
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import text

from tests.conftest import API_DIR


def run_seed(db_url, **env):
    return subprocess.run([sys.executable, "scripts/seed.py", "--reset"], cwd=API_DIR, capture_output=True,
                          text=True, env=os.environ | {"DATABASE_URL": db_url} | env)


@pytest.fixture(scope="module")
def seeded(engine, test_db_url):
    result = run_seed(test_db_url)
    assert result.returncode == 0, result.stderr
    return engine


def scalar(engine, sql):
    with engine.connect() as c:
        return c.execute(text(sql)).scalar()


def test_production_reset_refuses_and_leaves_data(seeded, test_db_url):
    counts = "SELECT (SELECT count(*) FROM sales), (SELECT count(*) FROM users), (SELECT sum(total_amount) FROM sales)"
    with seeded.connect() as c:
        before = c.execute(text(counts)).one()
    result = run_seed(test_db_url, APP_ENV="production")
    assert result.returncode != 0
    with seeded.connect() as c:
        assert c.execute(text(counts)).one() == before
    assert before[0] > 0


def test_total_amount_equals_sum_of_line_totals(seeded):
    assert scalar(seeded, """
        SELECT count(*) FROM sales s
        WHERE s.total_amount <> (SELECT coalesce(sum(line_total), 0) FROM sale_items WHERE sale_id = s.id)""") == 0


def test_aircon_lines_have_quantity_serials_others_none(seeded):
    assert scalar(seeded, """
        SELECT count(*) FROM sale_items i
        JOIN products p ON p.id = i.product_id
        JOIN sales s ON s.id = i.sale_id
        WHERE s.status = 'completed'
          AND (SELECT count(*) FROM sale_item_serials WHERE sale_item_id = i.id)
              <> CASE WHEN p.category = 'aircon' THEN i.quantity ELSE 0 END""") == 0
    # warranty_until = Yangon sale date + product warranty_months (D14)
    assert scalar(seeded, """
        SELECT count(*) FROM sale_item_serials x
        JOIN sale_items i ON i.id = x.sale_item_id
        JOIN products p ON p.id = i.product_id JOIN sales s ON s.id = i.sale_id
        WHERE x.warranty_until IS DISTINCT FROM
              (date(s.sold_at AT TIME ZONE 'Asia/Yangon') + make_interval(months => p.warranty_months))::date""") == 0


def test_void_sales_have_serials_only_in_voided_table(seeded):
    assert scalar(seeded, """
        SELECT count(*) FROM sale_item_serials x JOIN sale_items i ON i.id = x.sale_item_id
        JOIN sales s ON s.id = i.sale_id WHERE s.status = 'void'""") == 0
    # every voided aircon unit is in voided_sale_serials
    assert scalar(seeded, """
        SELECT count(*) FROM sale_items i JOIN products p ON p.id = i.product_id JOIN sales s ON s.id = i.sale_id
        WHERE s.status = 'void' AND p.category = 'aircon'
          AND (SELECT count(*) FROM voided_sale_serials WHERE original_sale_item_id = i.id) <> i.quantity""") == 0
    # D13: at least one voided serial was sold again
    assert scalar(seeded, """
        SELECT count(*) FROM voided_sale_serials v JOIN sale_item_serials x USING (serial_no)""") > 0


def test_sales_within_opening_hours_and_end_today(seeded):
    assert scalar(seeded, """
        SELECT count(*) FROM sales
        WHERE (sold_at AT TIME ZONE 'Asia/Yangon')::time NOT BETWEEN '09:00' AND '19:00'""") == 0
    last_day = scalar(seeded, "SELECT max(date(sold_at AT TIME ZONE 'Asia/Yangon')) FROM sales")
    assert last_day == datetime.now(ZoneInfo("Asia/Yangon")).date()
