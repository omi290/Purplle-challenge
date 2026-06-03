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

## 📈 4. Core Metrics Expected Output Ranges

When using the sample dataset, verify that the computed analytics fall within these expected ranges:

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
