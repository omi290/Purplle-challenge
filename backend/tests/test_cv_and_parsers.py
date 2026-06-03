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

def test_pos_importer_success(tmp_path, db):
    csv_file = tmp_path / "test_pos.csv"
    csv_content = (
        "order_id,invoice_number,order_date,order_time,store_id,store_name,city,customer_name,"
        "customer_number,sku,product_name,brand_name,dep_name,sub_category,qty,GMV,NMV,total_amount,"
        "salesperson_name,employee_code\n"
        "ORD1001,INV1001,03-06-2026,10:30:00,ST1008,Brigade_Bangalore,Bangalore,John Doe,"
        "9999999999,SKU101,Lipstick,BrandA,makeup,Lips,2,1000.0,900.0,900.0,Advisor A,EMP101\n"
    )
    csv_file.write_text(csv_content)
    
    res = import_pos_csv(str(csv_file), db)
    assert res["status"] == "success"
    assert res["records_imported"] == 1
    assert res["unique_orders"] == 1
    assert res["total_revenue"] == 900.0

