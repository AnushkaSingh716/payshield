"""Retrains the PayShield models using the original data PLUS user feedback.

A new model only replaces the current one if it scores better on the same
held-out test data. The old model is backed up first.

Run from the project root (the backend can keep running):
    python ml/retrain.py                    # both models, needs 5+ feedback rows each
    python ml/retrain.py --min-feedback 1   # easier for demos
    python ml/retrain.py --model fraud      # only the fraud model
    python ml/retrain.py --model scam       # only the scam model
"""
import argparse
import shutil
import sys
from pathlib import Path

import joblib
import mlflow
import pandas as pd
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))  # lets us reuse the backend's settings

from app.config import DATABASE_URL  # noqa: E402
from train_fraud import (  # noqa: E402
    ARTIFACTS,
    FEATURES,
    MODEL_PATH,
    TARGET,
    VERSION_PATH,
    load_data,
)
from train_scam import (  # noqa: E402
    DATA_PATH as SCAM_DATA_PATH,
    MODEL_PATH as SCAM_MODEL_PATH,
    build_pipeline,
)

SCAM_VERSION_PATH = ARTIFACTS / "scam_model_version.txt"

# Same settings as ml/train_fraud.py
FRAUD_PARAMS = {"n_estimators": 200, "max_depth": 5, "learning_rate": 0.1}

FRAUD_FEEDBACK_SQL = """
SELECT p.amount, p.avg_amount_30d, p.amount_ratio, p.hour,
       p.distance_from_home_km, p.txn_count_24h, p.is_new_device,
       p.is_international, p.account_age_days, f.user_label AS is_fraud
FROM feedback f
JOIN predictions p ON p.id = f.prediction_id
WHERE f.kind = 'transaction'
"""

SCAM_FEEDBACK_SQL = """
SELECT s.message_text AS text, f.user_label AS label
FROM feedback f
JOIN scam_checks s ON s.id = f.scam_check_id
WHERE f.kind = 'message'
"""


def read_sql(engine, query):
    with engine.connect() as connection:
        return pd.read_sql(text(query), connection)


def evaluate(predict_proba, X_test, y_test):
    """Precision, recall, F1 and ROC-AUC on the test set."""
    probabilities = predict_proba(X_test)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    return {
        "precision": round(precision_score(y_test, predictions, zero_division=0), 4),
        "recall": round(recall_score(y_test, predictions, zero_division=0), 4),
        "f1": round(f1_score(y_test, predictions, zero_division=0), 4),
        "roc_auc": round(roc_auc_score(y_test, probabilities), 4),
    }


def is_better(new, old, allow_ties):
    """Better = higher F1; if F1 is equal, higher ROC-AUC."""
    new_key = (new["f1"], new["roc_auc"])
    old_key = (old["f1"], old["roc_auc"])
    return new_key >= old_key if allow_ties else new_key > old_key


def print_comparison(old, new):
    print(f"{'metric':>10} {'current':>9} {'new':>9}")
    for name in old:
        print(f"{name:>10} {old[name]:>9.4f} {new[name]:>9.4f}")


def next_version(version_path):
    try:
        current = int(version_path.read_text().strip().lstrip("v"))
    except (FileNotFoundError, ValueError):
        current = 1
    return f"v{current + 1}"


def promote(new_model, model_path, version_path):
    """Back up the old model, save the new one, and bump the version."""
    backup = model_path.with_name(model_path.stem + "_previous.pkl")
    shutil.copy2(model_path, backup)
    joblib.dump(new_model, model_path)
    version = next_version(version_path)
    version_path.write_text(version)
    return version


def log_to_mlflow(experiment, old, new, n_feedback, promoted, model_path):
    mlflow.set_tracking_uri(f"sqlite:///{ROOT / 'mlflow.db'}")
    mlflow.set_experiment(experiment)
    with mlflow.start_run(run_name="retrain"):
        mlflow.log_param("feedback_rows", n_feedback)
        for name in old:
            mlflow.log_metric(f"current_{name}", old[name])
            mlflow.log_metric(f"new_{name}", new[name])
        mlflow.set_tag("promoted", "yes" if promoted else "no")
        if promoted:
            mlflow.log_artifact(str(model_path))


