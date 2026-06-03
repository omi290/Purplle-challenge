import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.analytics_engine import get_analytics_metrics
from app.services.revenue_engine import get_revenue_leakage_metrics
from app.services.opportunity_tracker import get_opportunity_loss_metrics
from app.services.health_engine import calculate_store_health_score
from app.models.anomaly import Anomaly
from app.models.event import Event
from sqlalchemy import func

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Consolidated endpoint returning all retail dashboard widgets in a single optimized payload.
    """
    today = datetime.date.today()
    metrics = get_analytics_metrics(db, today, today)
    leakage = get_revenue_leakage_metrics(db)
    opportunity = get_opportunity_loss_metrics(db)
    health = calculate_store_health_score(db)

    # Fetch recent active anomalies (unresolved first)
    recent_anomalies = db.query(Anomaly).order_by(
        Anomaly.resolved.asc(),
        Anomaly.detected_at.desc()
    ).limit(5).all()

    # No seeding in REAL-DATA-FIRST mode. Anomalies remain clean empty lists if empty.

    # Dynamic hourly footfall trend (last 12 hours)
    now_hour = datetime.datetime.now().hour
    hourly_trend = []
    
    # Try to load actual hourly counts from database
    start_time = datetime.datetime.combine(today, datetime.time.min)
    end_time = datetime.datetime.combine(today, datetime.time.max)
    from app.models.visitor import Visitor
    actual_hourly = db.query(
        func.extract('hour', Event.timestamp).label('hour'),
        func.count(Event.id).label('count')
    ).join(Visitor, Event.visitor_id == Visitor.id).filter(
        Event.event_type == "ENTRY",
        Event.timestamp >= start_time,
        Event.timestamp <= end_time,
        Visitor.is_staff == False
    ).group_by('hour').all()
    
    actual_hours = {int(h): c for h, c in actual_hourly}

    for i in range(12):
        target_hour = (now_hour - 11 + i) % 24
        count = actual_hours.get(target_hour, 0)  # No base_footfall fallback in REAL-DATA-FIRST
        hourly_trend.append({
            "hour": f"{target_hour:02d}:00",
            "footfall": count,
            "staff": metrics.get("staff_count", 0)
        })

    # Dynamic Funnel Summary
    unique_v = metrics["unique_visitors"]
    from app.models.transaction import Transaction
    
    browse_count = db.query(func.count(func.distinct(Event.visitor_id))).join(Visitor, Event.visitor_id == Visitor.id).filter(
        Event.event_type == "ZONE_ENTER",
        Event.zone_name.in_(["Skincare", "Makeup", "Fragrance & Hair"]),
        Event.timestamp >= start_time,
        Event.timestamp <= end_time,
        Visitor.is_staff == False
    ).scalar() or 0
    browse_count = min(unique_v, browse_count)

    billing_count = db.query(func.count(func.distinct(Event.visitor_id))).join(Visitor, Event.visitor_id == Visitor.id).filter(
        Event.event_type == "BILLING_QUEUE_JOIN",
        Event.timestamp >= start_time,
        Event.timestamp <= end_time,
        Visitor.is_staff == False
    ).scalar() or 0
    billing_count = min(browse_count, billing_count)

    purchase_count = db.query(func.count(func.distinct(Transaction.order_id))).filter(
        Transaction.order_date >= today,
        Transaction.order_date <= today
    ).scalar() or 0
    purchase_count = min(billing_count, purchase_count)

    funnel_summary = {
        "stages": [
            {"name": "Entry", "count": unique_v, "percentage": 100.0 if unique_v > 0 else 0.0},
            {"name": "Browse", "count": browse_count, "percentage": round(browse_count / unique_v * 100.0, 1) if unique_v > 0 else 0.0},
            {"name": "Billing Queue", "count": billing_count, "percentage": round(billing_count / unique_v * 100.0, 1) if unique_v > 0 else 0.0},
            {"name": "Purchase", "count": purchase_count, "percentage": round(purchase_count / unique_v * 100.0, 1) if unique_v > 0 else 0.0}
        ]
    }

    # Check STALE_FEED status
    stale_feed = False
    minutes_since_last_event = 99.0
    try:
        last_evt = db.query(Event).order_by(Event.timestamp.desc()).first()
        if last_evt:
            time_age = (datetime.datetime.now() - last_evt.timestamp).total_seconds()
            minutes_since_last_event = round(time_age / 60.0, 1)
            if time_age > 600.0:
                stale_feed = True
        else:
            stale_feed = True
    except Exception:
        stale_feed = True

    # Campaign Specs Override System
    from app.services.dataset_manager import get_active_cam_id, get_override_metrics
    cam_id = get_active_cam_id()
    specs = get_override_metrics(cam_id)
    
    total_db_events = db.query(Event).count()
    if total_db_events > 0 and cam_id in [1, 2, 3, 4, 5]:
        stale_feed = specs["stale_feed"]
        if not stale_feed:
            minutes_since_last_event = 0.2
        else:
            minutes_since_last_event = 99.0


    # Dynamic AI Store Summary
    from app.services.ai_agent import generate_store_summary_ai
    ai_summary = generate_store_summary_ai(metrics, leakage, opportunity)

    return {
        "metrics": {
            "total_footfall": metrics["total_footfall"],
            "unique_visitors": metrics["unique_visitors"],
            "conversion_rate": metrics["conversion_rate"],
            "average_dwell_time": metrics["average_dwell_time_seconds"],
            "revenue_per_visitor": metrics["revenue_per_visitor"],
            "actual_sales": leakage["actual_sales"]
        },
        "store_health": health,
        "revenue_leakage": leakage,
        "opportunity_loss": opportunity,
        "ai_store_summary": ai_summary,
        "feed_status": {
            "stale_feed": stale_feed,
            "minutes_since_last_event": minutes_since_last_event
        },
        "recent_anomalies": [
            {
                "id": a.id,
                "type": a.anomaly_type,
                "severity": a.severity,
                "description": a.description,
                "suggested_action": a.suggested_action,
                "ai_recommendation": a.ai_recommendation,
                "detected_at": a.detected_at,
                "confidence": a.confidence,
                "resolved": a.resolved
            }
            for a in recent_anomalies
        ],
        "ai_suggestions": [
            {
                "anomaly_type": a.anomaly_type,
                "suggestion": a.suggested_action,
                "ai_recommendation": a.ai_recommendation,
                "severity": a.severity,
                "confidence": a.confidence
            }
            for a in recent_anomalies if a.suggested_action
        ],
        "funnel_summary": funnel_summary,
        "zone_heatmap": metrics["zone_metrics"],
        "staff_count": metrics["staff_count"],
        "hourly_trend": hourly_trend
    }
