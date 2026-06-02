import pytest
import datetime
from app.services.event_engine import EventEngine
from app.services.cv_pipeline import TrackedDetection
from app.services.analytics_engine import get_analytics_metrics
from app.services.anomaly_engine import run_anomaly_check
from app.services.revenue_engine import get_revenue_leakage_metrics
from app.services.health_engine import calculate_store_health_score
from app.models.event import Event
from app.models.visitor import Visitor

def test_event_engine_tracking(db):
    engine = EventEngine(db, layout_path="nonexistent.xlsx")
    
    # Simulate track detections
    tracks = [
        TrackedDetection("track_test_1", (0.1, 0.1, 0.1, 0.1), 0.92, 1, 0.1),
        TrackedDetection("track_test_1", (0.25, 0.5, 0.1, 0.1), 0.90, 20, 1.5),
        TrackedDetection("track_test_1", (0.75, 0.85, 0.1, 0.1), 0.88, 50, 45.0)
    ]
    
    res = engine.process_tracks(tracks)
    assert res["events_created"] > 0
    
    # Verify events
    events = db.query(Event).all()
    event_types = [e.event_type for e in events]
    assert "ENTRY" in event_types
    assert "ZONE_ENTER" in event_types

def test_analytics_computation(db):
    engine = EventEngine(db, layout_path="nonexistent.xlsx")
    tracks = [
        TrackedDetection("track_test_1", (0.1, 0.1, 0.1, 0.1), 0.92, 1, 0.1),
        TrackedDetection("track_test_1", (0.85, 0.15, 0.1, 0.1), 0.90, 50, 10.0)
    ]
    engine.process_tracks(tracks)
    
    metrics = get_analytics_metrics(db)
    assert metrics["total_footfall"] == 1
    assert metrics["unique_visitors"] == 1
    assert metrics["average_dwell_time_seconds"] > 0.0

def test_anomaly_engine(db):
    # Running anomaly check on empty/normal data
    new_anom = run_anomaly_check(db)
    assert new_anom == 0
    
    # Generate massive billings to trigger billing queue spike
    engine = EventEngine(db, layout_path="nonexistent.xlsx")
    tracks = []
    # Create 15 distinct visitor tracks in billing area (0.75, 0.85 center)
    for i in range(15):
        tracks.append(TrackedDetection(f"track_anom_{i}", (0.75, 0.85, 0.1, 0.1), 0.91, 10, 1.0))
        
    engine.process_tracks(tracks)
    
    new_anom = run_anomaly_check(db)
    assert new_anom > 0

def test_revenue_leakage_calc(db):
    # Without POS sales
    leakage = get_revenue_leakage_metrics(db)
    assert leakage["leakage_rate"] == 0.0
    assert leakage["estimated_leaked_revenue"] == 0.0

def test_store_health_bounds(db):
    health = calculate_store_health_score(db)
    assert 0.0 <= health["overall_score"] <= 100.0
    assert "grade" in health
