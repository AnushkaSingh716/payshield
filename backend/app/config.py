"""Reads settings from the .env file (or environment variables)."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Project root = the "payshield" folder (this file is backend/app/config.py)
ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

# Some hosts (like Render) give "postgres://..." but SQLAlchemy needs "postgresql://..."
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./payshield.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Websites allowed to call this API (comma-separated in .env)
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
]

# Where the trained fraud model lives
_model_path = Path(os.getenv("FRAUD_MODEL_PATH", "ml/artifacts/model.pkl"))
FRAUD_MODEL_PATH = _model_path if _model_path.is_absolute() else ROOT / _model_path
