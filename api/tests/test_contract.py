"""Schemathesis contract tests: the in-process app against docs/openapi.yaml."""
from datetime import UTC, datetime, timedelta

import bcrypt
import pytest
import schemathesis
from hypothesis import HealthCheck, settings

from app.auth import make_token
from app.main import app
from tests.conftest import API_DIR
from tests.test_dashboard import YGN, Shop

schema = schemathesis.openapi.from_path(API_DIR.parent / "docs" / "openapi.yaml")
schema.app = app


@pytest.fixture
def token(db, client, make_user):
    """Owner with the contract's example password, and sales today/yesterday so the dashboard isn't empty."""
    shop = Shop(db, client, make_user)
    shop.owner.password_hash = bcrypt.hashpw(b"correct-horse-battery", bcrypt.gensalt(4)).decode()
    today = datetime.now(YGN).date()
    shop.sale(f"{today} 00:00", [("aircon", 1, 1_500_000), ("service", 1, 70_000)], method="kbzpay", pay="partial")
    shop.sale(f"{today} 00:01", [("accessory", 2, 25_000)], pay="unpaid")
    shop.sale(f"{today} 00:02", [("aircon", 1, 900_000)], voided_at=f"{today} 00:03")
    shop.sale(f"{today - timedelta(days=1)} 12:00", [("aircon", 1, 1_000_000)])
    db.flush()
    return make_token(shop.owner, datetime.now(UTC))


@schema.parametrize()
# the endpoints only read data, so sharing one dataset across generated cases is fine
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_api_matches_contract(case, token):
    case.call_and_validate(headers={"Authorization": f"Bearer {token}"})
