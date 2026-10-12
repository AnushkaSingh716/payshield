from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Prediction
from app.schemas import StatsOut

router = APIRouter()


@router.get("/stats", response_model=StatsOut)
def get_stats(db: Session = Depends(get_db)):
    """Counts for the dashboard charts."""
    rows = (
        db.query(Prediction.label, func.count(Prediction.id))
        .group_by(Prediction.label)
        .all()
    )
    counts = dict(rows)
    safe = counts.get("Safe", 0)
    suspicious = counts.get("Suspicious", 0)
    fraud = counts.get("Fraud", 0)
    total = safe + suspicious + fraud
    return StatsOut(
        total=total,
        safe=safe,
        suspicious=suspicious,
        fraud=fraud,
        fraud_rate=round(fraud / total * 100, 2) if total else 0.0,
    )
    