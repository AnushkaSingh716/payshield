"""Database tables."""
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Prediction(Base):
    """One row per transaction that was checked."""

    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # The transaction details that were sent in
    amount: Mapped[float] = mapped_column(Float)
    avg_amount_30d: Mapped[float] = mapped_column(Float)
    amount_ratio: Mapped[float] = mapped_column(Float)
    hour: Mapped[int] = mapped_column(Integer)
    distance_from_home_km: Mapped[float] = mapped_column(Float)
    txn_count_24h: Mapped[int] = mapped_column(Integer)
    is_new_device: Mapped[bool] = mapped_column(Boolean)
    is_international: Mapped[bool] = mapped_column(Boolean)
    account_age_days: Mapped[int] = mapped_column(Integer)

    # What the model decided
    fraud_probability: Mapped[float] = mapped_column(Float)
    label: Mapped[str] = mapped_column(String(20))  # Safe / Suspicious / Fraud


class ScamCheck(Base):
    """One row per message that was checked by the scam checker."""

    __tablename__ = "scam_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    message_text: Mapped[str] = mapped_column(Text)
    text_score: Mapped[float] = mapped_column(Float)   # from the text model, 0-100
    link_score: Mapped[float] = mapped_column(Float)   # from the link rules, 0-100
    risk_score: Mapped[float] = mapped_column(Float)   # final score, 0-100
    label: Mapped[str] = mapped_column(String(20))     # Safe / Suspicious / Scam


class Feedback(Base):
    """A user's correction. It points at either a prediction or a scam check."""

    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    kind: Mapped[str] = mapped_column(String(20))      # "transaction" or "message"
    action: Mapped[str] = mapped_column(String(20))    # report_fraud / this_was_me / report_wrong
    user_label: Mapped[int] = mapped_column(Integer)   # the TRUE label: 1 = fraud/scam, 0 = legit

    # Exactly one of these is filled in
    prediction_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("predictions.id"), nullable=True
    )
    scam_check_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("scam_checks.id"), nullable=True
    )