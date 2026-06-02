from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.database import get_db
from app.schemas.anomaly import AnomalyResponse
from app.models.anomaly import Anomaly
from app.services.anomaly_engine import run_anomaly_check

class AnomalyFeedbackInput(BaseModel):
    manager_feedback: str
    disagreed: bool = False

router = APIRouter(prefix="/anomalies", tags=["anomalies"])

@router.get("", response_model=List[AnomalyResponse])
def get_anomalies(
    severity: Optional[str] = Query(None, description="low, medium, high, critical"),
    anomaly_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get detected store operational anomalies with AI suggested actions.
    Triggers a fresh anomaly detection scan on request.
    """
    # Trigger a real-time check before returning results
    run_anomaly_check(db)
    
    query = db.query(Anomaly)
    
    if severity:
        query = query.filter(Anomaly.severity == severity)
    if anomaly_type:
        query = query.filter(Anomaly.anomaly_type == anomaly_type)
        
    # Return chronologically descending
    results = query.order_by(Anomaly.detected_at.desc()).offset(offset).limit(limit).all()
    # No seeding in REAL-DATA-FIRST mode. Returns clean scan results.
    return results

@router.post("/{anomaly_id}/feedback", response_model=AnomalyResponse)
def log_anomaly_feedback(anomaly_id: int, payload: AnomalyFeedbackInput, db: Session = Depends(get_db)):
    """
    Log manager feedback and resolve/dismiss the operational anomaly (closed-loop AI).
    """
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
        
    anomaly.manager_feedback = payload.manager_feedback
    anomaly.disagreed = payload.disagreed
    anomaly.resolved = True
    db.commit()
    db.refresh(anomaly)
    return anomaly
