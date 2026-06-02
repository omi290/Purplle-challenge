from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.revenue_engine import get_revenue_leakage_metrics

router = APIRouter(tags=["revenue"])

@router.get("/revenue-leakage")
@router.get("/api/revenue-leakage")
def get_revenue_leakage(db: Session = Depends(get_db)):
    """
    Get detailed Revenue Leakage Meter metrics.
    Includes lost customers count, POS average basket value, potential revenue lost,
    top loss zones, and recoverable revenue metrics.
    """
    return get_revenue_leakage_metrics(db)
