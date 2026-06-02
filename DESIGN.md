# 🏗️ DESIGN.md — Apex Retail Intelligence OS

## System Architecture

### High-Level Design

Apex Retail Intelligence OS follows a **monolithic architecture** with clear internal boundaries. All backend services run within a single FastAPI application, communicating through direct function calls rather than network protocols.

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              React SPA (Vite + Tailwind)                 │    │
│  │  Dashboard │ Funnel │ Heatmap │ Analytics │ AI │ Health  │    │
│  └──────────────────────┬──────────────────────────────────┘    │
└─────────────────────────┼───────────────────────────────────────┘
                          │ HTTP/REST (JSON)
┌─────────────────────────┼───────────────────────────────────────┐
│                    API Gateway Layer                              │
│  ┌──────────────────────┴──────────────────────────────────┐    │
│  │                    FastAPI Router                         │    │
│  │  /events │ /metrics │ /funnel │ /heatmap │ /anomalies   │    │
│  │  /health │ /upload  │ /dashboard                         │    │
│  └──────────────────────┬──────────────────────────────────┘    │
│                          │                                       │
│                    Service Layer                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐       │
│  │    CV    │ │  Event   │ │Analytics │ │   Anomaly    │       │
│  │ Pipeline │ │  Engine  │ │  Engine  │ │   Engine     │       │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘       │
│       │             │            │               │               │
│  ┌────┴─────┐ ┌─────┴────┐ ┌────┴─────┐ ┌──────┴───────┐       │
│  │  Staff   │ │ Revenue  │ │  Health  │ │Recommendation│       │
│  │Detection │ │  Engine  │ │  Engine  │ │   Engine     │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘       │
│                          │                                       │
│                    Data Layer                                     │
│  ┌──────────────────────┴──────────────────────────────────┐    │
│  │                 SQLAlchemy ORM + Alembic                  │    │
│  │  visitors │ sessions │ events │ transactions │ anomalies │    │
│  └──────────────────────┬──────────────────────────────────┘    │
└─────────────────────────┼───────────────────────────────────────┘
                          │
              ┌───────────┴───────────┐
              │     PostgreSQL 16     │
              └───────────────────────┘
```

---

## Data Flow

### 1. Video Processing Pipeline

```
CCTV Video File
       │
       ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   YOLOv8     │────▶│  ByteTrack   │────▶│    Staff     │
│  Detection   │     │   Tracking   │     │   Filter     │
│  (persons)   │     │  (track IDs) │     │ (remove staff)│
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                                  ▼
                                          ┌──────────────┐
                                          │    Event     │
                                          │   Engine     │
                                          │ (classify    │
                                          │  movements)  │
                                          └──────┬───────┘
                                                  │
                    ┌─────────────┬────────────────┼─────────────┐
                    ▼             ▼                ▼             ▼
             ┌──────────┐ ┌──────────┐   ┌──────────┐   ┌──────────┐
             │Analytics │ │ Anomaly  │   │ Revenue  │   │  Health  │
             │ Engine   │ │ Engine   │   │ Engine   │   │  Score   │
             └──────────┘ └──────────┘   └──────────┘   └──────────┘
```

### 2. Event Classification Logic

```
Track Detection at frame N
       │
       ├─── Near entrance boundary? ─── YES ──▶ ENTRY event
       │
       ├─── Near exit boundary? ─── YES ──▶ EXIT event
       │
       ├─── Crossed zone boundary (in)? ─── YES ──▶ ZONE_ENTER event
       │
       ├─── Crossed zone boundary (out)? ─── YES ──▶ ZONE_EXIT event
       │
       ├─── In zone > dwell threshold? ─── YES ──▶ ZONE_DWELL event
       │
       ├─── Entered billing zone? ─── YES ──▶ BILLING_QUEUE_JOIN event
       │
       ├─── Left billing without txn? ─── YES ──▶ BILLING_QUEUE_ABANDON event
       │
       └─── Previously exited track? ─── YES ──▶ REENTRY event
```

---

## Database Schema Design

### Entity Relationship Diagram

```
┌──────────┐       ┌──────────┐       ┌──────────┐
│ visitors │──1:N──│ sessions │──1:N──│  events  │
│          │       │          │       │          │
│ track_id │       │ entry_at │       │ type     │
│ is_staff │       │ exit_at  │       │ zone     │
│ first_seen│      │ duration │       │ timestamp│
│ last_seen│       │ is_reentry│      │ confidence│
└──────────┘       └──────────┘       └──────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ transactions │    │  anomalies   │    │ metrics_cache│
│              │    │              │    │              │
│ order_id     │    │ type         │    │ metric_name  │
│ amount       │    │ severity     │    │ metric_value │
│ products     │    │ suggested_   │    │ period       │
│ timestamp    │    │   action     │    │ computed_at  │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Indexing Strategy

