import pytest
import os
from app.services.cv_pipeline import process_video_file, run_simulated_pipeline
from app.services.store_layout_parser import parse_store_layout, get_default_zones
from app.services.pos_importer import import_pos_csv

def test_store_layout_parser_fallback():
    # File doesn't exist, should return default zones
    zones = parse_store_layout("nonexistent.xlsx")
    assert len(zones) > 0
    assert zones[0].name == "Entrance"
    assert zones[0].zone_type == "entrance"

def test_cv_pipeline_simulation():
    # If video path doesn't exist, process_video_file falls back to simulation mode
    detections = process_video_file("nonexistent.mp4")
    assert len(detections) > 0
    assert detections[0].track_id is not None
    assert len(detections[0].bbox) == 4

def test_pos_importer_missing_file(db):
    res = import_pos_csv("nonexistent.csv", db)
    assert res["status"] == "error"
