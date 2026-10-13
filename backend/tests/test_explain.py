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


def test_risky_transaction_has_reasons(client):
    body = client.post("/predict", json=RISKY).json()
    assert 3 <= len(body["reasons"]) <= 5
    for reason in body["reasons"]:
        assert reason["text"]
        assert reason["direction"] in ("increases", "decreases")
    # At least one reason should explain why the risk went UP
    assert any(r["direction"] == "increases" for r in body["reasons"])
    # One bar per factor for the chart
    assert len(body["contributions"]) == 7


def test_normal_transaction_has_reassuring_reason(client):
    body = client.post("/predict", json=NORMAL).json()
    assert len(body["reasons"]) >= 3
    assert any(r["direction"] == "decreases" for r in body["reasons"])