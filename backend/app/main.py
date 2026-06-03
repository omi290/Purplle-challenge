import os
import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.config import settings
from app.logging_config import setup_logging
from app.database import Base, engine, SessionLocal
from app.middleware import TraceIDMiddleware
from sqlalchemy import text

# Setup structured logger
logger = setup_logging()

# FastAPI Initialization
app = FastAPI(
    title="Apex Retail Intelligence OS",
    description="Convert CCTV footage into actionable retail store intelligence.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Policy configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core Middleware registration
app.add_middleware(TraceIDMiddleware)

# API Routers import
from app.api import events, metrics, funnel, heatmap, anomalies, health, upload, dashboard, revenue_leakage, opportunity

app.include_router(events.router, prefix="/api")
app.include_router(metrics.router, prefix="/api")
app.include_router(funnel.router, prefix="/api")
app.include_router(heatmap.router, prefix="/api")
app.include_router(anomalies.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(revenue_leakage.router)
app.include_router(opportunity.router)

@app.on_event("startup")
def startup_event():
    logger.info("Initializing database schemas...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database schemas initialized.")
    
    # Self-healing migrations for closed-loop AI manager feedback
    db = SessionLocal()
    try:
        db.execute(text("ALTER TABLE anomalies ADD COLUMN IF NOT EXISTS manager_feedback TEXT;"))
        db.execute(text("ALTER TABLE anomalies ADD COLUMN IF NOT EXISTS disagreed BOOLEAN DEFAULT FALSE;"))
        db.commit()
        logger.info("Database self-healing migrations applied successfully.")
    except Exception as e:
        db.rollback()
        logger.warning(f"Database self-healing migrations skipped or already applied: {e}")
    finally:
        db.close()
    
    # Force clean database state on startup to ensure a clean launch
    db = SessionLocal()
    try:
        from app.models.visitor import Visitor
        from app.models.session import Session as StoreSession
        from app.models.event import Event
        from app.models.anomaly import Anomaly
        from app.models.transaction import Transaction
        from app.models.metrics_cache import MetricsCache
        
        logger.info("Wiping all database tables on fresh launch to enforce zero-state dashboard...")
        db.query(Event).delete()
        db.query(Anomaly).delete()
        db.query(StoreSession).delete()
        db.query(Visitor).delete()
        db.query(Transaction).delete()
        db.query(MetricsCache).delete()
        db.commit()
        logger.info("Database tables cleared successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to clear database tables on startup: {e}")
    finally:
        db.close()
    
    # Pre-populate store data if the local files are present
    db = SessionLocal()
    try:
        # Search workspace directory for store files
        search_dir = os.path.dirname(settings.UPLOAD_DIR)
        
        # 1. Look for POS CSV
        pos_file = None
        for f in os.listdir(search_dir):
            if f.endswith(".csv") and "Brigade" in f:
                pos_file = os.path.join(search_dir, f)
                break
                
        if pos_file:
            logger.info(f"Auto-importing POS data from {pos_file}...")
            from app.services.pos_importer import import_pos_csv
            import_pos_csv(pos_file, db)
            
        # 2. Look for layout XLSX
        layout_file = None
        for f in os.listdir(search_dir):
            if f.endswith(".xlsx") and "layout" in f.lower():
                layout_file = os.path.join(search_dir, f)
                break
                
        if layout_file:
            logger.info(f"Auto-registering store layout from {layout_file}...")
            # Save a copy under standard upload folder inside container volume
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
            shutil_path = os.path.join(settings.UPLOAD_DIR, "store_layout.xlsx")
            import shutil
            shutil.copy(layout_file, shutil_path)
            
        # 3. Pre-populate simulated tracking events bypassed in REAL-DATA-FIRST mode.
        logger.info("REAL-DATA-FIRST mode: Awaiting manual CCTV ingestion to build tracking events.")
            
    except Exception as e:
        logger.error(f"Error during startup data initialization: {e}")
    finally:
        db.close()


@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "app": "Apex Retail Intelligence OS API",
        "docs": "/docs"
    }
