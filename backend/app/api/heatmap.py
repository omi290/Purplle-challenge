import datetime
import os
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.schemas.heatmap import HeatmapResponse, HeatmapZone, HeatmapZoneCoordinates
from app.models.event import Event
from app.models.session import Session as StoreSession
from app.services.store_layout_parser import parse_store_layout
from app.config import settings

router = APIRouter(prefix="/heatmap", tags=["heatmap"])

@router.get("", response_model=HeatmapResponse)
def get_heatmap(
    start_date: datetime.date = Query(default=None),
    end_date: datetime.date = Query(default=None),
    db: Session = Depends(get_db)
):
    """
    Get retail store zone heatmap traffic densities.
    """
    if start_date is None:
        start_date = datetime.date.today()
    if end_date is None:
        end_date = datetime.date.today()

    start_time = datetime.datetime.combine(start_date, datetime.time.min)
    end_time = datetime.datetime.combine(end_date, datetime.time.max)

    # Load store zones
    layout_file = os.path.join(settings.UPLOAD_DIR, "store_layout.xlsx")
    if not os.path.exists(layout_file):
        workspace_dir = os.path.dirname(settings.UPLOAD_DIR)
        for f in os.listdir(workspace_dir):
            if f.endswith(".xlsx"):
                layout_file = os.path.join(workspace_dir, f)
                break
                
    zones_list = parse_store_layout(layout_file)

    # Query distinct visitor counts per zone
    from app.models.visitor import Visitor
    visitor_query = db.query(
        Event.zone_name,
        func.count(func.distinct(Event.visitor_id)).label('count')
    ).join(Visitor, Event.visitor_id == Visitor.id).filter(
        Event.event_type == "ZONE_ENTER",
        Event.timestamp >= start_time,
        Event.timestamp <= end_time,
        Visitor.is_staff == False
    ).group_by(Event.zone_name).all()

    visitor_counts = {zone_name: count for zone_name, count in visitor_query}

    # Query average detection confidence per zone
    confidence_query = db.query(
        Event.zone_name,
        func.avg(Event.confidence).label('avg_conf')
    ).join(Visitor, Event.visitor_id == Visitor.id).filter(
        Event.event_type == "ZONE_ENTER",
        Event.timestamp >= start_time,
        Event.timestamp <= end_time,
        Visitor.is_staff == False
    ).group_by(Event.zone_name).all()

    zone_confidences = {zone_name: float(avg_conf or 0.88) for zone_name, avg_conf in confidence_query}

    heatmap_zones = []
    max_visitors = 1

    for zone in zones_list:
        if zone.name == "Exit":
            continue
            
        vis_count = visitor_counts.get(zone.name, 0)
            
        if vis_count > max_visitors:
            max_visitors = vis_count

        # Average Dwell inside zone
        avg_dwell = db.query(func.avg(StoreSession.max_dwell_seconds)).join(Visitor, StoreSession.visitor_id == Visitor.id).filter(
            StoreSession.max_dwell_zone == zone.name,
            StoreSession.entry_time >= start_time,
            StoreSession.entry_time <= end_time,
            Visitor.is_staff == False
        ).scalar() or 0.0

        # Calculate session count for data_confidence grading
        session_count = db.query(func.count(StoreSession.id)).join(Visitor, StoreSession.visitor_id == Visitor.id).filter(
            StoreSession.max_dwell_zone == zone.name,
            StoreSession.entry_time >= start_time,
            StoreSession.entry_time <= end_time,
            Visitor.is_staff == False
        ).scalar() or 0

        # Determine confidence level string
        if session_count < 20:
            conf_str = "LOW"
        elif session_count <= 50:
            conf_str = "MEDIUM"
        else:
            conf_str = "HIGH"

        heatmap_zones.append(HeatmapZone(
            zone_name=zone.name,
            zone_type=zone.zone_type,
            visitor_count=vis_count,
            avg_dwell_seconds=round(float(avg_dwell), 1),
            intensity=0.0,  # Will calculate intensity below
            data_confidence=conf_str,
            coordinates=HeatmapZoneCoordinates(
                x1=zone.x1,
                y1=zone.y1,
                x2=zone.x2,
                y2=zone.y2
            )
        ))

    # Calculate intensity proportional to traffic
    for hz in heatmap_zones:
        hz.intensity = round(hz.visitor_count / max_visitors, 2) if max_visitors > 0 else 0.0

    return HeatmapResponse(
        zones=heatmap_zones,
        max_visitors=max_visitors,
        total_zones=len(heatmap_zones)
    )
