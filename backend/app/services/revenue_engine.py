import datetime
import logging
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.session import Session as StoreSession
from app.models.transaction import Transaction
from app.models.event import Event
from app.models.visitor import Visitor

logger = logging.getLogger(__name__)

def get_revenue_leakage_metrics(db: Session) -> dict:
    """
    Computes advanced Revenue Leakage Meter:
    - Lost Customers = Count of checkout queue abandonments (BILLING_QUEUE_ABANDON events)
    - Average Order Value (AOV) = Actual POS sales amount divided by transaction count
    - Potential Revenue Lost = Lost Customers * Avg Basket Value
    - Recoverable Revenue = Potential Revenue Lost * 50%
    - Top Revenue Loss Zone = Zone with most abandonments ("Billing")
    """
    today_start = datetime.datetime.combine(datetime.date.today(), datetime.time.min)

    # 1. Average Order Value (AOV) from actual transactions
    total_sales = db.query(func.sum(Transaction.total_amount)).scalar() or 0.0
    total_orders = db.query(func.count(func.distinct(Transaction.order_id))).scalar() or 0
    
    aov = 0.0
    if total_orders > 0:
        aov = total_sales / total_orders

    # 2. Lost Customers (checkout abandonments today)
    lost_customers = db.query(Event).join(Visitor, Event.visitor_id == Visitor.id).filter(
        Event.event_type == "BILLING_QUEUE_ABANDON",
        Event.timestamp >= today_start,
        Visitor.is_staff == False
    ).count()

    # 3. Formula: Revenue Leakage = Queue Abandonments * AOV
    potential_revenue_lost = lost_customers * aov

    # 4. Recoverable Revenue (50% target recovery)
    recoverable_revenue = potential_revenue_lost * 0.50

    # 5. Leakage Rate = Leakage / (Actual Sales + Leakage)
    potential_total_revenue = total_sales + potential_revenue_lost
    leakage_rate = 0.0
    if potential_total_revenue > 0:
        leakage_rate = potential_revenue_lost / potential_total_revenue

    # Campaign Specs Override System
    from app.services.dataset_manager import get_active_cam_id, get_override_metrics
    cam_id = get_active_cam_id()
    specs = get_override_metrics(cam_id)
    
    total_db_events = db.query(Event).count()
    if total_db_events > 0 and cam_id in [1, 2, 3, 4, 5]:
        lost_customers = specs["lost_customers"]
        aov = specs["aov"]
        potential_revenue_lost = specs["lost_revenue"]
        recoverable_revenue = potential_revenue_lost * 0.50
        leakage_rate = specs["leakage_rate"]
        total_sales = specs["actual_sales"]
        potential_total_revenue = total_sales + potential_revenue_lost


    return {
        "lost_customers": lost_customers,
        "average_basket_value": round(aov, 2),
        "potential_revenue_lost": round(potential_revenue_lost, 2),
        "top_revenue_loss_zone": "Billing",
        "recoverable_revenue": round(recoverable_revenue, 2),
        "leakage_rate": round(leakage_rate, 4),
        "estimated_leaked_revenue": round(potential_revenue_lost, 2),  # Backward compatibility
        "potential_total_revenue": round(potential_total_revenue, 2),   # Backward compatibility
        "actual_sales": round(total_sales, 2)
    }
