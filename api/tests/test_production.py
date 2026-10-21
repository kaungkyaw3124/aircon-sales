"""Task 3.4: docs off in production, create_user.py, backup retention."""
import os
import subprocess
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import delete

from app.models import User
from tests.conftest import API_DIR

DOC_PATHS = ["/docs", "/redoc", "/openapi.json"]


def test_docs_off_in_production():
    code = ("from fastapi.testclient import TestClient; from app.main import app; c = TestClient(app)\n"
            f"for p in {DOC_PATHS}: r = c.get(p); print('RESULT', r.status_code, r.text)")
    result = subprocess.run([sys.executable, "-c", code], cwd=API_DIR, capture_output=True, text=True,
                            env=os.environ | {"APP_ENV": "production"})
    assert result.returncode == 0, result.stderr
    lines = [line for line in result.stdout.splitlines() if line.startswith("RESULT")]  # skip the access log
    assert lines == ['RESULT 404 {"error":{"code":"not_found","message":"Not Found"}}'] * 3


@pytest.mark.parametrize("path", DOC_PATHS)
def test_docs_on_in_development(client, path):
    assert client.get(path).status_code == 200


NAME = "cu-test-user"
PASSWORD = "long-enough-pw"


@pytest.fixture
def create_user(engine, test_db_url):
    """Runs create_user.py on the test database with `stdin` as the typed input; deletes the user afterwards."""
    def run(*args, stdin=f"{PASSWORD}\n{PASSWORD}\n"):
        # no controlling terminal, so getpass reads the "typed" password from stdin
        return subprocess.run([sys.executable, "scripts/create_user.py", "--username", NAME, *args], cwd=API_DIR,
                              input=stdin, capture_output=True, text=True, start_new_session=True,
                              env=os.environ | {"DATABASE_URL": test_db_url, "APP_ENV": "production"})
    yield run
    with engine.begin() as c:
        c.execute(delete(User).where(User.username == NAME))


def login(client, password=PASSWORD):
    return client.post("/auth/login", json={"username": NAME, "password": password})


def test_create_user_can_log_in(create_user, client):
    result = create_user("--full-name", "Ma Aye", "--role", "sales")
    assert result.returncode == 0, result.stderr
    assert PASSWORD not in result.stdout + result.stderr
    resp = login(client)
    assert resp.status_code == 200
    assert resp.json()["user"] | {"id": 0} == {"id": 0, "username": NAME, "full_name": "Ma Aye", "role": "sales"}


def test_update_changes_password_and_role(create_user, client):
    create_user("--full-name", "Ma Aye", "--role", "sales")
    assert create_user("--role", "owner", stdin="another-long-pw\nanother-long-pw\n").returncode == 0
    assert login(client).status_code == 401
    resp = login(client, "another-long-pw")
    assert resp.status_code == 200 and resp.json()["user"]["role"] == "owner"


@pytest.mark.parametrize("stdin, message", [("short-pw\nshort-pw\n", "at least 10 characters"),
                                            (f"{PASSWORD}\nsomething-else\n", "do not match")])
def test_create_user_refuses_bad_password(create_user, client, stdin, message):
    result = create_user("--full-name", "Ma Aye", "--role", "sales", stdin=stdin)
    assert result.returncode != 0 and message in result.stderr
    assert login(client).status_code == 401


def test_deactivate_makes_login_fail(create_user, client):
    create_user("--full-name", "Ma Aye", "--role", "sales")
    assert create_user("--deactivate", stdin="").returncode == 0
    resp = login(client)
    assert resp.status_code == 401 and resp.json()["error"]["code"] == "invalid_credentials"


def test_password_cannot_be_given_as_argument(create_user):
    result = create_user("--full-name", "Ma Aye", "--role", "sales", "--password", PASSWORD, stdin="")
    assert result.returncode == 2 and "unrecognized arguments" in result.stderr


def run_backup(tmp_path, docker_script):
    """backup.sh with a fake `docker` on PATH and BACKUP_DIR in tmp_path."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    (bin_dir / "docker").write_text(f"#!/bin/sh\n{docker_script}\n")
    (bin_dir / "docker").chmod(0o755)
    return subprocess.run(["bash", str(API_DIR / "scripts" / "backup.sh")], capture_output=True, text=True,
                          env=os.environ | {"PATH": f"{bin_dir}:{os.environ['PATH']}",
                                            "BACKUP_DIR": str(tmp_path / "b")})


def test_backup_retention_daily_and_monthly(tmp_path):
    backups = tmp_path / "b"
    backups.mkdir()
    today = datetime.now(ZoneInfo("Asia/Yangon")).date()
    for i in range(1, 500):  # one fake dump per day for the past 499 days
        (backups / f"aircon-{today - timedelta(days=i)}_0230.dump").write_text("old")
    result = run_backup(tmp_path, "echo fake-dump")
    assert result.returncode == 0, result.stderr

    names = sorted(p.name for p in backups.glob("aircon-*.dump"))
    new = names[-1]
    assert new.startswith(f"aircon-{today}_") and (backups / new).read_text() == "fake-dump\n"
    daily = [f"aircon-{today - timedelta(days=i)}_0230.dump" for i in range(1, 14)] + [new]
    months = sorted({(today.year * 12 + today.month - 1 - i) for i in range(12)})
    firsts = [f"aircon-{m // 12}-{m % 12 + 1:02d}-01_0230.dump" for m in months[:-1]]  # this month's first is `new`
    if today.day > 1:
        firsts.append(f"aircon-{today.replace(day=1)}_0230.dump")
    assert names == sorted(set(daily + firsts))
    assert (backups / "LAST_OK").exists() and not (backups / "LAST_FAILED").exists()


def test_backup_failure_writes_last_failed(tmp_path):
    assert run_backup(tmp_path, "echo fake-dump").returncode == 0
    result = run_backup(tmp_path, "exit 1")
    assert result.returncode == 1 and "backup FAILED" in result.stderr
    assert "pg_dump failed" in (tmp_path / "b" / "LAST_FAILED").read_text()
    assert (tmp_path / "b" / "LAST_OK").exists()  # still says when the last good backup was
    assert run_backup(tmp_path, "echo fake-dump").returncode == 0
    assert not (tmp_path / "b" / "LAST_FAILED").exists()
