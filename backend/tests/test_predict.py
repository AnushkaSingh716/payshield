NORMAL = {
    "amount": 1200,
    "avg_amount_30d": 1500,
    "hour": 14,
    "distance_from_home_km": 5,
    "txn_count_24h": 2,
    "is_new_device": False,
    "is_international": False,
    "account_age_days": 800,
}

RISKY = {
    "amount": 90000,
    "avg_amount_30d": 1500,
    "hour": 3,
    "distance_from_home_km": 400,
    "txn_count_24h": 9,
    "is_new_device": True,
    "is_international": True,
    "account_age_days": 20,
}


def test_predict_normal_transaction(client):
    response = client.post("/predict", json=NORMAL)
    assert response.status_code == 200
    body = response.json()
    assert body["fraud_probability"] < 0.5
    assert body["label"] in ("Safe", "Suspicious")


def test_predict_risky_transaction(client):
    response = client.post("/predict", json=RISKY)
    assert response.status_code == 200
    body = response.json()
    assert body["fraud_probability"] > 0.5
    assert body["label"] in ("Suspicious", "Fraud")


def test_predict_rejects_bad_input(client):
    bad = {**NORMAL, "hour": 99}  # hour must be 0 to 23
    response = client.post("/predict", json=bad)
    assert response.status_code == 422


def test_transactions_history(client):
    client.post("/predict", json=NORMAL)
    client.post("/predict", json=RISKY)
    response = client.get("/transactions")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_stats(client):
    client.post("/predict", json=NORMAL)
    client.post("/predict", json=RISKY)
    stats = client.get("/stats").json()
    assert stats["total"] == 2
    assert stats["safe"] + stats["suspicious"] + stats["fraud"] == 2