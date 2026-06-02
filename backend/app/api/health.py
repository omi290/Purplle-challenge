import time
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.health import SystemHealthResponse
from app.models.event import Event
from app.services.health_engine import calculate_store_health_score
from app.services.revenue_engine import get_revenue_leakage_metrics
from app.services.opportunity_tracker import get_opportunity_loss_metrics

router = APIRouter(prefix="/health", tags=["health"])

START_TIME = time.time()

@router.get("", response_model=SystemHealthResponse)
def get_system_and_store_health(db: Session = Depends(get_db)):
    """
    Get comprehensive system status, Store Health Score, and Revenue Leakage metrics.
    """
    uptime = time.time() - START_TIME
    
    # Check DB connectivity
    db_status = "connected"
    total_events = 0
    last_event_time = None
    feed_status = "live"
    stale_feed = False
    minutes_since_last_event = None
    try:
        total_events = db.query(Event).count()
        last_evt = db.query(Event).order_by(Event.timestamp.desc()).first()
        if last_evt:
            last_event_time = last_evt.timestamp
            import datetime as dt_mod
            time_age = (dt_mod.datetime.now() - last_event_time).total_seconds()
            minutes_since_last_event = round(time_age / 60.0, 1)
            # If latest event is older than 10 minutes, flag as stale
            if time_age > 600.0:
                stale_feed = True
                feed_status = "stale"
        else:
            stale_feed = True
            feed_status = "stale"
            minutes_since_last_event = 99.0
    except Exception:
        db_status = "disconnected"
        feed_status = "stale"
        stale_feed = True
        minutes_since_last_event = 99.0

    # Compute operational intelligence scores
    store_health = calculate_store_health_score(db)
    revenue_leakage = get_revenue_leakage_metrics(db)
    opportunity_loss = get_opportunity_loss_metrics(db)

    return {
        "status": "healthy",
        "version": "1.0.0",
        "uptime_seconds": uptime,
        "database": db_status,
        "feed_status": feed_status,
        "last_event_time": last_event_time,
        "total_events": total_events,
        "stale_feed": stale_feed,
        "minutes_since_last_event": minutes_since_last_event,
        "store_health": store_health,
        "revenue_leakage": revenue_leakage,
        "opportunity_loss": opportunity_loss
    }
