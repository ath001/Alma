import uuid

from fastapi.testclient import TestClient

from app.config import get_settings


def _create_lead(client: TestClient, *, files=None, **form_overrides):
    data = {
        "first_name": "Ada",
        "last_name": "Lovelace",
        "email": "ada@example.com",
        **form_overrides,
    }
    if files is None:
        files = {"resume": ("resume.pdf", b"%PDF-1.4 fake resume content", "application/pdf")}
    return client.post("/api/v1/leads", data=data, files=files)


def test_create_lead_returns_201_and_pending_state(client: TestClient) -> None:
    response = _create_lead(client)
    assert response.status_code == 201
    body = response.json()
    assert body["state"] == "PENDING"
    assert body["first_name"] == "Ada"
    assert body["resume_filename"] == "resume.pdf"
    assert body["reached_out_at"] is None


def test_create_lead_rejects_bad_content_type(client: TestClient) -> None:
    response = _create_lead(
        client, files={"resume": ("resume.png", b"not a resume", "image/png")}
    )
    assert response.status_code == 400


def test_create_lead_accepts_plain_text_resume(client: TestClient) -> None:
    response = _create_lead(
        client, files={"resume": ("resume.txt", b"plain text resume", "text/plain")}
    )
    assert response.status_code == 201


def test_create_lead_rejects_oversized_file(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("RESUME_MAX_SIZE_MB", "0")
    get_settings.cache_clear()
    try:
        response = _create_lead(client)
        assert response.status_code == 413
    finally:
        monkeypatch.delenv("RESUME_MAX_SIZE_MB", raising=False)
        get_settings.cache_clear()


def test_list_leads_includes_created_lead(client: TestClient) -> None:
    created = _create_lead(client, email="grace@example.com").json()
    listed = client.get("/api/v1/leads").json()
    assert created["id"] in [lead["id"] for lead in listed]


def test_resume_download_round_trips_bytes(client: TestClient) -> None:
    content = b"%PDF-1.4 unique resume bytes for download test"
    created = _create_lead(
        client, files={"resume": ("resume.pdf", content, "application/pdf")}
    ).json()
    response = client.get(f"/api/v1/leads/{created['id']}/resume")
    assert response.status_code == 200
    assert response.content == content
    assert response.headers["content-type"] == "application/pdf"
    assert "resume.pdf" in response.headers["content-disposition"]


def test_resume_download_round_trips_bytes_for_txt(client: TestClient) -> None:
    content = b"plain text resume, byte for byte"
    created = _create_lead(
        client, files={"resume": ("resume.txt", content, "text/plain")}
    ).json()
    response = client.get(f"/api/v1/leads/{created['id']}/resume")
    assert response.status_code == 200
    assert response.content == content
    assert response.headers["content-type"].startswith("text/plain")
    assert "resume.txt" in response.headers["content-disposition"]


def test_resume_download_unknown_id_returns_404(client: TestClient) -> None:
    response = client.get(f"/api/v1/leads/{uuid.uuid4()}/resume")
    assert response.status_code == 404


def test_reach_out_transitions_pending_to_reached_out(client: TestClient) -> None:
    created = _create_lead(client).json()
    response = client.post(f"/api/v1/leads/{created['id']}/reach-out")
    assert response.status_code == 200
    body = response.json()
    assert body["state"] == "REACHED_OUT"
    assert body["reached_out_at"] is not None


def test_reach_out_twice_returns_409(client: TestClient) -> None:
    created = _create_lead(client).json()
    client.post(f"/api/v1/leads/{created['id']}/reach-out")
    response = client.post(f"/api/v1/leads/{created['id']}/reach-out")
    assert response.status_code == 409


def test_reach_out_unknown_id_returns_404(client: TestClient) -> None:
    response = client.post(f"/api/v1/leads/{uuid.uuid4()}/reach-out")
    assert response.status_code == 404
