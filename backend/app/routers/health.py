from fastapi import APIRouter

from app.config import FRAUD_MODEL_PATH, SCAM_MODEL_PATH

router = APIRouter()


@router.get("/health")
def health():
    """Quick check that the API is alive and both model files exist."""
    return {
        "status": "ok",
        "fraud_model_found": FRAUD_MODEL_PATH.exists(),
        "scam_model_found": SCAM_MODEL_PATH.exists(),
    }