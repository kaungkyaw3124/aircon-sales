import logging


def test_request_is_logged_in_one_line_without_secrets(client, make_user, caplog):
    make_user(username="owner", password="secret-pw")
    with caplog.at_level(logging.INFO, logger="app.access"):
        token = client.post("/auth/login", json={"username": "owner", "password": "secret-pw"}).json()["access_token"]
        client.get("/dashboard/today?x=1", headers={"Authorization": f"Bearer {token}"})
        client.get("/health")
    lines = [r.getMessage() for r in caplog.records if r.name == "app.access"]
    assert len(lines) == 2
    assert lines[0].startswith("POST /auth/login 200 ") and lines[0].endswith("ms")
    assert lines[1].startswith("GET /dashboard/today 200 ")
    assert not any("secret-pw" in l or token in l or "Bearer" in l for l in lines)
