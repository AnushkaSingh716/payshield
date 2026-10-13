from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ScamCheck
from app.schemas import MessageIn, ScamCheckOut
from app.services import scam_checker

router = APIRouter()


@router.post("/check-message", response_model=ScamCheckOut)
def check_message(body: MessageIn, db: Session = Depends(get_db)):
    """Check a pasted SMS/WhatsApp message and links for scam signs."""
    result = scam_checker.analyze_message(body.text)

    row = ScamCheck(
        message_text=body.text,
        text_score=result["text_score"],
        link_score=result["link_score"],
        risk_score=result["risk_score"],
        label=result["label"],
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return ScamCheckOut(id=row.id, **result)