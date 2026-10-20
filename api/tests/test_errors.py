import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.main import app


class Body(BaseModel):
    name: str
    count: int


@pytest.fixture(scope="module")
def client():
    """App with two throwaway routes: one with a body, one that raises."""
    def echo(body: Body):
        return body

    def boom():
        raise RuntimeError("secret internal detail")

    app.add_api_route("/_test/echo", echo, methods=["POST"])
    app.add_api_route("/_test/boom", boom)
    yield TestClient(app, raise_server_exceptions=False)
    app.router.routes[:] = [r for r in app.router.routes if not getattr(r, "path", "").startswith("/_test/")]


def assert_error(resp, status, code):
    assert resp.status_code == status
    assert set(resp.json()) == {"error"}
    assert set(resp.json()["error"]) == {"code", "message"}
    assert resp.json()["error"]["code"] == code


def test_bad_body_gives_422_in_shared_shape(client):
    resp = client.post("/_test/echo", json={"count": "many"})
    assert_error(resp, 422, "validation_error")
    assert "name: field required" in resp.json()["error"]["message"]


def test_non_json_body_gives_422_in_shared_shape(client):
    assert_error(client.post("/_test/echo", content=b"not json", headers={"content-type": "application/json"}),
                 422, "validation_error")


def test_undecodable_body_gives_422_in_shared_shape(client):
    assert_error(client.post("/_test/echo", content=b"\xff\xfe\x00", headers={"content-type": "application/json"}),
                 422, "validation_error")


def test_unknown_path_gives_404_in_shared_shape(client):
    assert_error(client.get("/no/such/path"), 404, "not_found")


def test_wrong_method_gives_405_in_shared_shape(client):
    resp = client.post("/health")
    assert_error(resp, 405, "method_not_allowed")
    assert resp.headers["allow"] == "GET"


def test_unhandled_exception_gives_500_without_traceback(client):
    resp = client.get("/_test/boom")
    assert_error(resp, 500, "internal_error")
    assert "Traceback" not in resp.text and "secret internal detail" not in resp.text and "RuntimeError" not in resp.text


def test_health_unchanged(client):
    resp = client.get("/health")
    assert resp.status_code == 200 and resp.json() == {"status": "ok"}
