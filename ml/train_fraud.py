"""Trains the PayShield fraud model (XGBoost), evaluates it, logs it to MLflow,
and saves it as ml/artifacts/model.pkl.

Run from the project root:  python ml/train_fraud.py
"""
from pathlib import Path

import joblib
import mlflow
import pandas as pd
from sklearn.metrics import (
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "ml" / "data" / "fraud_transactions.csv"
ARTIFACTS = ROOT / "ml" / "artifacts"
MODEL_PATH = ARTIFACTS / "model.pkl"
VERSION_PATH = ARTIFACTS / "model_version.txt"

# The columns the model learns from. The API in Phase 3 must send these exact names.
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
TARGET = "is_fraud"


def load_data():
    """Read the CSV and do basic cleaning."""
    df = pd.read_csv(DATA_PATH)
    df = df.drop_duplicates()        # remove repeated rows
    df = df.dropna(subset=FEATURES + [TARGET])  # remove rows with missing values
    return df


def train_and_evaluate(df, params):
    """Split the data, train the model, and return (model, metrics)."""
    X = df[FEATURES]
    y = df[TARGET]

    # Keep 20% of the data hidden for testing. "stratify" keeps the same
    # fraud percentage in both the training and test sets.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Class weights: tell the model one fraud row matters ~49x more than a legit row.
    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

    model = XGBClassifier(
        **params,
        scale_pos_weight=scale_pos_weight,
        eval_metric="logloss",
        random_state=42,
    )
    model.fit(X_train, y_train)

    # Predict on the hidden test data
    probabilities = model.predict_proba(X_test)[:, 1]  # chance of fraud, 0 to 1
    predictions = (probabilities >= 0.5).astype(int)    # 1 = fraud

    metrics = {
        "precision": precision_score(y_test, predictions),
        "recall": recall_score(y_test, predictions),
        "f1": f1_score(y_test, predictions),
        "roc_auc": roc_auc_score(y_test, probabilities),
    }

    print("\n=== Results on the test set ===")
    print(classification_report(y_test, predictions, target_names=["Legit", "Fraud"]))
    for name, value in metrics.items():
        print(f"{name:>10}: {value:.4f}")

    return model, metrics


def main():
    df = load_data()
    print(f"Loaded {len(df):,} rows ({df[TARGET].mean():.2%} fraud)")

    params = {
        "n_estimators": 200,   # number of trees
        "max_depth": 5,        # how deep each tree can go
        "learning_rate": 0.1,  # how fast it learns
    }

    # Where MLflow stores the run history (a local file, ignored by Git)
    mlflow.set_tracking_uri(f"sqlite:///{ROOT / 'mlflow.db'}")
    mlflow.set_experiment("payshield-fraud")

    with mlflow.start_run() as run:
        model, metrics = train_and_evaluate(df, params)

        mlflow.log_params(params)
        mlflow.log_metrics(metrics)

        # Save the model file that the backend will load
        ARTIFACTS.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, MODEL_PATH)
        VERSION_PATH.write_text("v1")
        mlflow.log_artifact(str(MODEL_PATH))

        print(f"\nModel saved to {MODEL_PATH}")
        print(f"MLflow run ID: {run.info.run_id}")


if __name__ == "__main__":
    main()
    