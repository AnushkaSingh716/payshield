"""Reads settings from the .env file (or environment variables)."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Project root = the "payshield" folder (this file is backend/app/config.py)
ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./payshield.db")

# Hosts like Render give "postgres://..." and our .env uses "postgresql://...".
# SQLAlchemy needs the driver named explicitly: "postgresql+psycopg://..."
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# Websites allowed to call this API (comma-separated in .env)
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
]


def _resolve(path_text: str) -> Path:
    """Relative paths are measured from the project root."""
    path = Path(path_text)
    return path if path.is_absolute() else ROOT / path


# Where the trained models live
FRAUD_MODEL_PATH = _resolve(os.getenv("FRAUD_MODEL_PATH", "ml/artifacts/model.pkl"))
SCAM_MODEL_PATH = _resolve(os.getenv("SCAM_MODEL_PATH", "ml/artifacts/scam_model.pkl"))