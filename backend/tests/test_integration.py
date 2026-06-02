import pytest
import datetime

def test_full_operational_flow(client):
    today_str = datetime.date.today().isoformat()
    # 1. Ingest customer arrival
    payload_arrival = {
        "events": [
            {
                "event_type": "ENTRY",
                "track_id": "cust_99",
                "zone_name": "Entrance",
                "timestamp": f"{today_str}T10:00:00",
                "confidence": 0.95,
                "bbox_x": 0.1, "bbox_y": 0.1, "bbox_w": 0.1, "bbox_h": 0.2
            }
        ]
    }
    resp1 = client.post("/api/events/ingest", json=payload_arrival)
    assert resp1.status_code == 201

    # 2. Ingest customer browsing makeup
    payload_browse = {
        "events": [
            {
                "event_type": "ZONE_ENTER",
                "track_id": "cust_99",
                "zone_name": "Makeup",
                "timestamp": f"{today_str}T10:02:00",
                "confidence": 0.93,
                "bbox_x": 0.7, "bbox_y": 0.5, "bbox_w": 0.1, "bbox_h": 0.2
            }
        ]
    }
    resp2 = client.post("/api/events/ingest", json=payload_browse)
    assert resp2.status_code == 201

    # 3. Check funnel update
    resp3 = client.get("/api/funnel")
    assert resp3.status_code == 200
    data_funnel = resp3.json()
    assert data_funnel["stages"][0]["count"] == 1  # Entry stage
    assert data_funnel["stages"][1]["count"] == 1  # Browse stage

    # 4. Check consolidated dashboard summary
    resp4 = client.get("/api/dashboard")
    assert resp4.status_code == 200
    data_dash = resp4.json()
    assert data_dash["metrics"]["unique_visitors"] == 1
