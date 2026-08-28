import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app


@pytest.fixture(autouse=True)
def _no_real_smtp(monkeypatch: pytest.MonkeyPatch):
    """Tests must never use real SMTP credentials from a developer's local
    .env — force email off by default for every test, regardless of what's
    configured for actual app usage. Individual tests (see
    test_notifications.py) can still monkeypatch their own fake
    SMTP_USERNAME/PASSWORD to exercise the "configured" path, since that
    monkeypatch.setenv happens after this fixture's and overrides it — and
    that path also mocks smtplib.SMTP itself, so no real network call is
    made either way."""
    monkeypatch.setenv("SMTP_USERNAME", "")
    monkeypatch.setenv("SMTP_PASSWORD", "")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    """Logs in as the seeded admin/admin attorney (see the Alembic migration
    that creates it) and returns an Authorization header for protected
    endpoints."""
    response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin"})
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}
