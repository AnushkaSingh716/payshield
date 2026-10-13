"""Loads model.pkl and turns a transaction into a fraud probability."""
import joblib
import pandas as pd

from app.config import FRAUD_MODEL_PATH

# Must match the FEATURES list in ml/train_fraud.py (same names, same order).
FEATURES = [
    "amount",
    "avg_amount_30d",
    "amount_ratio",
    "hour",
    "distance_from_home_km",
    "txn_count_24h",
    "is_new_device",
    "is_international",
    "account_age_days",
]

_model = None  # loaded once, then reused


def get_model():
    global _model
    if _model is None:
        _model = joblib.load(FRAUD_MODEL_PATH)
    return _model


def build_frame(data: dict) -> pd.DataFrame:
    """Turn one transaction (a dict) into the one-row table the model expects."""
    row = dict(data)
    row["is_new_device"] = int(row["is_new_device"])        # True/False -> 1/0
    row["is_international"] = int(row["is_international"])
    return pd.DataFrame([row])[FEATURES]                     # right column order


def predict_probability(data: dict) -> float:
    """Return the chance (0 to 1) that this transaction is fraud."""
    return float(get_model().predict_proba(build_frame(data))[0, 1])


def label_for(probability: float) -> str:
    """Turn a probability into a simple label."""
    if probability < 0.30:
        return "Safe"
    if probability < 0.70:
        return "Suspicious"
    return "Fraud"