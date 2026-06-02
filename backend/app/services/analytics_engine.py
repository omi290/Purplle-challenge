import datetime
import logging
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.visitor import Visitor
from app.models.session import Session as StoreSession
from app.models.event import Event
from app.models.transaction import Transaction
from app.models.metrics_cache import MetricsCache

logger = logging.getLogger(__name__)

def get_analytics_metrics(db: Session, start_date: datetime.date = None, end_date: datetime.date = None) -> dict:
    """
    Computes key performance indicators for retail intelligence dashboard.
    """
    if start_date is None:
        start_date = datetime.date.today()
    if end_date is None:
        end_date = datetime.date.today()

    start_time = datetime.datetime.combine(start_date, datetime.time.min)
    end_time = datetime.datetime.combine(end_date, datetime.time.max)

    # 1. Total Footfall (ENTRY events)
    footfall = db.query(Event).filter(
        Event.event_type == "ENTRY",
        Event.timestamp >= start_time,
        Event.timestamp <= end_time
    ).count()

    # 2. Unique Visitors
    unique_visitors = db.query(func.count(Visitor.id)).filter(
        Visitor.first_seen >= start_time,
        Visitor.first_seen <= end_time,
        Visitor.is_staff == False
    ).scalar() or 0

    # 3. Staff count
    staff_count = db.query(func.count(Visitor.id)).filter(
        Visitor.first_seen >= start_time,
        Visitor.first_seen <= end_time,
        Visitor.is_staff == True
    ).scalar() or 0

    # 4. Total transactions & conversion rate
    total_txns = db.query(func.count(func.distinct(Transaction.order_id))).filter(
        Transaction.order_date >= start_date,
        Transaction.order_date <= end_date
    ).scalar() or 0

    conversion_rate = 0.0
    if unique_visitors > 0:
        conversion_rate = min(1.0, total_txns / unique_visitors)

    # 5. Average dwell time
    avg_dwell = db.query(func.avg(StoreSession.duration_seconds)).filter(
        StoreSession.entry_time >= start_time,
        StoreSession.entry_time <= end_time
    ).scalar() or 0.0

    # 6. Revenue per visitor
    total_rev = db.query(func.sum(Transaction.total_amount)).filter(
        Transaction.order_date >= start_date,
        Transaction.order_date <= end_date
    ).scalar() or 0.0

    rev_per_visitor = 0.0
    if unique_visitors > 0:
        rev_per_visitor = total_rev / unique_visitors

    # 7. Bounce rate (visitors who exit within 60s or didn't browse any zone)
    bounces = db.query(func.count(StoreSession.id)).filter(
        StoreSession.entry_time >= start_time,
        StoreSession.entry_time <= end_time,
        StoreSession.duration_seconds < 60.0
    ).scalar() or 0

    total_sessions = db.query(func.count(StoreSession.id)).filter(
        StoreSession.entry_time >= start_time,
        StoreSession.entry_time <= end_time
    ).scalar() or 0

    bounce_rate = 0.0
    if total_sessions > 0:
        bounce_rate = bounces / total_sessions

    # 8. Peak Hours (hour of day -> footfall count)
    hourly_query = db.query(
        func.extract('hour', Event.timestamp).label('hour'),
        func.count(Event.id).label('count')
    ).filter(
        Event.event_type == "ENTRY",
        Event.timestamp >= start_time,
        Event.timestamp <= end_time
    ).group_by('hour').all()

    peak_hours = [{"hour": int(h), "count": count} for h, count in hourly_query]
    # Fill in all 24 hours
    present_hours = {ph["hour"]: ph["count"] for ph in peak_hours}
    peak_hours_complete = [{"hour": h, "count": present_hours.get(h, 0)} for h in range(24)]

    # 9. Zone distribution metrics
    zone_query = db.query(
        Event.zone_name,
        func.count(func.distinct(Event.visitor_id)).label('visitors'),
        func.avg(Event.confidence).label('conf')
    ).filter(
        Event.event_type == "ZONE_ENTER",
        Event.timestamp >= start_time,
        Event.timestamp <= end_time
    ).group_by(Event.zone_name).all()

    zone_metrics = []
    total_conf = 0.0
    conf_count = 0
    for name, vis_cnt, conf in zone_query:
        if not name or name == "Exit":
            continue
        
        # Calculate average dwell in this zone
        avg_dwell_zone = db.query(func.avg(StoreSession.max_dwell_seconds)).filter(
            StoreSession.max_dwell_zone == name,
            StoreSession.entry_time >= start_time,
            StoreSession.entry_time <= end_time
        ).scalar() or 0.0

        zone_metrics.append({
            "zone_name": name,
            "visitor_count": vis_cnt,
            "avg_dwell_seconds": round(float(avg_dwell_zone), 1)
        })
        if conf is not None:
            total_conf += conf
            conf_count += 1

    overall_confidence = 0.85
    if conf_count > 0:
        overall_confidence = total_conf / conf_count

    # Cache metrics in MetricsCache table
    try:
        for m_name, m_val in [
            ("total_footfall", footfall),
            ("unique_visitors", unique_visitors),
            ("conversion_rate", conversion_rate),
            ("average_dwell_time_seconds", avg_dwell),
            ("revenue_per_visitor", rev_per_visitor),
            ("bounce_rate", bounce_rate)
        ]:
            cache_entry = db.query(MetricsCache).filter(
                MetricsCache.metric_name == m_name,
                MetricsCache.period_start == start_time
            ).first()
            if not cache_entry:
                cache_entry = MetricsCache(
                    metric_name=m_name,
                    metric_value=float(m_val),
                    period_start=start_time,
                    period_end=end_time,
                    confidence=overall_confidence
                )
                db.add(cache_entry)
            else:
                cache_entry.metric_value = float(m_val)
                cache_entry.computed_at = datetime.datetime.now()
        db.commit()
    except Exception as cache_error:
        db.rollback()
        logger.error(f"Error caching metrics: {cache_error}")

    return {
        "total_footfall": footfall,
        "unique_visitors": unique_visitors,
        "conversion_rate": round(conversion_rate, 4),
        "average_dwell_time_seconds": round(float(avg_dwell), 1),
        "revenue_per_visitor": round(float(rev_per_visitor), 2),
        "bounce_rate": round(bounce_rate, 4),
        "peak_hours": peak_hours_complete,
        "zone_metrics": zone_metrics,
        "staff_count": staff_count,
        "customer_count": unique_visitors,
        "confidence": round(overall_confidence, 2),
        "period": {
            "start": start_date,
            "end": end_date
        }
    }
