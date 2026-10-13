"""Trains the scam message classifier (TF-IDF + Logistic Regression),
evaluates it, logs it to MLflow, and saves it as ml/artifacts/scam_model.pkl.

Run from the project root:  python ml/train_scam.py
"""
from pathlib import Path

import joblib
import mlflow
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "ml" / "data" / "scam_messages.csv"
ARTIFACTS = ROOT / "ml" / "artifacts"
MODEL_PATH = ARTIFACTS / "scam_model.pkl"

# A few hand-written messages the model has never seen (a quick sanity check)
SANITY_CHECKS = [
    ("Dear user your bank account is suspended, click link to verify now", "scam"),
    ("You have won a free vacation! Send your card details to claim.", "scam"),
    ("Hey are you free for lunch tomorrow?", "safe"),
    ("Your OTP is 482913. Do not share it with anyone.", "safe"),
]


def build_pipeline():
    """TF-IDF turns text into numbers; Logistic Regression learns from them."""
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 2),   # single words and 2-word phrases
                    min_df=2,             # ignore words that appear only once
                    sublinear_tf=True,
                    token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z]+\b",  # letters only
                ),
            ),
            ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )


def main():
    df = pd.read_csv(DATA_PATH)
    df = df.drop_duplicates(subset="text").dropna(subset=["text", "label"])
    print(f"Loaded {len(df):,} messages ({df['label'].mean():.0%} scam)")

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
    )

    mlflow.set_tracking_uri(f"sqlite:///{ROOT / 'mlflow.db'}")
    mlflow.set_experiment("payshield-scam")

    with mlflow.start_run() as run:
        pipeline = build_pipeline()
        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)

        metrics = {
            "precision": precision_score(y_test, predictions),
            "recall": recall_score(y_test, predictions),
            "f1": f1_score(y_test, predictions),
        }

        print("\n=== Results on the test set ===")
        print(classification_report(y_test, predictions, target_names=["Safe", "Scam"]))
        for name, value in metrics.items():
            print(f"{name:>10}: {value:.4f}")

        mlflow.log_params({"model": "TfidfVectorizer + LogisticRegression",
                           "ngram_range": "1-2", "min_df": 2})
        mlflow.log_metrics(metrics)

        ARTIFACTS.mkdir(parents=True, exist_ok=True)
        joblib.dump(pipeline, MODEL_PATH)
        mlflow.log_artifact(str(MODEL_PATH))
        print(f"\nModel saved to {MODEL_PATH}")
        print(f"MLflow run ID: {run.info.run_id}")

    print("\n=== Sanity check on brand-new messages ===")
    for text, expected in SANITY_CHECKS:
        chance = pipeline.predict_proba([text])[0, 1]
        print(f"[expected {expected:>4}] scam chance {chance:5.0%}  |  {text}")


if __name__ == "__main__":
    main()