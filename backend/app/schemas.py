"""Pydantic schemas: they check incoming data and shape outgoing data."""
from datetime import datetime
from typing import Literal

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
    """One plain-English reason behind a result."""

    text: str
    direction: str  # "increases" or "decreases" the risk


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


class MessageIn(BaseModel):
    """What the user sends to POST /check-message."""

    model_config = ConfigDict(str_strip_whitespace=True)

    text: str = Field(min_length=3, max_length=2000)


class ScamCheckOut(BaseModel):
    """What POST /check-message returns."""

    id: int
    risk_score: float          # 0 to 100
    label: str                 # Safe / Suspicious / Scam
    text_score: float          # how scammy the wording looks, 0 to 100
    link_score: float          # how risky the links look, 0 to 100
    reasons: list[Reason]
    urls_found: list[str]


class FeedbackIn(BaseModel):
    """What the user sends to POST /feedback."""

    kind: Literal["transaction", "message"]
    target_id: int = Field(gt=0, description="ID of the prediction or scam check")
    action: Literal["report_fraud", "this_was_me", "report_wrong"]


class FeedbackOut(BaseModel):
    """What POST /feedback returns."""

    id: int
    kind: str
    target_id: int
    action: str
    user_label: int   # the label we saved: 1 = fraud/scam, 0 = legit
    updated: bool     # True if this replaced an earlier answer for the same item


class FeedbackStats(BaseModel):
    """Numbers for the Feedback stats panel."""

    total: int
    fraud_reports: int
    this_was_me: int
    wrong_result_reports: int
    fraud_model_version: str
    scam_model_version: str