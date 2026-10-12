from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Prediction
from app.schemas import PredictionOut

router = APIRouter()


@router.get("/transactions", response_model=list[PredictionOut])
def list_transactions(
    limit: int = Query(50, ge=1, le=500), db: Session = Depends(get_db)
):
    """Newest predictions first."""
    return db.query(Prediction).order_by(Prediction.id.desc()).limit(limit).all()
