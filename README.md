# 🔮 Apex Retail Intelligence OS

> Convert CCTV footage into actionable retail intelligence. Powered by YOLOv8, ByteTrack, and AI-driven analytics.

![Architecture](https://img.shields.io/badge/Architecture-Monolith-blue)
![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)
![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791)
![CV](https://img.shields.io/badge/CV-YOLOv8%20%2B%20ByteTrack-FF6F00)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Data Sources](#data-sources)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

Apex Retail Intelligence OS is a comprehensive retail analytics platform that transforms CCTV camera feeds into business intelligence. The system detects, tracks, and analyzes customer movement through a retail store, generating real-time events and actionable insights.

### What It Does

1. **Ingests CCTV footage** and processes it through a YOLOv8 + ByteTrack computer vision pipeline
2. **Detects and tracks** individual visitors as they move through the store
3. **Classifies events** — entry, exit, zone browsing, queue joining, billing, and re-entry
4. **Correlates with POS data** to measure conversion, revenue leakage, and opportunity loss
5. **Generates anomalies** and AI-powered suggested actions
6. **Presents insights** through a premium real-time dashboard

---

## ✨ Features

### Core Analytics
| Feature | Description |
|---------|-------------|
| **Footfall Counter** | Total and unique visitor counting with confidence scores |
| **Conversion Funnel** | Entry → Browse → Queue → Purchase with drop-off analysis |
| **Zone Heatmap** | Traffic density visualization across store zones |
| **Dwell Time Analysis** | Per-zone and overall customer engagement metrics |
| **Peak Hour Analysis** | Hourly traffic distribution and trend identification |

### Differentiator Features
| Feature | Description |
|---------|-------------|
| 🏥 **Store Health Score** | Composite 0-100 score from conversion, dwell, queue efficiency, utilization, and anomaly rates |
| 💰 **Revenue Leakage Meter** | Identifies visitors who reached billing but had no POS transaction |
| 📉 **Opportunity Loss Tracker** | Estimates missed revenue from unconverted visitors |
| 🎯 **Confidence-Aware Analytics** | Every metric includes a detection confidence score |
| 👥 **Staff Detection Layer** | Separates staff from customers using color-based uniform detection |
| 🤖 **AI Suggested Actions** | Context-aware recommendations for each detected anomaly |
| 📊 **Live Dashboard** | Auto-refreshing premium dashboard with real-time updates |

### Computer Vision
- **Detection**: YOLOv8 nano model (fast inference)
- **Tracking**: ByteTrack multi-object tracker via Supervision library
- **Staff Detection**: Color-based HSV uniform detection (primary), CLIP zero-shot classification (optional)

### Event Types
| Event | Trigger |
|-------|---------|
| `ENTRY` | Person crosses store entrance boundary |
| `EXIT` | Person crosses store exit boundary |
| `ZONE_ENTER` | Person enters a defined store zone |
| `ZONE_EXIT` | Person exits a defined store zone |
| `ZONE_DWELL` | Person stays in a zone beyond threshold (30s) |
| `BILLING_QUEUE_JOIN` | Person enters billing/checkout zone |
| `BILLING_QUEUE_ABANDON` | Person leaves billing zone without purchase |
| `REENTRY` | Previously exited person re-enters the store |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Docker Compose                         │
│                                                          │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │ Frontend │    │   Backend    │    │  PostgreSQL  │   │
│  │  React   │───▶│   FastAPI    │───▶│    16-alpine │   │
│  │  :3000   │    │    :8000     │    │     :5432    │   │
│  └──────────┘    └──────┬───────┘    └──────────────┘   │
│                         │                                │
│                  ┌──────┴───────┐                        │
│                  │  CV Pipeline │                        │
│                  │  YOLOv8 +    │                        │
│                  │  ByteTrack   │                        │
│                  └──────────────┘                        │
└──────────────────────────────────────────────────────────┘
```

### Backend Services
- **CV Pipeline**: YOLOv8 detection + ByteTrack tracking
- **Event Engine**: Movement-to-event classification
- **Analytics Engine**: Metric computation with caching
- **Anomaly Engine**: Z-score based anomaly detection
- **Revenue Engine**: POS correlation and leakage detection
- **Health Engine**: Composite store health scoring
- **Staff Detection**: Uniform-based staff filtering
- **Recommendation Engine**: Rule-based AI suggestions

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed
- At least 4GB free RAM (for CV model)
- CCTV footage file (MP4), Store Layout (XLSX), POS Data (CSV)

### One-Command Start

```bash
# Clone and navigate to the project
cd Purplle-challenge

# Create data directory and copy input files
mkdir -p data/videos data/uploads
# Copy your CCTV video to data/videos/
# Copy your Store Layout XLSX and POS CSV to data/uploads/

# Start everything
docker compose up --build
```

### Access Points
| Service | URL |
|---------|-----|
| **Dashboard** | http://localhost:3000 |
| **API Docs (Swagger)** | http://localhost:8000/docs |
| **API Docs (ReDoc)** | http://localhost:8000/redoc |
| **Health Check** | http://localhost:8000/health |

### Upload Data via API

```bash
# Upload store layout
curl -X POST http://localhost:8000/api/upload/store-layout \
  -F "file=@Brigade Road - Store layoutc5f5d56.xlsx"

# Upload POS data
curl -X POST http://localhost:8000/api/upload/pos-data \
  -F "file=@Brigade_Bangalore_10_April_26 (1)bc6219c.csv"

# Upload and process video
curl -X POST http://localhost:8000/api/upload/video \
  -F "file=@cctv_footage.mp4"

# Trigger full processing pipeline
curl -X POST http://localhost:8000/api/upload/process
```

---

## 📁 Project Structure

```
Purplle-challenge/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │       └── 001_initial_schema.py
│   ├── app/
│   │   ├── main.py                     # FastAPI entry point
│   │   ├── config.py                   # Environment configuration
│   │   ├── database.py                 # SQLAlchemy setup
│   │   ├── middleware.py               # Trace ID middleware
│   │   ├── logging_config.py           # Structured logging
│   │   ├── models/                     # SQLAlchemy models
│   │   │   ├── visitor.py
│   │   │   ├── session.py
│   │   │   ├── event.py
│   │   │   ├── transaction.py
│   │   │   ├── anomaly.py
│   │   │   └── metrics_cache.py
│   │   ├── schemas/                    # Pydantic schemas
│   │   ├── api/                        # API route handlers
│   │   │   ├── events.py               # POST /events/ingest
│   │   │   ├── metrics.py              # GET /metrics
│   │   │   ├── funnel.py               # GET /funnel
│   │   │   ├── heatmap.py              # GET /heatmap
│   │   │   ├── anomalies.py            # GET /anomalies
│   │   │   ├── health.py               # GET /health
│   │   │   ├── upload.py               # File upload endpoints
│   │   │   └── dashboard.py            # Aggregate dashboard
│   │   ├── services/                   # Business logic
│   │   │   ├── cv_pipeline.py          # YOLOv8 + ByteTrack
│   │   │   ├── event_engine.py         # Event classification
│   │   │   ├── analytics_engine.py     # Metrics computation
│   │   │   ├── anomaly_engine.py       # Anomaly detection
│   │   │   ├── revenue_engine.py       # Revenue leakage
│   │   │   ├── health_engine.py        # Store health score
│   │   │   ├── staff_detection.py      # Staff vs customer
│   │   │   ├── recommendation_engine.py # AI suggestions
│   │   │   ├── store_layout_parser.py  # XLSX parser
│   │   │   ├── pos_importer.py         # CSV importer
│   │   │   └── opportunity_tracker.py  # Opportunity loss
│   │   └── utils/
│   │       └── helpers.py
│   └── tests/                          # Test suite
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── App.jsx
│       ├── index.css
│       ├── api/client.js
│       ├── components/                 # Reusable UI components
│       └── pages/                      # Page components
├── docker-compose.yml
├── .env.example
├── README.md
├── DESIGN.md
├── CHOICES.md
└── API_DOCUMENTATION.md
```

---

## 📡 API Documentation

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for full API reference.

### Quick Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/events/ingest` | Ingest tracking events |
| `GET` | `/api/metrics` | Get computed metrics |
| `GET` | `/api/funnel` | Get conversion funnel data |
| `GET` | `/api/heatmap` | Get zone heatmap data |
| `GET` | `/api/anomalies` | Get detected anomalies |
| `GET` | `/api/health` | System + store health |
| `GET` | `/api/dashboard` | Aggregated dashboard data |
| `POST` | `/api/upload/video` | Upload CCTV footage |
| `POST` | `/api/upload/store-layout` | Upload store layout |
| `POST` | `/api/upload/pos-data` | Upload POS CSV |
| `POST` | `/api/upload/process` | Trigger CV pipeline |

---

## 📊 Data Sources

### 1. CCTV Video
- Format: MP4, AVI, or other OpenCV-compatible formats
- Resolution: Any (YOLOv8 handles resizing)
- The system processes at configurable FPS skip rate (default: every 5th frame)

### 2. Store Layout (XLSX)
- Defines store zones: entrance, exit, billing, browse areas
- Parsed automatically using openpyxl
- Falls back to default zone layout if format is unrecognized

### 3. POS Data (CSV)
- Purplle store POS export format
- 38 columns including order_id, timestamps, products, amounts
- Date format: DD-MM-YYYY
- Automatically imported and correlated with visitor sessions

---

## 🧪 Testing

```bash
# Run all tests
cd backend
pip install -r requirements.txt
pytest tests/ -v --tb=short

# Run with coverage report
pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# Run specific test modules
pytest tests/test_api_events.py -v
pytest tests/test_analytics_engine.py -v
```

### Test Coverage Target: >70%

---

## 🔧 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `docker compose up` fails with port conflict | Change ports in docker-compose.yml (e.g., 8001:8000) |
| Database connection refused | Wait for PostgreSQL health check to pass; check `docker logs apex-db` |
| YOLO model download fails | Ensure internet connectivity; model downloads on first build |
| Frontend shows no data | Dashboard uses demo data by default; upload real data via API |
| Out of memory during CV processing | Increase Docker memory limit or reduce video resolution |
| Permission denied on data directory | Run `chmod -R 777 data/` or adjust volume permissions |

### Reset Everything

```bash
docker compose down -v  # Remove containers and volumes
docker compose up --build  # Fresh start
```

### View Logs

```bash
docker logs apex-backend -f   # Backend logs
docker logs apex-frontend -f  # Frontend logs
docker logs apex-db -f        # Database logs
```

---

## 📄 License

This project was built for the Purplle Retail Intelligence Challenge.

---

*Built with ❤️ by the Apex Team*
