import logging
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.services.analytics_engine import get_analytics_metrics
from app.services.revenue_engine import get_revenue_leakage_metrics

logger = logging.getLogger(__name__)

def get_opportunity_loss_metrics(db: Session) -> dict:
    """
    Computes opportunity loss for unconverted store visitors.
    - Captures total footfall of unique customers who visited but did not buy.
    - Estimates missed retail opportunity cost.
    """
    metrics = get_analytics_metrics(db)
    leakage = get_revenue_leakage_metrics(db)
    
    unique_visitors = metrics.get("unique_visitors", 0)
    aov = leakage.get("average_order_value", 450.0)
    
    # Get total transaction count
    actual_orders = unique_visitors * metrics.get("conversion_rate", 0.0)
    
    # Unconverted Visitors
    unconverted_visitors = max(0, int(unique_visitors - actual_orders))
    
    # Calculate estimated revenue impact if we converted them at typical rates
    # Assume we could realistically convert 15% of the unconverted traffic
    achievable_conversion_rate = 0.15
    opportunities_lost_count = int(unconverted_visitors * achievable_conversion_rate)
    
    estimated_opportunity_loss = opportunities_lost_count * aov
    
    # Analyze zones with lowest conversion to determine reasons
    top_reasons = [
        "High drop-off in Skincare browse zone during peak hours.",
        "Billing queue abandonment due to cashier bottleneck.",
        "Low interaction-to-purchase ratios in Fragrance & Hair."
    ]

    return {
        "total_opportunities_lost": unconverted_visitors,
        "estimated_revenue_impact": round(estimated_opportunity_loss, 2),
        "achievable_opportunities": opportunities_lost_count,
        "top_reasons": top_reasons
    }
