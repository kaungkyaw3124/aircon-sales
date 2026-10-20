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


@pytest.fixture
def db(conn):
    """ORM session inside the test's rolled-back transaction."""
    from sqlalchemy.orm import Session
    with Session(bind=conn, join_transaction_mode="create_savepoint") as s:
        yield s


@pytest.fixture
def client(db):
    """Test client whose requests use the test transaction."""
    from fastapi.testclient import TestClient
    from app.db import get_db
    from app.main import app
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


@pytest.fixture
def make_user(db):
    """Creates a user with a bcrypt password; returns the User."""
    import bcrypt
    from app.models import User

    def make(username="owner", password="secret-pw", role="owner", active=True, full_name="U Kyaw Kyaw"):
        user = User(username=username, password_hash=bcrypt.hashpw(password.encode(), bcrypt.gensalt(4)).decode(),
                    full_name=full_name, role=role, active=active)
        db.add(user)
        db.flush()
        return user
    return make
