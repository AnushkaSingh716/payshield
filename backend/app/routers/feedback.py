from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import FRAUD_MODEL_PATH, SCAM_MODEL_PATH
from app.database import get_db
from app.models import Feedback, Prediction, ScamCheck
from app.schemas import FeedbackIn, FeedbackOut, FeedbackStats

router = APIRouter()


def read_version(path: Path) -> str:
    """Model versions are stored in small text files next to the models."""
    try:
        return path.read_text().strip() or "v1"
    except OSError:
        return "v1"


@router.post("/feedback", response_model=FeedbackOut)
def submit_feedback(body: FeedbackIn, db: Session = Depends(get_db)):
    """Save the user's correction. One answer per item; sending again replaces it."""
    if body.kind == "transaction":
        if body.action not in ("report_fraud", "this_was_me"):
            raise HTTPException(
                status_code=400,
                detail="Transactions accept 'report_fraud' or 'this_was_me'.",
            )
        if db.get(Prediction, body.target_id) is None:
            raise HTTPException(status_code=404, detail="Prediction not found.")

        user_label = 1 if body.action == "report_fraud" else 0
        links = {"prediction_id": body.target_id}
        existing = (
            db.query(Feedback)
            .filter(Feedback.kind == "transaction", Feedback.prediction_id == body.target_id)
            .first()
        )
    else:
        if body.action != "report_wrong":
            raise HTTPException(
                status_code=400, detail="Messages accept 'report_wrong'."
            )
        check = db.get(ScamCheck, body.target_id)
        if check is None:
            raise HTTPException(status_code=404, detail="Scam check not found.")

        # The user says our answer was wrong, so the true label is the opposite:
        # we said Safe -> it was really a scam; we said Suspicious/Scam -> it was safe.
        user_label = 1 if check.label == "Safe" else 0
        links = {"scam_check_id": body.target_id}
        existing = (
            db.query(Feedback)
            .filter(Feedback.kind == "message", Feedback.scam_check_id == body.target_id)
            .first()
        )

    if existing:
        existing.action = body.action
        existing.user_label = user_label
        row, updated = existing, True
    else:
        row = Feedback(
            kind=body.kind, action=body.action, user_label=user_label, **links
        )
        db.add(row)
        updated = False

    db.commit()
    db.refresh(row)
    return FeedbackOut(
        id=row.id,
        kind=row.kind,
        target_id=body.target_id,
        action=row.action,
        user_label=row.user_label,
        updated=updated,
    )


@router.get("/feedback/stats", response_model=FeedbackStats)
def feedback_stats(db: Session = Depends(get_db)):
    """How many reports came in, and which model versions are in use."""
    counts = dict(
        db.query(Feedback.action, func.count(Feedback.id))
        .group_by(Feedback.action)
        .all()
    )
    return FeedbackStats(
        total=sum(counts.values()),
        fraud_reports=counts.get("report_fraud", 0),
        this_was_me=counts.get("this_was_me", 0),
        wrong_result_reports=counts.get("report_wrong", 0),
        fraud_model_version=read_version(FRAUD_MODEL_PATH.parent / "model_version.txt"),
        scam_model_version=read_version(SCAM_MODEL_PATH.parent / "scam_model_version.txt"),
    )