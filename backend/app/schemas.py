"""Pydantic schemas: they check incoming data and shape outgoing data."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TransactionIn(BaseModel):
    """What the user sends to POST /predict. Bad values are rejected automatically."""

    amount: float = Field(gt=0, description="Transaction amount in rupees")
    avg_amount_30d: float = Field(gt=0, description="Usual average spend (last 30 days)")
    hour: int = Field(ge=0, le=23, description="Hour of the day, 0 to 23")
    distance_from_home_km: float = Field(ge=0)
    txn_count_24h: int = Field(ge=0, description="Transactions in the last 24 hours")
    is_new_device: bool
    is_international: bool
    account_age_days: int = Field(ge=0)


class PredictionOut(BaseModel):
    """One saved prediction, as returned by the history endpoint."""

    model_config = ConfigDict(from_attributes=True)  # lets us build it from a DB row

    id: int
    created_at: datetime
    amount: float
    avg_amount_30d: float
    amount_ratio: float
    hour: int
    distance_from_home_km: float
    txn_count_24h: int
    is_new_device: bool
    is_international: bool
    account_age_days: int
    fraud_probability: float
    label: str


class Reason(BaseModel):
    """One plain-English reason behind a prediction."""

    text: str
    direction: str  # "increases" or "decreases" the fraud risk


class Contribution(BaseModel):
    """How much one factor pushed the score (positive = toward fraud)."""

    feature: str
    impact: float


class PredictResponse(PredictionOut):
    """What POST /predict returns: the prediction plus its explanation."""

    reasons: list[Reason] = []
    contributions: list[Contribution] = []


class StatsOut(BaseModel):
    """Numbers for the dashboard."""

    total: int
    safe: int
    suspicious: int
    fraud: int
    fraud_rate: float  # percent of all checked transactions