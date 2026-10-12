from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Prediction
from app.schemas import PredictionOut, TransactionIn
from app.services import fraud_model

router = APIRouter()


@router.post("/predict", response_model=PredictionOut)
def predict(txn: TransactionIn, db: Session = Depends(get_db)):
    """Score one transaction, save it, and return the result."""
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
    return row
