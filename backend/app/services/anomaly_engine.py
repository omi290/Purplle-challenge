import datetime
import logging
import json
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.anomaly import Anomaly
from app.models.event import Event
from app.models.session import Session as StoreSession
from app.models.visitor import Visitor
from app.services.recommendation_engine import get_ai_suggestion_structured, get_ai_suggestion_json
from app.services.ai_agent import explain_anomaly_ai

logger = logging.getLogger(__name__)

class QueueSeverityEngine:
    """
    Stateful evaluation engine to determine queue spikes/abandonment alert severity.
    Levels:
    - INFO (low): minor deviation
    - WARN (high): operational concern
    - CRITICAL (critical): immediate intervention needed
    """
    @staticmethod
    def calculate_severity(queue_depth: int, abandonment_rate: float, avg_wait_seconds: float) -> str:
        scores = []
        
        # 1. Queue depth
        if queue_depth > 12:
            scores.append(3)  # critical
        elif queue_depth >= 8:
            scores.append(2)  # high (warning)
        else:
            scores.append(1)  # low (info)
            
        # 2. Abandonment rate
        if abandonment_rate > 0.25:
            scores.append(3)
        elif abandonment_rate >= 0.15:
            scores.append(2)
        else:
            scores.append(1)
            
        # 3. Waiting duration
        if avg_wait_seconds > 300.0:
            scores.append(3)
        elif avg_wait_seconds >= 180.0:
            scores.append(2)
        else:
            scores.append(1)
            
        max_score = max(scores) if scores else 1
        if max_score == 3:
            return "critical"
        elif max_score == 2:
            return "high"
        else:
            return "low"

