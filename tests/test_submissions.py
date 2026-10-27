"""Bāzes testi: API un MI šķirotājs."""

from app import triage


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_submission_returns_201(client, valid_payload):
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"].startswith("IES-2026-")
    assert data["status"] == "RECEIVED"
    assert data["replyChannel"] == "EMAIL"


def test_get_submission_after_create(client, valid_payload):
    created = client.post("/submissions", json=valid_payload).json()
    response = client.get(f"/submissions/{created['id']}")
    assert response.status_code == 200
    assert response.json()["department"] == "UTILITIES"


def test_unknown_submission_returns_404(client):
    response = client.get("/submissions/IES-2026-999999")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_invalid_personal_code_returns_400(client, valid_payload):
    response = client.post("/submissions", json={**valid_payload, "personalCode": "123"})
    assert response.status_code == 400
    assert response.json()["error"]["details"][0]["field"] == "personalCode"


def test_triage_heating_support_goes_to_social():
    result = triage.route("Apkures pabalsts", "Lūdzu piešķirt apkures pabalstu.")
    assert result.ok
    assert result.department == "SOCIAL"


def test_triage_unclear_goes_to_chancery():
    result = triage.route("Jautājums", "Kad strādā pašvaldība?")
    assert result.department == "CHANCERY"
