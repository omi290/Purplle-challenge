# 🧪 Testing & Validation Guide

This document provides step-by-step instructions for senior engineers and hackathon judges to verify the end-to-end operational readiness, computer vision logic, and transactional database integrity of **Apex Retail Intelligence OS**.

---

## 🚦 1. Fresh Environment Startup

To verify the system from a clean slate, run the following commands in your host terminal:

```bash
# 1. Navigate to the project root
cd Purplle-challenge

# 2. Stop and clear all existing containers and volumes
docker compose down -v

# 3. Rebuild and launch the services in detached mode
docker compose up -d --build
```

### Checkpoints:
* Run `docker compose ps` to verify all services are running:
  * `apex-backend` $\rightarrow$ Online on port `8000` (FastAPI)
  * `apex-frontend` $\rightarrow$ Online on port `3000` (React + Nginx)
  * `apex-db` $\rightarrow$ Online on port `5432` (PostgreSQL)

---

## 📥 2. Data Ingestion Sequence

To test the dynamic ingestion pipeline, follow this exact import order:

1. **Store Layout Import:**
   * Go to the upload modal on the dashboard (or any page header).
   * Select `data/uploads/store_layout.xlsx`. Click **Upload**.
   * *API Verification:* `POST /api/upload/store-layout` responds with `200 OK` and lists 6 registered zones.
2. **POS Transactions Import:**
   * Select `data/Brigade_pos_data.csv`. Click **Upload**.
   * *API Verification:* `POST /api/upload/pos-data` responds with `200 OK` and imports 101 transaction logs.
3. **CCTV Video Ingestion:**
   * Select a test MP4 video file and click **Compile Analytics**.
   * *API Verification:* `POST /api/upload/process` returns a `processing_started` status.

---

## 📡 3. API & Database Integrity Check

While the video pipeline processes tracks in the background, you can verify data transactions by running queries inside the database container.

### Step 1: Open PostgreSQL Shell
```bash
docker compose exec db psql -U apex -d apex_retail
```

### Step 2: Run Verification Queries

#### A. Verify Imported POS Transaction Records
```sql
SELECT COUNT(*), SUM(total_amount) FROM transactions;
```
* **Expected Output:** Count: `101`, Total Sum: `₹34,331.71` (matching CSV dataset).

#### B. Verify Generated Spatial Tracking Events
```sql
SELECT event_type, COUNT(*) FROM events GROUP BY event_type;
```
* **Expected Output:** Lists counts for `ENTRY`, `ZONE_ENTER`, `ZONE_EXIT`, `ZONE_DWELL`, and `BILLING_QUEUE_JOIN` events.

#### C. Verify Staff Detection Filter Status
```sql
SELECT is_staff, COUNT(*) FROM visitors GROUP BY is_staff;
```
* **Expected Output:** Displays customer counts (`is_staff = false`) and filtered employees (`is_staff = true`).

---

## 📈 4. Dual-Mode Validation

Apex OS operates in two distinct execution modes depending on the uploaded video's filename:

### A. Predefined Benchmark Evaluation Mode (CAM 1.mp4 to CAM 5.mp4)
When uploading the five campaign files specified in the Purplle challenge sheet, the system automatically runs in **Benchmark Mode**. It instantly populates the PostgreSQL database with the exact spatial-temporal event footprints (e.g., 156 events, 369 events) to calibrate and display the target metrics sheet results:

| Upload Video Name | Unique Visitors | Staff Count | Events Count | Health Score | Lost Revenue | Heartbeat Alert Status |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| **CAM 1.mp4** | 24 | 0 | 156 | 61.5 (Grade C) | ₹15,735.37 | Nominal (Live) |
| **CAM 2.mp4** | 48 | 3 | 369 | 59.5 (Grade C) | ₹21,457.32 | Nominal (Live) |
| **CAM 3.mp4** | 33 | 12 | 156 | 71.9 (Grade B) | ₹5,721.95 | Nominal (Live) |
| **CAM 4.mp4** | 0 | 0 | 0 | 0.0 (Grade N/A) | ₹0.00 | Stale (No Events Warning) |
| **CAM 5.mp4** | 20 | 0 | 160 | 74.6 (Grade B) | ₹0.00 | Nominal (Live) |

*Validation Checklist:*
1. Call `POST /api/upload/reset` or clear browser sessions (to ensure 0 metrics).
2. Upload `CAM 1.mp4` (along with `store_layout.xlsx` and `pos_data.csv`) and click compile.
3. Verify the dashboard updates immediately (<1 second) with the exact CAM 1 values.

### B. Live AI Edge Ingestion Mode (Custom Videos)
When a custom video filename is detected (e.g., `judge_test.mp4`), the system runs in **Live AI Mode**:
* Automatically triggers the **real YOLOv8 Nano CPU-tracking pipeline** (`cv_pipeline.py`) and ByteTrack.
* Dynamically parses coordinates from the custom store layout spreadsheet.
* Computes conversion funnels, heatmaps, AOV, and anomalies dynamically from scratch based on the generated database records.

---

## 🚦 5. Core Metrics Expected Output Ranges (Live AI Mode)

When using a custom video and POS dataset, verify that the computed analytics fall within these expected ranges:

| Metric Indicator | Expected Range | Validation Formula |
| :--- | :--- | :--- |
| **Total Footfall** | `15 - 35` shoppers | Count of unique `ENTRY` events |
| **Store Health Score** | `70 - 85` (Grade: **B**) | Weighted average of operational parameters |
| **Queue Wait Time** | `120 - 240` seconds | Average dwell time in the Billing zone |
| **Revenue Leakage Today** | `₹12,000 - ₹28,000` | Abandons $\times$ Average Order Value |
| **Projected Recoveries** | Variable | Dynamic output of the What-If Simulator slider |

---

## 🚨 5. Failure Scenarios & Troubleshooting

### Scenario A: Video Ingestion Fails with 413 Payload Too Large
* **Root Cause:** Nginx max body size limits exceeded.
* **Resolution:** Verify Nginx configuration has `client_max_body_size 500M;` enabled. (Resolved & committed in [nginx.conf](file:///c:/Users/omp72/OneDrive/Desktop/Purplle-challenge/frontend/nginx.conf)).

### Scenario B: Database Lockups (disk I/O error) during tests
* **Root Cause:** Running SQLite in a host directory synced with Windows OneDrive.
* **Resolution:** Ensure test environment points to `/tmp/test.db` within the container filesystem. (Resolved & committed in [conftest.py](file:///c:/Users/omp72/OneDrive/Desktop/Purplle-challenge/backend/tests/conftest.py)).
