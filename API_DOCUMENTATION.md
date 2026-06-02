# 📡 API Documentation — Apex Retail Intelligence OS

**Base URL**: `http://localhost:8000/api`  
**API Documentation UI**: `http://localhost:8000/docs` (Swagger) | `http://localhost:8000/redoc` (ReDoc)

---

## Authentication

No authentication required (demo mode). All endpoints are publicly accessible.

---

## Common Headers

| Header | Value | Description |
|--------|-------|-------------|
| `Content-Type` | `application/json` | Request body format |
| `X-Trace-ID` | `uuid` | Auto-generated request trace ID (returned in response) |

---

## Endpoints

### 1. POST /api/events/ingest

Ingest tracking events from the CV pipeline or external sources.

**Request Body**:
```json
{
  "events": [
    {
      "event_type": "ENTRY",
      "track_id": "track_001",
      "zone_name": "entrance",
      "timestamp": "2026-04-10T10:30:00Z",
      "confidence": 0.92,
      "bbox_x": 120.5,
      "bbox_y": 200.3,
      "bbox_w": 45.0,
      "bbox_h": 120.0,
      "frame_number": 1500
    }
  ]
}
```

**Event Types** (enum):
- `ENTRY` — Person enters the store
- `EXIT` — Person exits the store
- `ZONE_ENTER` — Person enters a store zone
- `ZONE_EXIT` — Person exits a store zone
- `ZONE_DWELL` — Person stays in zone beyond threshold
- `BILLING_QUEUE_JOIN` — Person enters billing queue
- `BILLING_QUEUE_ABANDON` — Person leaves billing queue without purchase
- `REENTRY` — Previously exited person re-enters

**Response** (201 Created):
```json
{
  "status": "success",
  "events_created": 1,
  "event_ids": [42]
}
```

**Errors**:
| Code | Description |
|------|-------------|
| 400 | Invalid event_type or missing required fields |
| 422 | Validation error (Pydantic) |

---

### 2. GET /api/metrics

Get computed retail metrics for a time period.

**Query Parameters**:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `start_date` | `date` (YYYY-MM-DD) | Today | Period start |
| `end_date` | `date` (YYYY-MM-DD) | Today | Period end |

**Response** (200 OK):
```json
{
  "total_footfall": 847,
  "unique_visitors": 623,
  "conversion_rate": 0.34,
  "average_dwell_time_seconds": 482.5,
  "revenue_per_visitor": 245.80,
  "bounce_rate": 0.12,
  "peak_hours": [
    {"hour": 14, "count": 89},
    {"hour": 15, "count": 95},
    {"hour": 16, "count": 78}
  ],
  "zone_metrics": [
    {
      "zone_name": "Skincare",
      "visitor_count": 312,
      "avg_dwell_seconds": 180.5
    }
  ],
  "staff_count": 5,
  "customer_count": 618,
  "confidence": 0.87,
  "period": {
    "start": "2026-04-10",
    "end": "2026-04-10"
  }
}
```

---

### 3. GET /api/funnel

Get conversion funnel data.

**Query Parameters**:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `start_date` | `date` | Today | Period start |
| `end_date` | `date` | Today | Period end |

**Response** (200 OK):
```json
{
  "stages": [
    {
      "name": "Entry",
      "count": 623,
      "percentage": 100.0
    },
    {
      "name": "Browse",
      "count": 548,
      "percentage": 87.96,
      "drop_off": 12.04
    },
    {
      "name": "Billing Queue",
      "count": 245,
      "percentage": 39.33,
      "drop_off": 48.63
    },
    {
      "name": "Purchase",
      "count": 212,
      "percentage": 34.03,
      "drop_off": 5.30
    }
  ],
  "overall_conversion": 0.34,
  "confidence": 0.85
}
```

---

### 4. GET /api/heatmap

Get zone-based traffic heatmap data.

**Query Parameters**:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `start_date` | `date` | Today | Period start |
| `end_date` | `date` | Today | Period end |

**Response** (200 OK):
```json
{
  "zones": [
    {
      "zone_name": "Entrance",
      "zone_type": "entrance",
      "visitor_count": 623,
      "avg_dwell_seconds": 15.2,
      "intensity": 1.0,
      "coordinates": {
        "x1": 0.0, "y1": 0.0,
        "x2": 0.2, "y2": 0.3
      }
    },
    {
      "zone_name": "Skincare",
      "zone_type": "browse",
      "visitor_count": 312,
      "avg_dwell_seconds": 180.5,
      "intensity": 0.72,
      "coordinates": {
        "x1": 0.2, "y1": 0.0,
        "x2": 0.5, "y2": 0.5
      }
    }
  ],
  "max_visitors": 623,
  "total_zones": 6
}
```

---

### 5. GET /api/anomalies

Get detected anomalies with AI-suggested actions.

