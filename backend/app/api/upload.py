import os
import shutil
import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.services.pos_importer import import_pos_csv
from app.services.store_layout_parser import parse_store_layout
from app.api.events import background_video_processing

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/video")
def upload_video(file: UploadFile = File(...)):
    """
    Upload CCTV footage video.
    """
    if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        raise HTTPException(status_code=400, detail="Invalid video format. Supported: MP4, AVI, MOV, MKV")
        
    os.makedirs(settings.VIDEO_DIR, exist_ok=True)
    file_path = os.path.join(settings.VIDEO_DIR, "cctv_footage.mp4")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Save original filename to a text file for campaign detection
        name_path = os.path.join(settings.UPLOAD_DIR, "original_video_name.txt")
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        with open(name_path, "w") as f:
            f.write(file.filename)

        
        size = os.path.getsize(file_path)
        logger.info(f"Successfully uploaded video to {file_path} (size: {size} bytes)")
        
        return {
            "status": "uploaded",
            "filename": file.filename,
            "size_bytes": size,
            "path": file_path
        }
    except Exception as e:
        logger.error(f"Failed to save uploaded video: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save video: {str(e)}")

@router.post("/store-layout")
def upload_store_layout(file: UploadFile = File(...)):
    """
    Upload store layout XLSX file.
    """
    if not file.filename.lower().endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Invalid file format. Supported: XLSX")
        
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, "store_layout.xlsx")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Parse it right away to validate
        zones = parse_store_layout(file_path)
        
        return {
            "status": "parsed",
            "zones_found": len(zones),
            "zones": [z.name for z in zones]
        }
    except Exception as e:
        logger.error(f"Failed to process store layout upload: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process store layout: {str(e)}")

@router.post("/pos-data")
def upload_pos_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload POS transaction CSV file and import records.
    """
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Supported: CSV")
        
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, "pos_data.csv")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Import to DB
        res = import_pos_csv(file_path, db)
        return res
    except Exception as e:
        logger.error(f"Failed to import POS upload: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process POS data: {str(e)}")

@router.post("/process")
def trigger_full_processing(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Triggers complete retail intelligence parsing pipeline:
    Layout -> Video tracking -> Events -> Aggregations.
    """
    video_path = os.path.join(settings.VIDEO_DIR, "cctv_footage.mp4")
    layout_path = os.path.join(settings.UPLOAD_DIR, "store_layout.xlsx")
    
    # If standard upload files don't exist, search workspace directory
    search_dir = os.path.dirname(settings.UPLOAD_DIR)
    
    if not os.path.exists(video_path):
        # Look for any .mp4 file
        for root, dirs, files in os.walk(search_dir):
            for f in files:
                if f.endswith(".mp4"):
                    video_path = os.path.join(root, f)
                    break
            if os.path.exists(video_path):
                break
                
    if not os.path.exists(layout_path):
        for f in os.listdir(search_dir):
            if f.endswith(".xlsx"):
                layout_path = os.path.join(search_dir, f)
                break

    background_tasks.add_task(background_video_processing, video_path, layout_path)
    return {
        "status": "processing_started",
        "video_file": os.path.basename(video_path),
        "layout_file": os.path.basename(layout_path)
    }

@router.get("/status")
def get_processing_status():
    """
    Queries whether CV background processing is currently running.
    """
    lock_path = os.path.join(settings.UPLOAD_DIR, "processing.lock")
    return {"processing": os.path.exists(lock_path)}

@router.post("/reset")
def reset_database(db: Session = Depends(get_db)):
    """
    Wipes all SQL tables to restore clean zero-state dashboard.
    """
    try:
        from app.models.visitor import Visitor
        from app.models.session import Session as StoreSession
        from app.models.event import Event
        from app.models.anomaly import Anomaly
        from app.models.transaction import Transaction
        from app.models.metrics_cache import MetricsCache
        
        logger.info("Wiping database tables via user request reset endpoint...")
        db.query(Event).delete()
        db.query(Anomaly).delete()
        db.query(StoreSession).delete()
        db.query(Visitor).delete()
        db.query(Transaction).delete()
        db.query(MetricsCache).delete()
        db.commit()
        
        # Delete original video filename file if exists to clear campaign mapping
        name_path = os.path.join(settings.UPLOAD_DIR, "original_video_name.txt")
        if os.path.exists(name_path):
            try:
                os.remove(name_path)
                logger.info("Cleared original_video_name.txt campaign cache.")
            except Exception as fe:
                logger.warning(f"Failed to remove original_video_name.txt: {fe}")
                
        logger.info("Database reset to zero-state successfully.")
        return {"status": "success", "message": "Database tables cleared."}
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to reset database: {e}")
        raise HTTPException(status_code=500, detail=str(e))


