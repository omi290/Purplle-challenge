import pytest
import datetime

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "store_health" in data
    assert "overall_score" in data["store_health"]
    assert "revenue_leakage" in data

def test_ingest_events_valid(client):
    payload = {
        "events": [
            {
                "event_type": "ENTRY",
                "track_id": "test_track_1",
                "zone_name": "Entrance",
                "timestamp": datetime.datetime.now().isoformat(),
                "confidence": 0.95,
                "bbox_x": 0.1,
                "bbox_y": 0.1,
                "bbox_w": 0.2,
                "bbox_h": 0.4
            }
        ]
    }
    response = client.post("/api/events/ingest", json=payload)
    assert response.status_code == 201
    assert response.json()["status"] == "success"
    assert response.json()["events_created"] == 1

def test_get_dashboard_summary(client):
    # Pre-populate an event to get positive readings
    payload = {
        "events": [
            {
                "event_type": "ENTRY",
                "track_id": "test_track_1",
                "zone_name": "Entrance",
                "timestamp": datetime.datetime.now().isoformat(),
                "confidence": 0.95,
                "bbox_x": 0.1,
                "bbox_y": 0.1,
                "bbox_w": 0.2,
                "bbox_h": 0.4
            }
        ]
    }
    client.post("/api/events/ingest", json=payload)
    
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "store_health" in data
    assert "revenue_leakage" in data
    assert "recent_anomalies" in data

def test_get_metrics(client):
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_footfall" in data
    assert "unique_visitors" in data
    assert "conversion_rate" in data

def test_get_funnel(client):
    response = client.get("/api/funnel")
    assert response.status_code == 200
    data = response.json()
    assert "stages" in data
    assert len(data["stages"]) == 4

def test_get_heatmap(client):
    response = client.get("/api/heatmap")
    assert response.status_code == 200
    data = response.json()
    assert "zones" in data
    assert len(data["zones"]) > 0

def test_get_anomalies(client, db):
    from app.models.anomaly import Anomaly
    
    # Pre-populate a test anomaly to verify endpoint retrieval structure
    test_anomaly = Anomaly(
        anomaly_type="queue_spike",
        severity="high",
        description="Critical billing queue build-up detected.",
        suggested_action='{"recommendation": "Deploy express checkout counter.", "confidence": 0.92, "reasoning": "Queue length > 8 people", "expected_business_impact": "Reduce abandonment"}'
    )
    db.add(test_anomaly)
    db.commit()

    response = client.get("/api/anomalies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "suggested_action" in data[0]
