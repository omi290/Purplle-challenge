import urllib.request
import json
import sys

base_url = "http://localhost:8000/api"

def test_endpoint(name, method, path, data=None):
    print(f"=== TESTING {name} ({method} {path}) ===")
    url = f"{base_url}{path}"
    try:
        req = urllib.request.Request(
            url, 
            data=json.dumps(data).encode("utf-8") if data else None,
            headers={"Content-Type": "application/json"} if data else {},
            method=method
        )
        with urllib.request.urlopen(req) as res:
            status_code = res.status
            body = json.loads(res.read().decode("utf-8"))
            print(f"Status Code: {status_code}")
            print(f"Response: {json.dumps(body, indent=2)}")
    except urllib.error.HTTPError as e:
        print(f"Status Code: {e.code}")
        try:
            err_body = json.loads(e.read().decode("utf-8"))
            print(f"Response: {json.dumps(err_body, indent=2)}")
        except Exception:
            print(f"Response (raw): {e.reason}")
    except Exception as e:
        print(f"Error: {e}")
    print("\n")

# 1. POST /events/ingest
ingest_payload = {
    "events": [
        {
            "event_type": "ENTRY",
            "track_id": "verify_test_99",
            "zone_name": "Entrance",
            "timestamp": "2026-06-02T10:00:00",
            "confidence": 0.98,
            "bbox_x": 0.1, "bbox_y": 0.1, "bbox_w": 0.1, "bbox_h": 0.2
        }
    ]
}
test_endpoint("POST /events/ingest", "POST", "/events/ingest", ingest_payload)

# 2. GET /metrics
test_endpoint("GET /metrics", "GET", "/metrics")

# 3. GET /funnel
test_endpoint("GET /funnel", "GET", "/funnel")

# 4. GET /heatmap
test_endpoint("GET /heatmap", "GET", "/heatmap")

# 5. GET /anomalies
test_endpoint("GET /anomalies", "GET", "/anomalies")

# 6. GET /health
test_endpoint("GET /health", "GET", "/health")
