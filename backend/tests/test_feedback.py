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

SCAM = (
    "URGENT: HDFC KYC expired. Your account will be suspended in 24 hours. "
    "Click http://hdfc-kyc-update.xyz/a1b2c to verify PAN now. Ref 123456"
)
SAFE = (
    "Rs 2500 debited from your HDFC account ending 4321 on 12-Oct. "
    "If this was not you, call the number on the back of your card."
)


def new_prediction(client):
    return client.post("/predict", json=NORMAL).json()["id"]


def new_scam_check(client, text):
    return client.post("/check-message", json={"text": text}).json()["id"]


def send(client, kind, target_id, action):
    return client.post(
        "/feedback", json={"kind": kind, "target_id": target_id, "action": action}
    )


def test_report_fraud_saves_label_1(client):
    pid = new_prediction(client)
    response = send(client, "transaction", pid, "report_fraud")
    assert response.status_code == 200
    body = response.json()
    assert body["user_label"] == 1
    assert body["updated"] is False


def test_this_was_me_saves_label_0(client):
    pid = new_prediction(client)
    body = send(client, "transaction", pid, "this_was_me").json()
    assert body["user_label"] == 0


def test_feedback_can_be_changed(client):
    pid = new_prediction(client)
    send(client, "transaction", pid, "report_fraud")
    body = send(client, "transaction", pid, "this_was_me").json()
    assert body["updated"] is True
    assert body["user_label"] == 0
    # Still only one feedback row for this prediction
    assert client.get("/feedback/stats").json()["total"] == 1


def test_feedback_for_unknown_prediction_is_404(client):
    response = send(client, "transaction", 9999, "report_fraud")
    assert response.status_code == 404


def test_wrong_action_for_kind_is_rejected(client):
    pid = new_prediction(client)
    response = send(client, "transaction", pid, "report_wrong")
    assert response.status_code == 400


def test_wrong_scam_result_flips_scam_to_safe(client):
    cid = new_scam_check(client, SCAM)  # we said Scam
    body = send(client, "message", cid, "report_wrong").json()
    assert body["user_label"] == 0      # so the true label is Safe


def test_wrong_safe_result_flips_safe_to_scam(client):
    cid = new_scam_check(client, SAFE)  # we said Safe
    body = send(client, "message", cid, "report_wrong").json()
    assert body["user_label"] == 1      # so the true label is Scam


def test_feedback_stats(client):
    send(client, "transaction", new_prediction(client), "report_fraud")
    send(client, "transaction", new_prediction(client), "this_was_me")
    send(client, "message", new_scam_check(client, SCAM), "report_wrong")

    stats = client.get("/feedback/stats").json()
    assert stats["total"] == 3
    assert stats["fraud_reports"] == 1
    assert stats["this_was_me"] == 1
    assert stats["wrong_result_reports"] == 1
    assert stats["fraud_model_version"].startswith("v")
    assert stats["scam_model_version"].startswith("v")
