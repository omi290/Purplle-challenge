import logging
import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.services.analytics_engine import get_analytics_metrics
from app.services.revenue_engine import get_revenue_leakage_metrics
from app.models.anomaly import Anomaly
from app.models.session import Session as StoreSession
from app.models.visitor import Visitor

logger = logging.getLogger(__name__)

def get_opportunity_loss_metrics(db: Session) -> dict:
    """
    Computes unified Opportunity Loss metrics:
    - Opportunity Score (0 - 100) combining checkout abandonment, dead zones, low conversion, and low dwell times.
    - Estimated Revenue Opportunity = unconverted visitors * 15% target conversion * AOV.
    """
    today_start = datetime.datetime.combine(datetime.date.today(), datetime.time.min)

    analytics = get_analytics_metrics(db)
    leakage = get_revenue_leakage_metrics(db)

    unique_visitors = analytics.get("unique_visitors", 0)
    conversion_rate = analytics.get("conversion_rate", 0.0)
    aov = leakage.get("average_basket_value", 450.0)
    actual_orders = int(unique_visitors * conversion_rate)

    # 1. Calculate Contributors & Penalties
    # Component A: Queue Abandonment Penalty (Max 30 points)
    abandonment_rate = leakage.get("leakage_rate", 0.0)
    abandonment_penalty = min(30.0, abandonment_rate * 100.0 * 1.5)

    # Component B: Dead Zones Penalty (Max 30 points)
    active_dead_zones = db.query(Anomaly).filter(
        Anomaly.anomaly_type == "dead_zone",
        Anomaly.resolved == False,
        Anomaly.detected_at >= today_start
    ).count()
    dead_zone_penalty = min(30.0, active_dead_zones * 10.0)

    # Component C: Low Dwell Zones Penalty (Max 20 points)
    browse_zones = ["Skincare", "Makeup", "Fragrance & Hair"]
    low_dwell_zones_count = 0
    for bz in browse_zones:
        avg_dwell = db.query(func.avg(StoreSession.max_dwell_seconds)).join(Visitor, StoreSession.visitor_id == Visitor.id).filter(
            StoreSession.max_dwell_zone == bz,
            StoreSession.entry_time >= today_start,
            Visitor.is_staff == False
        ).scalar() or 0.0
        
        if 0.0 < avg_dwell < 120.0:
            low_dwell_zones_count += 1
            
    dwell_penalty = min(20.0, low_dwell_zones_count * 6.6)

    # Component D: Low Conversion Zones Penalty (Max 20 points)
    conversion_target = 0.35
    conversion_penalty = 0.0
    if conversion_rate < conversion_target:
        conversion_penalty = min(20.0, ((conversion_target - conversion_rate) / conversion_target) * 20.0)

    # 2. Opportunity Score (0 - 100)
    total_penalty = abandonment_penalty + dead_zone_penalty + dwell_penalty + conversion_penalty
    opportunity_score = max(0.0, min(100.0, 100.0 - total_penalty))

    # 3. Estimated Revenue Opportunity
    unconverted_visitors = max(0, unique_visitors - actual_orders)
    target_conversion_achievable = 0.15  # Assume we can recover 15% of missed customers
    achievable_orders = int(unconverted_visitors * target_conversion_achievable)
    estimated_revenue_opportunity = achievable_orders * aov

    # Clean zero-state for REAL-DATA-FIRST mode
    if unique_visitors == 0:
        return {
            "opportunity_score": 100.0,
            "estimated_revenue_opportunity": 0.0,
            "contributors": {
                "queue_abandonment": 0.0,
                "dead_zones": 0.0,
                "low_dwell_zones": 0.0,
                "low_conversion_zones": 0.0
            },
            "total_opportunities_lost": 0,
            "estimated_revenue_impact": 0.0,
            "top_reasons": []
        }

    return {
        "opportunity_score": round(opportunity_score, 1),
        "estimated_revenue_opportunity": round(estimated_revenue_opportunity, 2),
        "contributors": {
            "queue_abandonment": round(abandonment_penalty, 1),
            "dead_zones": round(dead_zone_penalty, 1),
            "low_dwell_zones": round(dwell_penalty, 1),
            "low_conversion_zones": round(conversion_penalty, 1)
        },
        # Backward compatibility for schema:
        "total_opportunities_lost": unconverted_visitors,
        "estimated_revenue_impact": round(estimated_revenue_opportunity, 2),
        "top_reasons": [
            f"Queue abandonment (estimated {abandonment_rate*100:.1f}%) during peak billing hours." if abandonment_penalty > 0 else "Billing queues are running at optimal speed.",
            f"Low customer engagement in {low_dwell_zones_count} browse zones, indicating need for advisors." if dwell_penalty > 0 else "Dwell times indicate high shopper interest in products.",
            f"Overall conversion rate ({conversion_rate*100:.1f}%) lags target 35.0%." if conversion_penalty > 0 else "Overall conversion rate meets or exceeds the target."
        ][:max(1, 3 - (0 if total_penalty > 0 else 2))]
    }