def finish(label, old, new, n_feedback, allow_ties, model, model_path, version_path, experiment):
    """Compare, decide, promote if better, and log to MLflow."""
    print_comparison(old, new)
    promoted = is_better(new, old, allow_ties)
    if promoted:
        version = promote(model, model_path, version_path)
        print(f"\nNew {label} model is better. Replaced the old one (now {version}).")
        print("Restart the backend so it loads the new model.")
    else:
        print(f"\nNew {label} model is not better. Keeping the current one.")
    log_to_mlflow(experiment, old, new, n_feedback, promoted, model_path)


def retrain_fraud(engine, min_feedback, allow_ties):
    print("\n=== Fraud model ===")
    feedback = read_sql(engine, FRAUD_FEEDBACK_SQL)
    if len(feedback) < min_feedback:
        print(f"Only {len(feedback)} feedback rows (need {min_feedback}). Skipping.")
        return
    feedback[["is_new_device", "is_international"]] = feedback[
        ["is_new_device", "is_international"]
    ].astype(int)
    print(f"Feedback rows: {len(feedback)} ({int(feedback[TARGET].sum())} marked as fraud)")

    df = load_data()
    X, y = df[FEATURES], df[TARGET]
    # Same split as ml/train_fraud.py, so the test set is identical and fair
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Training data = original training rows + the user's feedback rows
    X_train = pd.concat([X_train, feedback[FEATURES]], ignore_index=True)
    y_train = pd.concat([y_train, feedback[TARGET]], ignore_index=True)

    weight = (y_train == 0).sum() / max(1, (y_train == 1).sum())
    new_model = XGBClassifier(
        **FRAUD_PARAMS, scale_pos_weight=weight, eval_metric="logloss", random_state=42
    )
    new_model.fit(X_train, y_train)

    current_model = joblib.load(MODEL_PATH)
    old = evaluate(current_model.predict_proba, X_test, y_test)
    new = evaluate(new_model.predict_proba, X_test, y_test)
    finish("fraud", old, new, len(feedback), allow_ties, new_model,
           MODEL_PATH, VERSION_PATH, "payshield-fraud")


def retrain_scam(engine, min_feedback, allow_ties):
    print("\n=== Scam message model ===")
    feedback = read_sql(engine, SCAM_FEEDBACK_SQL)
    if len(feedback) < min_feedback:
        print(f"Only {len(feedback)} feedback rows (need {min_feedback}). Skipping.")
        return
    print(f"Feedback rows: {len(feedback)} ({int(feedback['label'].sum())} marked as scam)")

    df = pd.read_csv(SCAM_DATA_PATH)
    df = df.drop_duplicates(subset="text").dropna(subset=["text", "label"])
    # Same split as ml/train_scam.py
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
    )

    X_train = pd.concat([X_train, feedback["text"]], ignore_index=True)
    y_train = pd.concat([y_train, feedback["label"]], ignore_index=True)

    new_model = build_pipeline()
    new_model.fit(X_train, y_train)

    current_model = joblib.load(SCAM_MODEL_PATH)
    old = evaluate(current_model.predict_proba, X_test, y_test)
    new = evaluate(new_model.predict_proba, X_test, y_test)
    finish("scam", old, new, len(feedback), allow_ties, new_model,
           SCAM_MODEL_PATH, SCAM_VERSION_PATH, "payshield-scam")


def main():
    parser = argparse.ArgumentParser(description="Retrain PayShield with user feedback.")
    parser.add_argument("--model", choices=["fraud", "scam", "all"], default="all")
    parser.add_argument("--min-feedback", type=int, default=5,
                        help="minimum feedback rows needed to retrain (default 5)")
    parser.add_argument("--allow-ties", action="store_true",
                        help="also replace the model when scores are equal (handy for demos)")
    args = parser.parse_args()

    engine = create_engine(DATABASE_URL)
    try:
        if args.model in ("fraud", "all"):
            retrain_fraud(engine, args.min_feedback, args.allow_ties)
        if args.model in ("scam", "all"):
            retrain_scam(engine, args.min_feedback, args.allow_ties)
    except OperationalError:
        print("Could not read feedback from the database. Is the payshield-db container running?")
        print("Start it with:  docker start payshield-db")


if __name__ == "__main__":
    main()