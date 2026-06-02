import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.metrics import MetricsResponse
from app.services.analytics_engine import get_analytics_metrics

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("", response_model=MetricsResponse)
def get_metrics(
    start_date: datetime.date = Query(default=None, description="Start date YYYY-MM-DD"),
    end_date: datetime.date = Query(default=None, description="End date YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """
    Get retail intelligence metrics for a date range.
    """
    if start_date is None:
        start_date = datetime.date.today()
    if end_date is None:
        end_date = datetime.date.today()
        
    metrics = get_analytics_metrics(db, start_date, end_date)
    return metrics
