from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, make_url

from app.config import settings

API_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def test_db_url() -> str:
    url = settings.test_database_url
    assert url and make_url(url).database.endswith("_test"), "tests must run against a *_test database"
    return url


@pytest.fixture(scope="session")
def engine(test_db_url):
    """Fresh schema in the test database: downgrade to base, then upgrade to head."""
    cfg = Config(str(API_DIR / "alembic.ini"), attributes={"configure_logger": False})
    cfg.set_main_option("sqlalchemy.url", test_db_url)
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")
    eng = create_engine(test_db_url)
    yield eng
    eng.dispose()


@pytest.fixture
def conn(engine):
    """Connection in a transaction that is rolled back after the test."""
    with engine.connect() as c:
        tx = c.begin()
        yield c
        tx.rollback()
