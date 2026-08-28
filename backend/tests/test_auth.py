from fastapi.testclient import TestClient


def test_login_with_seeded_admin_succeeds(client: TestClient) -> None:
    response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin"})
    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "admin"
    assert body["token"]


def test_login_with_wrong_password_returns_401(client: TestClient) -> None:
    response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "wrong"})
    assert response.status_code == 401


def test_login_with_unknown_username_returns_401(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login", json={"username": "nobody", "password": "whatever"}
    )
    assert response.status_code == 401


def test_me_without_token_returns_401(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_with_invalid_token_returns_401(client: TestClient) -> None:
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401


def test_me_with_valid_token_returns_username(client: TestClient, auth_headers: dict) -> None:
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "admin"


def test_logout_invalidates_session(client: TestClient, auth_headers: dict) -> None:
    logout_response = client.post("/api/v1/auth/logout", headers=auth_headers)
    assert logout_response.status_code == 204

    me_response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert me_response.status_code == 401
