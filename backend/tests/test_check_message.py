SCAM = (
    "URGENT: HDFC KYC expired. Your account will be suspended in 24 hours. "
    "Click http://hdfc-kyc-update.xyz/a1b2c to verify PAN now. Ref 123456"
)
SAFE = (
    "Rs 2500 debited from your HDFC account ending 4321 on 12-Oct. "
    "If this was not you, call the number on the back of your card."
)


def test_scam_message_is_flagged(client):
    response = client.post("/check-message", json={"text": SCAM})
    assert response.status_code == 200
    body = response.json()
    assert body["label"] == "Scam"
    assert body["risk_score"] >= 65
    assert body["urls_found"] == ["http://hdfc-kyc-update.xyz/a1b2c"]
    assert len(body["reasons"]) >= 2


def test_safe_message_is_safe(client):
    response = client.post("/check-message", json={"text": SAFE})
    assert response.status_code == 200
    body = response.json()
    assert body["label"] == "Safe"
    assert body["urls_found"] == []
    assert isinstance(body["id"], int)


def test_message_too_short_is_rejected(client):
    response = client.post("/check-message", json={"text": "a"})
    assert response.status_code == 422


def test_missing_text_is_rejected(client):
    response = client.post("/check-message", json={})
    assert response.status_code == 422
    