import datetime
import logging
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.session import Session as StoreSession
from app.models.transaction import Transaction

logger = logging.getLogger(__name__)

def get_revenue_leakage_metrics(db: Session) -> dict:
    """
    Computes Revenue Leakage Meter:
    - Analyzes sessions that entered the billing area.
    - Compares unique visitors at checkout against actual POS sales.
    - Estimates missed revenue due to queue abandonment or checkout leakage.
    """
    # Get total POS sales today
    total_sales = db.query(func.sum(Transaction.total_amount)).scalar() or 0.0
    total_orders = db.query(func.count(func.distinct(Transaction.order_id))).scalar() or 0
    
    # Average order value (AOV)
    aov = 0.0
    if total_orders > 0:
        aov = total_sales / total_orders
    else:
        aov = 450.0  # Fallback Purplle average cosmetic purchase value

    # Count unique visitors who entered the Billing area
    billing_visitors = db.query(func.count(func.distinct(StoreSession.visitor_id))).filter(
        StoreSession.max_dwell_zone == "Billing"
    ).scalar() or 0

    # Leakage calculation: visitors who reached billing but did not purchase
    leaked_visitors = max(0, billing_visitors - total_orders)
    
    # Leaked Revenue = Leaked Visitors * Average Order Value
    estimated_leaked_revenue = leaked_visitors * aov
    
    # Potential Revenue = Actual Sales + Leaked Revenue
    potential_revenue = total_sales + estimated_leaked_revenue
    
    leakage_rate = 0.0
    if potential_revenue > 0:
        leakage_rate = estimated_leaked_revenue / potential_revenue

    return {
        "leakage_rate": round(leakage_rate, 4),
        "estimated_leaked_revenue": round(estimated_leaked_revenue, 2),
        "potential_total_revenue": round(potential_revenue, 2),
        "average_order_value": round(aov, 2),
        "leaked_visitors_count": leaked_visitors,
        "actual_sales": round(total_sales, 2)
    }
