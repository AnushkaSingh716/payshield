import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Prediction
from app.schemas import PredictionOut, PredictResponse, TransactionIn
from app.services import explain, fraud_model

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/predict", response_model=PredictResponse)
def predict(txn: TransactionIn, db: Session = Depends(get_db)):
    """Score one transaction, save it, explain it, and return the result."""
    data = txn.model_dump()
    # How unusual is this amount compared with the customer's normal spending?
    data["amount_ratio"] = round(data["amount"] / data["avg_amount_30d"], 2)

    probability = fraud_model.predict_probability(data)

    row = Prediction(
        **data,
        fraud_probability=round(probability, 4),
        label=fraud_model.label_for(probability),
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    # Explain the result. If SHAP ever fails, still return the prediction.
    try:
        reasons, contributions = explain.explain(data)
    except Exception:
        logger.exception("SHAP explanation failed")
        reasons, contributions = [], []

    return PredictResponse(
        **PredictionOut.model_validate(row).model_dump(),
        reasons=reasons,
        contributions=contributions,
    )