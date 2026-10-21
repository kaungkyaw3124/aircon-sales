"""Login rate limit (D30): 5 failures per username or 20 per client IP in 15 minutes -> 429."""
import os
import socket
import subprocess
import sys
import time
from datetime import UTC, datetime, timedelta

import bcrypt
import httpx
import pytest
from sqlalchemy import delete, func, select

from app import auth
from app.clock import now
from app.main import app
from app.models import LoginFailure, User
from tests.conftest import API_DIR

T0 = datetime(2026, 10, 21, 3, 0, tzinfo=UTC)
LIMITED = {"error": {"code": "rate_limited", "message": "Too many login attempts. Try again in 15 minutes."}}


@pytest.fixture
def clock():
    """Fixed, movable clock for the app; `clock.at` is the current time."""
    class Clock:
        at = T0
    app.dependency_overrides[now] = lambda: Clock.at
    yield Clock


def login(client, username, password, **headers):
    return client.post("/auth/login", json={"username": username, "password": password}, headers=headers)


def test_sixth_attempt_is_limited_even_with_right_password(client, make_user, clock):
    make_user()
    for i in range(5):
        clock.at = T0 + timedelta(minutes=i)
        assert login(client, "owner", "wrong").status_code == 401
    resp = login(client, "owner", "secret-pw")
    assert resp.status_code == 429 and resp.json() == LIMITED
    # the first failure (T0) leaves the window at T0+15m; now is T0+4m
    assert resp.headers["retry-after"] == str(11 * 60)


def test_other_username_still_works(client, make_user, clock):
    make_user()
    make_user(username="sales1", password="sales-pw", role="sales")
    for _ in range(5):
        login(client, "owner", "wrong")
    assert login(client, "owner", "secret-pw").status_code == 429
    assert login(client, "sales1", "sales-pw").status_code == 200


def test_login_works_again_after_window(client, make_user, clock):
    make_user()
    for _ in range(5):
        login(client, "owner", "wrong")
    clock.at = T0 + timedelta(minutes=15) - timedelta(seconds=1)
    resp = login(client, "owner", "secret-pw")
    assert resp.status_code == 429 and resp.headers["retry-after"] == "1"
    clock.at = T0 + timedelta(minutes=15)
    assert login(client, "owner", "secret-pw").status_code == 200


def test_success_resets_username_counter(client, make_user, clock):
    make_user()
    for _ in range(4):
        login(client, "owner", "wrong")
    assert login(client, "owner", "secret-pw").status_code == 200
    for _ in range(4):
        assert login(client, "owner", "wrong").status_code == 401
    assert login(client, "owner", "secret-pw").status_code == 200


def test_ip_limit_across_usernames(client, make_user, clock):
    make_user()
    for i in range(20):
        assert login(client, f"guess{i}", "wrong").status_code == 401
    resp = login(client, "owner", "secret-pw")
    assert resp.status_code == 429 and resp.json() == LIMITED


def test_forwarded_for_ignored_unless_proxy_trusted(client, make_user, clock):
    make_user()
    # untrusted: every request counts against the real peer ("testclient"), whatever header it sends
    for i in range(20):
        login(client, f"guess{i}", "wrong", **{"X-Forwarded-For": f"10.0.0.{i}"})
    assert login(client, "owner", "secret-pw").status_code == 429


def test_trusted_proxy_header_gives_client_ip(client, db, make_user, clock, monkeypatch):
    make_user()
    monkeypatch.setattr(auth, "TRUSTED_PROXIES", {"testclient"})
    for i in range(20):
        login(client, f"guess{i}", "wrong", **{"X-Forwarded-For": "6.6.6.6, 1.2.3.4"})
    assert db.scalar(select(func.count()).where(LoginFailure.ip == "1.2.3.4")) == 20
    assert login(client, "owner", "secret-pw", **{"X-Forwarded-For": "1.2.3.4"}).status_code == 429
    assert login(client, "owner", "secret-pw", **{"X-Forwarded-For": "5.5.5.5"}).status_code == 200


def test_old_rows_are_cleaned_up(client, db, clock):
    login(client, "a", "wrong")
    clock.at = T0 + timedelta(minutes=15)
    login(client, "b", "wrong")
    assert db.scalars(select(LoginFailure.username)).all() == ["b"]


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def two_servers(engine, test_db_url):
    """Two separate uvicorn processes on the test database, like the container's 2 workers."""
    name = "rl-shared-user"
    with engine.begin() as c:
        c.execute(delete(LoginFailure).where(LoginFailure.username == name))
        c.execute(delete(User).where(User.username == name))
        c.execute(User.__table__.insert().values(username=name, full_name="RL", role="owner",
                                                 password_hash=bcrypt.hashpw(b"right-pw", bcrypt.gensalt(4)).decode()))
    env = os.environ | {"DATABASE_URL": test_db_url}
    ports = [free_port(), free_port()]
    procs = [subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--port", str(p), "--no-access-log"],
                              cwd=API_DIR, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for p in ports]
    urls = [f"http://127.0.0.1:{p}" for p in ports]
    try:
        for url in urls:
            for _ in range(100):
                try:
                    httpx.get(url + "/health")
                    break
                except httpx.TransportError:
                    time.sleep(0.1)
        yield name, urls
    finally:
        for p in procs:
            p.terminate()
            p.wait()
        with engine.begin() as c:
            c.execute(delete(LoginFailure).where(LoginFailure.username == name))
            c.execute(delete(User).where(User.username == name))


def test_counters_shared_between_app_instances(two_servers):
    name, (a, b) = two_servers
    body = {"username": name, "password": "wrong"}
    for url in (a, b, a, b, a):
        assert httpx.post(url + "/auth/login", json=body).status_code == 401
    resp = httpx.post(b + "/auth/login", json={"username": name, "password": "right-pw"})
    assert resp.status_code == 429 and "retry-after" in resp.headers