| Table | Index | Rationale |
|-------|-------|-----------|
| `visitors` | `track_id` | Fast lookup by tracking ID |
| `visitors` | `first_seen` | Time-range queries |
| `sessions` | `visitor_id` | Join with visitors |
| `sessions` | `entry_time` | Time-range queries |
| `events` | `event_type` | Filter by event type |
| `events` | `timestamp` | Time-series queries |
| `events` | `zone_name` | Zone-level analytics |
| `transactions` | `order_id` | Order lookup |
| `transactions` | `order_date` | Date range filtering |
| `anomalies` | `anomaly_type` | Filter anomalies |
| `anomalies` | `detected_at` | Timeline queries |
| `metrics_cache` | `(metric_name, period_start)` | Cache lookup (unique) |

---

## Store Health Score Formula

```
Health Score = Σ (component_score × weight)

Components:
┌───────────────────────┬────────┬──────────────────────────────┐
│ Component             │ Weight │ Calculation                  │
├───────────────────────┼────────┼──────────────────────────────┤
│ Conversion Rate       │  0.25  │ actual / target × 100        │
│ Dwell Quality         │  0.20  │ 100 - |actual - optimal|/opt │
│ Queue Efficiency      │  0.20  │ 100 - (wait_time + abandon%) │
│ Zone Utilization      │  0.15  │ evenness of distribution      │
│ Anomaly Rate          │  0.10  │ 100 - (anomalies / expected) │
│ Revenue Efficiency    │  0.10  │ revenue_per_visitor / target  │
└───────────────────────┴────────┴──────────────────────────────┘

Final Score = clamp(weighted_sum, 0, 100)
```

---

## Anomaly Detection

### Statistical Method

We use **z-score based anomaly detection** with rolling window statistics:

```python
z_score = (current_value - rolling_mean) / rolling_std

if abs(z_score) > threshold:
    anomaly_detected = True
```

### Thresholds by Type

| Anomaly Type | Z-Score Threshold | Severity Mapping |
|-------------|-------------------|------------------|
| Queue Spike | > 2.0 | medium (2-3), high (>3) |
| Conversion Drop | < -1.5 | medium (-1.5 to -2.5), high (<-2.5) |
| Unusual Dwell | > 3.0 | low (3-4), medium (>4) |
| Low Footfall | < -2.0 | medium (-2 to -3), high (<-3) |
| High Abandonment | > 2.0 | high (>2), critical (>3) |

### AI Suggestion Generation

Each anomaly type maps to contextual recommendations:

```
queue_spike → "Open additional billing counter"
conversion_drop → "Review queue congestion and staffing"  
unusual_dwell → "Check for customer confusion in {zone}"
low_footfall → "Increase storefront promotion"
high_abandonment → "Deploy additional staff to billing"
revenue_leakage → "Cross-reference billing visitors with POS"
```

---

## Frontend Architecture

### Component Hierarchy

```
App
├── Layout
│   ├── Sidebar (navigation)
│   ├── Header (title, live indicator, actions)
│   └── Page Content
│       ├── Dashboard
│       │   ├── MetricCard × 4
│       │   ├── StoreHealthScore
│       │   ├── RevenueLeakageMeter
│       │   ├── OpportunityLossCard
│       │   ├── HourlyTrendChart
│       │   └── AnomalyTable (mini)
│       ├── Funnel
│       │   ├── FunnelChart
│       │   └── StageBreakdown
│       ├── Heatmap
│       │   └── HeatmapGrid
│       ├── Analytics
│       │   ├── BarChart (footfall)
│       │   ├── PieChart (zones)
│       │   └── LineChart (trends)
│       ├── AIInsights
│       │   ├── AIInsightCard × N
│       │   └── AnomalyTimeline
│       └── HealthMonitoring
│           ├── StoreHealthScore (large)
│           ├── ComponentCards
│           └── HealthTrend
```

### State Management

Simple React state with `useState` and `useEffect`:
- Each page fetches its own data on mount
- Auto-refresh with `setInterval` (30 seconds)
- Error fallback to comprehensive demo data
- No external state library needed (KISS principle)

### Design System

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-primary` | `#0f172a` | Main background |
| `--bg-secondary` | `#1e293b` | Card backgrounds |
| `--accent-purple` | `#8b5cf6` | Primary accent |
| `--accent-cyan` | `#06b6d4` | Secondary accent |
| `--accent-emerald` | `#10b981` | Success/positive |
| `--glass-bg` | `rgba(30,41,59,0.7)` | Glassmorphism |
| `--glass-border` | `rgba(148,163,184,0.1)` | Card borders |

---

## Security Considerations

### Current Implementation (Hackathon Scope)
- CORS allows all origins (configurable)
- No authentication (demo mode)
- SQL injection prevented by SQLAlchemy ORM
- File upload size limits enforced
- Trace ID for request tracking

### Production Recommendations
- Add JWT authentication
- Implement rate limiting
- Restrict CORS origins
- Add input sanitization for file uploads
- Enable HTTPS with TLS certificates
- Add database connection pooling limits
- Implement audit logging

---

## Performance Considerations

### Video Processing
- YOLOv8 nano model chosen for speed over accuracy
- Frame skip (default: 5) reduces processing load by 80%
- Processing is synchronous but could be backgrounded

### Database
- Metrics caching prevents repeated computation
- Strategic indexes on time-series and filter columns
- Batch inserts for event data

### Frontend
- Demo data fallback eliminates API dependency for demos
- Lazy loading for chart components
- Auto-refresh interval configurable
