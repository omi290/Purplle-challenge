import logging
from sqlalchemy.orm import Session
from app.services.analytics_engine import get_analytics_metrics
from app.services.revenue_engine import get_revenue_leakage_metrics
from app.models.anomaly import Anomaly

logger = logging.getLogger(__name__)

def calculate_store_health_score(db: Session) -> dict:
    """
    Computes a composite Store Health Score (0-100) based on weighted retail metrics:
    - Conversion Rate Score (25%)
    - Dwell Quality Score (20%)
    - Queue Efficiency Score (20%)
    - Zone Utilization Score (15%)
    - Anomaly Rate Score (10%)
    - Revenue Efficiency Score (10%)
    """
    try:
        metrics = get_analytics_metrics(db)
        leakage = get_revenue_leakage_metrics(db)
        
        if metrics.get("unique_visitors", 0) == 0:
            return {
                "overall_score": 0.0,
                "grade": "N/A",
                "components": {
                    "conversion_rate": {"score": 0.0, "weight": 0.25},
                    "dwell_quality": {"score": 0.0, "weight": 0.20},
                    "queue_efficiency": {"score": 0.0, "weight": 0.20},
                    "zone_utilization": {"score": 0.0, "weight": 0.15},
                    "anomaly_rate": {"score": 0.0, "weight": 0.10},
                    "revenue_efficiency": {"score": 0.0, "weight": 0.10}
                }
            }
        
        # 1. Conversion Rate Score (Weight: 0.25)
        # Standard conversion target is 35% (0.35)
        conv = metrics.get("conversion_rate", 0.0)
        conversion_score = min(100.0, (conv / 0.35) * 100.0)
        
        # 2. Dwell Quality Score (Weight: 0.20)
        # Optimal average dwell time is between 5 to 15 mins (300-900 seconds)
        avg_dwell = metrics.get("average_dwell_time_seconds", 0.0)
        if 300.0 <= avg_dwell <= 900.0:
            dwell_score = 100.0
        elif avg_dwell < 300.0:
            dwell_score = max(0.0, (avg_dwell / 300.0) * 100.0)
        else:
            # penalize extremely high dwell (congestion)
            dwell_score = max(0.0, 100.0 - ((avg_dwell - 900.0) / 900.0) * 100.0)
            
        # 3. Queue Efficiency Score (Weight: 0.20)
        # Based on revenue leakage rate
        leakage_rate = leakage.get("leakage_rate", 0.0)
        queue_score = max(0.0, 100.0 - (leakage_rate * 2.0) * 100.0)
        
        # 4. Zone Utilization Score (Weight: 0.15)
        # Evenness of browsing across Skincare vs Makeup vs Fragrance
        zones = metrics.get("zone_metrics", [])
        if not zones:
            zone_score = 70.0
        else:
            counts = [z["visitor_count"] for z in zones]
            max_c = max(counts) if counts else 1
            min_c = min(counts) if counts else 0
            # Difference ratio
            zone_score = max(0.0, 100.0 - ((max_c - min_c) / max_c) * 50.0)
            
        # 5. Anomaly Rate Score (Weight: 0.10)
        # Penalize unresolved anomalies
        unresolved_anomalies = db.query(Anomaly).filter(Anomaly.resolved == False).count()
        anomaly_score = max(0.0, 100.0 - (unresolved_anomalies * 10.0))
        
        # 6. Revenue Efficiency Score (Weight: 0.10)
        # Revenue per visitor against standard target ₹300
        rpv = metrics.get("revenue_per_visitor", 0.0)
        revenue_score = min(100.0, (rpv / 300.0) * 100.0)
        
        # Weighted Composite
        weighted_score = (
            (conversion_score * 0.25) +
            (dwell_score * 0.20) +
            (queue_score * 0.20) +
            (zone_score * 0.15) +
            (anomaly_score * 0.10) +
            (revenue_score * 0.10)
        )
        
        overall = round(max(0.0, min(100.0, weighted_score)), 1)
        
        # Letter Grade
        if overall >= 85: grade = "A"
        elif overall >= 70: grade = "B"
        elif overall >= 55: grade = "C"
        elif overall >= 40: grade = "D"
        else: grade = "E"
        
        return {
            "overall_score": overall,
            "grade": grade,
            "components": {
                "conversion_rate": {"score": round(conversion_score, 1), "weight": 0.25},
                "dwell_quality": {"score": round(dwell_score, 1), "weight": 0.20},
                "queue_efficiency": {"score": round(queue_score, 1), "weight": 0.20},
                "zone_utilization": {"score": round(zone_score, 1), "weight": 0.15},
                "anomaly_rate": {"score": round(anomaly_score, 1), "weight": 0.10},
                "revenue_efficiency": {"score": round(revenue_score, 1), "weight": 0.10}
            }
        }
    except Exception as e:
        logger.error(f"Error calculating store health score: {e}")
        raise e
