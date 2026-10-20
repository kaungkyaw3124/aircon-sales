import os
import subprocess
import sys
from datetime import UTC, datetime

import jwt
import pytest
from fastapi import Depends

from app.auth import get_current_user, make_token
from app.config import settings
from app.main import app
from tests.conftest import API_DIR

INVALID = {"error": {"code": "invalid_credentials", "message": "Wrong username or password."}}
UNAUTHORIZED = {"error": {"code": "unauthorized", "message": "Missing or invalid token."}}


@pytest.fixture(scope="module", autouse=True)
def me_route():
    """Throwaway authenticated route to test get_current_user."""
    app.add_api_route("/_test/me", lambda user=Depends(get_current_user): {"id": user.id})
    yield
    app.router.routes[:] = [r for r in app.router.routes if getattr(r, "path", "") != "/_test/me"]


def login(client, username, password):
    return client.post("/auth/login", json={"username": username, "password": password})


def me(client, token):
    return client.get("/_test/me", headers={"Authorization": f"Bearer {token}"})


def test_correct_login(client, make_user):
    user = make_user()
    resp = login(client, "owner", "secret-pw")
    assert resp.status_code == 200
    body = resp.json()
    assert list(body) == ["access_token", "token_type", "expires_in", "user"]
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == settings.jwt_expire_minutes * 60
    assert body["user"] == {"id": user.id, "username": "owner", "full_name": "U Kyaw Kyaw", "role": "owner"}
    claims = jwt.decode(body["access_token"], settings.jwt_secret, algorithms=["HS256"])
    assert claims["sub"] == str(user.id) and claims["role"] == "owner"
    assert abs(claims["exp"] - datetime.now(UTC).timestamp() - body["expires_in"]) < 60
    assert me(client, body["access_token"]).json() == {"id": user.id}


def test_wrong_password_unknown_user_inactive_user_give_identical_401(client, make_user):
    make_user()
    make_user(username="gone", password="gone-pw", role="sales", active=False)
    responses = [login(client, "owner", "wrong"), login(client, "nobody", "secret-pw"), login(client, "gone", "gone-pw")]
    for resp in responses:
        assert resp.status_code == 401
        assert resp.json() == INVALID


@pytest.mark.parametrize("body", [{}, {"username": "owner"}, {"password": "x"}, {"username": "", "password": "x"}])
def test_missing_fields_give_422(client, body):
    resp = client.post("/auth/login", json=body)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "validation_error"


def test_password_over_72_bytes_gives_401_not_500(client, make_user):
    make_user(username="owner")
    resp = login(client, "owner", "é" * 40)  # 80 bytes in UTF-8
    assert resp.status_code == 401 and resp.json() == INVALID


def test_nul_in_username_gives_401_not_500(client):
    resp = login(client, "own\x00er", "secret-pw")
    assert resp.status_code == 401 and resp.json() == INVALID


def test_missing_token_gives_401(client, make_user):
    resp = client.get("/_test/me")
    assert resp.status_code == 401 and resp.json() == UNAUTHORIZED
    assert resp.headers["www-authenticate"] == "Bearer"


def test_garbage_token_gives_401(client):
    resp = me(client, "not-a-jwt")
    assert resp.status_code == 401 and resp.json() == UNAUTHORIZED


def test_expired_token_gives_401(client, make_user):
    token = make_token(make_user(), datetime.now(UTC), minutes=-1)
    resp = me(client, token)
    assert resp.status_code == 401 and resp.json() == UNAUTHORIZED


def test_token_signed_with_another_secret_gives_401(client, make_user):
    user = make_user()
    token = jwt.encode({"sub": str(user.id), "role": "owner", "exp": datetime.now(UTC).timestamp() + 3600},
                       "x" * 40, algorithm="HS256")
    resp = me(client, token)
    assert resp.status_code == 401 and resp.json() == UNAUTHORIZED


def test_user_deactivated_after_token_issued_gives_401(client, db, make_user):
    user = make_user()
    token = login(client, "owner", "secret-pw").json()["access_token"]
    assert me(client, token).status_code == 200
    user.active = False
    db.flush()
    resp = me(client, token)
    assert resp.status_code == 401 and resp.json() == UNAUTHORIZED


@pytest.mark.parametrize("secret", ["", "short", "x" * 31])
def test_short_jwt_secret_refuses_to_start(secret):
    result = subprocess.run([sys.executable, "-c", "import app.main"], cwd=API_DIR, capture_output=True, text=True,
                            env=os.environ | {"JWT_SECRET": secret})
    assert result.returncode != 0
    assert "JWT_SECRET must be at least 32 characters" in result.stderr


def test_32_char_jwt_secret_starts():
    result = subprocess.run([sys.executable, "-c", "import app.main"], cwd=API_DIR, capture_output=True, text=True,
                            env=os.environ | {"JWT_SECRET": "x" * 32})
    assert result.returncode == 0, result.stderr
