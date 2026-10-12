from fastapi import APIRouter

from app.config import FRAUD_MODEL_PATH

router = APIRouter()


@router.get("/health")
def health():
    """Quick check that the API is alive and the model file exists."""
    return {"status": "ok", "model_found": FRAUD_MODEL_PATH.exists()}