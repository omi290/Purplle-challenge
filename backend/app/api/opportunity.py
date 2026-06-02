from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.opportunity_tracker import get_opportunity_loss_metrics

router = APIRouter(tags=["opportunity"])

@router.get("/opportunity-loss")
@router.get("/api/opportunity-loss")
def get_opportunity_loss(db: Session = Depends(get_db)):
    """
    Get detailed Opportunity Loss Tracker metrics.
    Includes overall Opportunity Score (0 - 100) and Estimated Revenue Opportunity.
    """
    return get_opportunity_loss_metrics(db)
