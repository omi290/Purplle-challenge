import os
import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.database import get_db
from app.schemas.event import EventIngest
from app.models.event import Event
from app.models.visitor import Visitor
from app.models.session import Session as StoreSession
from app.services.cv_pipeline import process_video_file
from app.services.event_engine import EventEngine
from app.config import settings

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/ingest", status_code=201)
def ingest_events(payload: EventIngest, db: Session = Depends(get_db)):
    """
    Ingest real-time tracking events.
    """
    events_created = 0
    event_ids = []
    
    # Store layout path
    layout_file = os.path.join(settings.UPLOAD_DIR, "store_layout.xlsx")
    if not os.path.exists(layout_file):
        # Scan if there's any layout xlsx in Purplle-challenge directory
        # (the user's layout is Brigade Road - Store layoutc5f5d56.xlsx)
        search_dir = os.path.dirname(settings.UPLOAD_DIR)
        for f in os.listdir(search_dir):
            if f.endswith(".xlsx"):
                layout_file = os.path.join(search_dir, f)
                break
                
    event_engine = EventEngine(db, layout_file)
    
    try:
        # Loop through Pydantic events, insert into DB
        for e in payload.events:
            # 1. Ensure visitor exists
            visitor = db.query(Visitor).filter(Visitor.track_id == e.track_id).first()
            if not visitor:
                visitor = Visitor(
                    track_id=e.track_id,
                    first_seen=e.timestamp,
                    last_seen=e.timestamp
                )
                db.add(visitor)
                db.flush()
            else:
                visitor.last_seen = e.timestamp
                db.flush()

            # 2. Get active session or create new
            store_session = db.query(StoreSession).filter(
                StoreSession.visitor_id == visitor.id,
                StoreSession.exit_time == None
            ).first()
            
            if not store_session:
                store_session = StoreSession(
                    visitor_id=visitor.id,
                    entry_time=e.timestamp,
                    zones_visited=[e.zone_name] if e.zone_name else []
                )
                db.add(store_session)
                db.flush()
            else:
                # Add to zones visited if not present
                if e.zone_name:
                    visited = list(store_session.zones_visited)
                    if e.zone_name not in visited:
                        visited.append(e.zone_name)
                        store_session.zones_visited = visited
                        db.flush()

            # 3. Create Event record
            db_event = Event(
                visitor_id=visitor.id,
                session_id=store_session.id,
                event_type=e.event_type,
                zone_name=e.zone_name,
                timestamp=e.timestamp,
                confidence=e.confidence,
                bbox_x=e.bbox_x,
                bbox_y=e.bbox_y,
                bbox_w=e.bbox_w,
                bbox_h=e.bbox_h,
                frame_number=e.frame_number,
                metadata_json=e.metadata_json
            )
            db.add(db_event)
            db.flush()
            event_ids.append(db_event.id)
            events_created += 1
            
        db.commit()
        return {
            "status": "success",
            "events_created": events_created,
            "event_ids": event_ids
        }
    except Exception as err:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(err))

def background_video_processing(video_path: str, layout_path: str, db_session: Session):
    try:
        logger = logging.getLogger(__name__)
        logger.info(f"Background task starting: processing video {video_path}")
        
        # Clear database to prevent blending metrics between different video uploads
        from app.models.anomaly import Anomaly
        from app.models.metrics_cache import MetricsCache
        
        logger.info("Wiping existing events, anomalies, sessions, visitors, and metrics cache to ensure a clean slate.")
        db_session.query(Event).delete()
        db_session.query(Anomaly).delete()
        db_session.query(StoreSession).delete()
        db_session.query(Visitor).delete()
        db_session.query(MetricsCache).delete()
        db_session.commit()
        
        # 1. Run CV tracking pipeline
        tracked_detections = process_video_file(video_path)
        
        # 2. Run Event Engine to classify tracking points into retail events
        engine = EventEngine(db_session, layout_path)
        engine.process_tracks(tracked_detections)
        
        logger.info(f"Background task completed: finished processing video {video_path}")
    except Exception as e:
        import traceback
        logging.error(f"Error in background video processing: {e}\n{traceback.format_exc()}")

@router.post("/process-video")
def trigger_video_processing(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Triggers YOLOv8 + ByteTrack processing on uploaded video.
    """
    video_path = os.path.join(settings.VIDEO_DIR, "cctv_footage.mp4")
    
    # Locate layout file
    layout_file = os.path.join(settings.UPLOAD_DIR, "store_layout.xlsx")
    search_dir = "/app" # inside workspace inside container
    if not os.path.exists(layout_file):
        # Look in Purplle-challenge workspace directory
        workspace_dir = os.path.dirname(settings.UPLOAD_DIR)
        for f in os.listdir(workspace_dir):
            if f.endswith(".xlsx"):
                layout_file = os.path.join(workspace_dir, f)
                break

    background_tasks.add_task(background_video_processing, video_path, layout_file, db)
    return {
        "status": "processing_started",
        "video_file": os.path.basename(video_path),
        "message": "Processing in progress asynchronously. Check dashboard for live updates."
    }