def run_anomaly_check(db: Session) -> int:
    """
    Scans recent events and store states to detect anomalies with stateful severities,
    queue escalation engines, dead zone detectors, and structured AI suggestion confidence.
    """
    now = datetime.datetime.now()
    two_hours_ago = now - datetime.timedelta(hours=2)
    new_anomalies_count = 0

    # ==========================================
    # 1. Queue Analytics & QueueSeverityEngine
    # ==========================================
    joins = db.query(Event).join(Visitor, Event.visitor_id == Visitor.id).filter(
        Event.event_type == "BILLING_QUEUE_JOIN",
        Event.timestamp >= two_hours_ago,
        Visitor.is_staff == False
    ).count()

    exits = db.query(Event).join(Visitor, Event.visitor_id == Visitor.id).filter(
        Event.event_type == "ZONE_EXIT",
        Event.zone_name == "Billing",
        Event.timestamp >= two_hours_ago,
        Visitor.is_staff == False
    ).count()

    current_queue_len = max(0, joins - exits)
    
    abandonments = db.query(Event).join(Visitor, Event.visitor_id == Visitor.id).filter(
        Event.event_type == "BILLING_QUEUE_ABANDON",
        Event.timestamp >= two_hours_ago,
        Visitor.is_staff == False
    ).count()

    total_billing_visits = joins
    abandonment_rate = 0.0
    if total_billing_visits > 0:
        abandonment_rate = abandonments / total_billing_visits

    # Average wait time in Billing zone
    avg_wait = db.query(func.avg(StoreSession.duration_seconds)).join(Visitor, StoreSession.visitor_id == Visitor.id).filter(
        StoreSession.max_dwell_zone == "Billing",
        StoreSession.entry_time >= two_hours_ago,
        Visitor.is_staff == False
    ).scalar() or 0.0

    # Calculate severity using QueueSeverityEngine
    calculated_sev = QueueSeverityEngine.calculate_severity(current_queue_len, abandonment_rate, avg_wait)

    # 1.1 Check Billing Queue Spike Anomaly
    if current_queue_len > 8:
        existing = db.query(Anomaly).filter(
            Anomaly.anomaly_type == "queue_spike",
            Anomaly.resolved == False,
            Anomaly.detected_at >= two_hours_ago
        ).first()
        
        if not existing:
            action_json = get_ai_suggestion_json("queue_spike", "Billing", float(current_queue_len), 8.0)
            desc = explain_anomaly_ai("queue_spike", calculated_sev, float(current_queue_len), 8.0, "Billing")
            anomaly = Anomaly(
                anomaly_type="queue_spike",
                severity=calculated_sev,
                description=desc,
                suggested_action=action_json,
                detected_at=now,
                confidence=0.94,
                metric_value=float(current_queue_len),
                threshold_value=8.0,
                zone_name="Billing"
            )
            db.add(anomaly)
            new_anomalies_count += 1
        else:
            # STATEFUL TEMPORAL ESCALATION
            active_duration = (now - existing.detected_at).total_seconds()
            if active_duration >= 600.0 and existing.severity != "critical":
                existing.severity = "critical"
                # Update action to reflect critical escalation
                action_json = get_ai_suggestion_json("queue_spike", "Billing", float(current_queue_len), 8.0)
                # Overwrite reasoning inside the suggestion
                suggestion_data = json.loads(action_json)
                suggestion_data["reasoning"] = f"CRITICAL ESCALATION: Checkout queue unresolved for {int(active_duration/60)} minutes. Capacity bottleneck."
                existing.suggested_action = json.dumps(suggestion_data)
                existing.description = f"CRITICAL ESCALATION: Queue bottleneck unresolved for {int(active_duration/60)} mins. Current size is {current_queue_len} shoppers."
                db.flush()

    # 1.2 Check High Checkout Abandonment Anomaly
    if abandonment_rate > 0.15:
        existing = db.query(Anomaly).filter(
            Anomaly.anomaly_type == "high_abandonment",
            Anomaly.resolved == False,
            Anomaly.detected_at >= two_hours_ago
        ).first()
        
        if not existing:
            action_json = get_ai_suggestion_json("high_abandonment", "Billing", abandonment_rate, 0.15)
            desc = explain_anomaly_ai("high_abandonment", calculated_sev, abandonment_rate, 0.15, "Billing")
            anomaly = Anomaly(
                anomaly_type="high_abandonment",
                severity=calculated_sev,
                description=desc,
                suggested_action=action_json,
                detected_at=now,
                confidence=0.93,
                metric_value=float(abandonment_rate),
                threshold_value=0.15,
                zone_name="Billing"
            )
            db.add(anomaly)
            new_anomalies_count += 1
        else:
            # STATEFUL TEMPORAL ESCALATION
            active_duration = (now - existing.detected_at).total_seconds()
            if active_duration >= 600.0 and existing.severity != "critical":
                existing.severity = "critical"
                action_json = get_ai_suggestion_json("high_abandonment", "Billing", abandonment_rate, 0.15)
                suggestion_data = json.loads(action_json)
                suggestion_data["reasoning"] = f"CRITICAL ESCALATION: High queue abandonment unresolved for {int(active_duration/60)} minutes. Conversion loss."
                existing.suggested_action = json.dumps(suggestion_data)
                existing.description = f"CRITICAL ESCALATION: Checkout drop-off unresolved for {int(active_duration/60)} mins. Abandonment: {abandonment_rate*100:.1f}%."
                db.flush()

    # ==========================================
    # 2. Check for Unusual Dwell times
    # ==========================================
    avg_dwell_query = db.query(
        Event.zone_name,
        func.avg(StoreSession.duration_seconds).label('avg_dur')
    ).join(StoreSession, Event.session_id == StoreSession.id).join(Visitor, StoreSession.visitor_id == Visitor.id).filter(
        Event.event_type == "ZONE_ENTER",
        Event.timestamp >= two_hours_ago,
        Visitor.is_staff == False
    ).group_by(Event.zone_name).all()

    for zone_name, avg_dur in avg_dwell_query:
        if not zone_name or zone_name in ["Entrance", "Exit", "Billing"]:
            continue
            
        if avg_dur and avg_dur > 300.0:
            existing = db.query(Anomaly).filter(
                Anomaly.anomaly_type == "unusual_dwell",
                Anomaly.zone_name == zone_name,
                Anomaly.resolved == False,
                Anomaly.detected_at >= two_hours_ago
            ).first()
            
            if not existing:
                action_json = get_ai_suggestion_json("unusual_dwell", zone_name, float(avg_dur), 300.0)
                desc = explain_anomaly_ai("unusual_dwell", "low", float(avg_dur), 300.0, zone_name)
                anomaly = Anomaly(
                    anomaly_type="unusual_dwell",
                    severity="low",
                    description=desc,
                    suggested_action=action_json,
                    detected_at=now,
                    confidence=0.85,
                    metric_value=float(avg_dur),
                    threshold_value=300.0,
                    zone_name=zone_name
                )
                db.add(anomaly)
                new_anomalies_count += 1

    # ==========================================
    # 3. Dynamic DEAD_ZONE Detection Engine
    # ==========================================
    today_start = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    total_uniques = db.query(func.count(Visitor.id)).filter(
        Visitor.first_seen >= today_start,
        Visitor.is_staff == False
    ).scalar() or 0

    if total_uniques > 0:
        browse_zones = ["Skincare", "Makeup", "Fragrance & Hair"]

        # 3.1 Calculate traffic statistical averages for dead zone checking
        zone_visitors = {}
        dead_zone_query = db.query(
            Event.zone_name,
            func.count(func.distinct(Event.visitor_id)).label('cnt')
        ).join(Visitor, Event.visitor_id == Visitor.id).filter(
            Event.event_type == "ZONE_ENTER",
            Event.timestamp >= today_start,
            Visitor.is_staff == False
        ).group_by(Event.zone_name).all()
        
        zone_visitors = {name: cnt for name, cnt in dead_zone_query}

        # Store average traffic count
        avg_zone_traffic = sum(zone_visitors.values()) / len(browse_zones) if zone_visitors else 0.0

        for bz in browse_zones:
            # Check Condition A: Inactivity (No activity for 30+ minutes)
            last_evt = db.query(Event).filter(
                Event.zone_name == bz,
                Event.timestamp >= today_start
            ).order_by(Event.timestamp.desc()).first()

            if last_evt:
                inactive_minutes = (now - last_evt.timestamp).total_seconds() / 60.0
            else:
                inactive_minutes = (now - today_start).total_seconds() / 60.0

            # Check Condition B: Statistical underperformance (<10% of overall zone average traffic)
            traffic_count = zone_visitors.get(bz, 0)
            is_statistically_low = (avg_zone_traffic > 0 and (traffic_count / avg_zone_traffic) < 0.10)
            is_statistically_warn = (avg_zone_traffic > 0 and (traffic_count / avg_zone_traffic) < 0.15)

            # Trigger DEAD_ZONE alert
            if inactive_minutes >= 30.0 or is_statistically_low:
                existing = db.query(Anomaly).filter(
                    Anomaly.anomaly_type == "dead_zone",
                    Anomaly.zone_name == bz,
                    Anomaly.resolved == False,
                    Anomaly.detected_at >= today_start
                ).first()

                if not existing:
                    # Severity determination
                    if inactive_minutes >= 30.0:
                        severity = "critical"  # Zero activity in browse zone for 30+ minutes
                    elif is_statistically_low:
                        severity = "high"
                    else:
                        severity = "low"

                    ratio = traffic_count / total_uniques if total_uniques > 0 else 0.0
                    desc = explain_anomaly_ai("dead_zone", severity, ratio, 0.10, bz)
                    action_json = get_ai_suggestion_json("dead_zone", bz, ratio, 0.10)
                    
                    anomaly = Anomaly(
                        anomaly_type="dead_zone",
                        severity=severity,
                        description=desc,
                        suggested_action=action_json,
                        detected_at=now,
                        confidence=0.90,
                        metric_value=float(ratio),
                        threshold_value=0.10,
                        zone_name=bz
                    )
                    db.add(anomaly)
                    new_anomalies_count += 1
                else:
                    # Update existing dead zone description if inactivity persists
                    if inactive_minutes >= 30.0 and existing.severity != "critical":
                        existing.severity = "critical"
                        existing.description = f"CRITICAL DEAD ZONE: Zero customer activity in {bz} for the last {int(inactive_minutes)} minutes."
                        db.flush()

    db.commit()
    return new_anomalies_count