**Query Parameters**:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `severity` | `string` | all | Filter: low, medium, high, critical |
| `anomaly_type` | `string` | all | Filter by type |
| `limit` | `int` | 50 | Max results |
| `offset` | `int` | 0 | Pagination offset |

**Response** (200 OK):
```json
{
  "anomalies": [
    {
      "id": 1,
      "anomaly_type": "queue_spike",
      "severity": "high",
      "description": "Billing queue length exceeded 2 standard deviations at 15:30",
      "suggested_action": "Open additional billing counter. Current queue exceeds optimal threshold.",
      "detected_at": "2026-04-10T15:30:00Z",
      "confidence": 0.91,
      "metric_value": 12.0,
      "threshold_value": 6.5,
      "zone_name": "Billing",
      "resolved": false
    }
  ],
  "total": 8,
  "limit": 50,
  "offset": 0
}
```

---

### 6. GET /api/health

System health check and store health score.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "database": "connected",
  "last_event_time": "2026-04-10T16:55:36Z",
  "total_events": 4523,
  "store_health": {
    "overall_score": 73.5,
    "grade": "B",
    "components": {
      "conversion_rate": {"score": 68.0, "weight": 0.25},
      "dwell_quality": {"score": 82.0, "weight": 0.20},
      "queue_efficiency": {"score": 65.0, "weight": 0.20},
      "zone_utilization": {"score": 78.0, "weight": 0.15},
      "anomaly_rate": {"score": 85.0, "weight": 0.10},
      "revenue_efficiency": {"score": 71.0, "weight": 0.10}
    }
  },
  "revenue_leakage": {
    "leakage_rate": 0.08,
    "estimated_leaked_revenue": 12450.00,
    "potential_total_revenue": 155625.00
  },
  "opportunity_loss": {
    "total_opportunities_lost": 156,
    "estimated_revenue_impact": 38220.00,
    "top_reasons": [
      "High bounce rate in Makeup zone",
      "Queue abandonment during peak hours"
    ]
  }
}
```

---

### 7. GET /api/dashboard

Aggregated dashboard data (single API call for all dashboard widgets).

**Response** (200 OK):
```json
{
  "metrics": {
    "total_footfall": 847,
    "unique_visitors": 623,
    "conversion_rate": 0.34,
    "average_dwell_time": 482.5,
    "revenue_per_visitor": 245.80
  },
  "store_health": {
    "overall_score": 73.5,
    "grade": "B",
    "components": {}
  },
  "revenue_leakage": {
    "leakage_rate": 0.08,
    "estimated_leaked_revenue": 12450.00
  },
  "opportunity_loss": {
    "total_lost": 156,
    "revenue_impact": 38220.00
  },
  "recent_anomalies": [],
  "ai_suggestions": [],
  "funnel_summary": {},
  "zone_heatmap": [],
  "staff_count": 5,
  "hourly_trend": []
}
```

---

### 8. POST /api/upload/video

Upload CCTV footage for processing.

**Request**: `multipart/form-data`
| Field | Type | Description |
|-------|------|-------------|
| `file` | `file` | Video file (MP4, AVI) |

**Response** (200 OK):
```json
{
  "status": "uploaded",
  "filename": "cctv_footage.mp4",
  "size_bytes": 680011561,
  "path": "/data/videos/cctv_footage.mp4"
}
```

---

### 9. POST /api/upload/store-layout

Upload store layout XLSX file.

**Request**: `multipart/form-data`
| Field | Type | Description |
|-------|------|-------------|
| `file` | `file` | XLSX file |

**Response** (200 OK):
```json
{
  "status": "parsed",
  "zones_found": 6,
  "zones": ["Entrance", "Skincare", "Makeup", "Hair Care", "Fragrance", "Billing"]
}
```

---

### 10. POST /api/upload/pos-data

Upload POS transaction CSV.

**Request**: `multipart/form-data`
| Field | Type | Description |
|-------|------|-------------|
| `file` | `file` | CSV file |

**Response** (200 OK):
```json
{
  "status": "imported",
  "total_rows": 102,
  "unique_orders": 20,
  "total_revenue": 28456.78,
  "date_range": {"start": "2026-04-10", "end": "2026-04-10"}
}
```

---

### 11. POST /api/upload/process

Trigger the full CV pipeline processing.

**Response** (200 OK):
```json
{
  "status": "processing_started",
  "video_file": "cctv_footage.mp4",
  "estimated_frames": 45000,
  "fps_skip": 5,
  "frames_to_process": 9000
}
```

---

## Error Responses

All errors follow a consistent format:

```json
{
  "detail": "Error description",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created (event ingestion) |
| 400 | Bad Request (invalid input) |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

---

## Rate Limits

No rate limits in demo mode. For production, recommended limits:
- `/events/ingest`: 1000 req/min
- `/metrics`, `/funnel`, `/heatmap`: 100 req/min
- `/upload/*`: 10 req/min
- `/health`: Unlimited
