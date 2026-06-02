import datetime
import logging
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.anomaly import Anomaly
from app.models.event import Event
from app.models.session import Session as StoreSession
from app.services.recommendation_engine import get_ai_suggestion

logger = logging.getLogger(__name__)

def run_anomaly_check(db: Session) -> int:
    """
    Scans recent events and store states to detect anomalies (queue spikes, conversion drops, etc.).
    Returns the number of new anomalies detected.
    """
    now = datetime.datetime.now()
    two_hours_ago = now - datetime.timedelta(hours=2)
    
    new_anomalies_count = 0

    # 1. Check Billing Queue Spike
    # Count BILLING_QUEUE_JOIN vs ZONE_EXIT in Billing zone
    joins = db.query(Event).filter(
        Event.event_type == "BILLING_QUEUE_JOIN",
        Event.timestamp >= two_hours_ago
    ).count()

    exits = db.query(Event).filter(
        Event.event_type == "ZONE_EXIT",
        Event.zone_name == "Billing",
        Event.timestamp >= two_hours_ago
    ).count()

    current_queue_len = max(0, joins - exits)
    
    # Simple statistical check: if queue size > 8, trigger spike
    if current_queue_len > 8:
        existing = db.query(Anomaly).filter(
            Anomaly.anomaly_type == "queue_spike",
            Anomaly.resolved == False,
            Anomaly.detected_at >= two_hours_ago
        ).first()
        
        if not existing:
            action = get_ai_suggestion("queue_spike")
            anomaly = Anomaly(
                anomaly_type="queue_spike",
                severity="high" if current_queue_len > 12 else "medium",
                description=f"Billing queue spike detected. Current queue size is {current_queue_len} people.",
                suggested_action=action,
                detected_at=now,
                confidence=0.91,
                metric_value=float(current_queue_len),
                threshold_value=8.0,
                zone_name="Billing"
            )
            db.add(anomaly)
            new_anomalies_count += 1

    # 2. Check Queue Abandonment rate
    abandonments = db.query(Event).filter(
        Event.event_type == "BILLING_QUEUE_ABANDON",
        Event.timestamp >= two_hours_ago
    ).count()

    total_billing_visits = db.query(Event).filter(
        Event.event_type == "BILLING_QUEUE_JOIN",
        Event.timestamp >= two_hours_ago
    ).count()

    abandonment_rate = 0.0
    if total_billing_visits > 0:
        abandonment_rate = abandonments / total_billing_visits

    if abandonment_rate > 0.15:  # Greater than 15% abandon queue
        existing = db.query(Anomaly).filter(
            Anomaly.anomaly_type == "high_abandonment",
            Anomaly.resolved == False,
            Anomaly.detected_at >= two_hours_ago
        ).first()
        
        if not existing:
            action = get_ai_suggestion("high_abandonment")
            anomaly = Anomaly(
                anomaly_type="high_abandonment",
                severity="critical" if abandonment_rate > 0.25 else "high",
                description=f"High queue abandonment rate of {abandonment_rate*100:.1f}%. Customers leaving checkout without purchase.",
                suggested_action=action,
                detected_at=now,
                confidence=0.88,
                metric_value=float(abandonment_rate),
                threshold_value=0.15,
                zone_name="Billing"
            )
            db.add(anomaly)
            new_anomalies_count += 1

    # 3. Check for Unusual Dwell times (indicates confusion or congestion)
    avg_dwell_query = db.query(
        Event.zone_name,
        func.avg(StoreSession.duration_seconds).label('avg_dur')
    ).join(StoreSession, Event.session_id == StoreSession.id).filter(
        Event.event_type == "ZONE_ENTER",
        Event.timestamp >= two_hours_ago
    ).group_by(Event.zone_name).all()

    for zone_name, avg_dur in avg_dwell_query:
        if not zone_name or zone_name == "Entrance" or zone_name == "Exit":
            continue
            
        # If average dwell is very long (>300 seconds for browse)
        if avg_dur and avg_dur > 300.0:
            existing = db.query(Anomaly).filter(
                Anomaly.anomaly_type == "unusual_dwell",
                Anomaly.zone_name == zone_name,
                Anomaly.resolved == False,
                Anomaly.detected_at >= two_hours_ago
            ).first()
            
            if not existing:
                action = get_ai_suggestion("unusual_dwell", zone_name)
                anomaly = Anomaly(
                    anomaly_type="unusual_dwell",
                    severity="low",
                    description=f"Unusual high dwell time detected in {zone_name} (avg {avg_dur/60:.1f} minutes). Check for congestion or confusion.",
                    suggested_action=action,
                    detected_at=now,
                    confidence=0.82,
                    metric_value=float(avg_dur),
                    threshold_value=300.0,
                    zone_name=zone_name
                )
                db.add(anomaly)
                new_anomalies_count += 1

    db.commit()
    return new_anomalies_count
