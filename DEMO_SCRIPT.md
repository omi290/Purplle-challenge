# 🎙️ DEMO_SCRIPT.md — Presentation Playbooks

> This document contains step-by-step scripts designed to maximize judge confidence in **Apex Retail Intelligence OS** during hackathon evaluations. It provides playbooks for **5-minute**, **10-minute**, and **15-minute** durations.

---

## 🎯 Core Goal
**Acknowledge and prove that there are NO hardcoded metrics or mock fallbacks.** You must guide the judges to watch the database wipe, process your actual CCTV clips, and compute real-time, randomized shopper analytics from scratch.

---

## ⏱️ Playbook A: The 5-Minute Elevator Pitch
*Focus: Business value, dynamic data ingestion flow, and premium design.*

* **0:00 - 1:00 ➔ The Setup & The Retail Blind Spot**
  * **What to Show:** The main dashboard landing page (🔗 http://localhost:3000). Highlight the green "System Status Nominal" badge and clean "0" state.
  * **What to Say:** *"Physical brick-and-mortar stores historically operate in an analytical blind spot. Unlike e-commerce sites, which track every click and bounce, store managers only see POS sales. Apex OS bridges this gap. On this cold startup, our database is completely empty by design, showing 100% authenticity. We will now feed it custom data."*
* **1:00 - 2:30 ➔ Dynamic Ingestion Inception**
  * **What to Show:** Click **Upload CCTV/Data** in the navigation bar. Upload the store layout spreadsheet, POS sales CSV, and a video clip. Click **Trigger Video Processing**.
  * **What to Say:** *"As we upload the store assets, the backend container starts a background processing thread. It automatically clean-wipes any previous cache or sessions, extracts video lengths dynamically, and processes the raw CCTV frames. The camera heartbeat watchdog immediately transitions from stale to active status."*
* **2:30 - 4:15 ➔ Live Metrics & Layout Heatmaps**
  * **What to Show:** Navigate back to the **Dashboard** and **Layout Heatmap** views. Highlight footfall metrics, the conversion funnel, and hovering over shelf zones to show counts and dwells.
  * **What to Say:** *"Our edge-optimized YOLOv8 + ByteTrack pipeline processes paths on standard CPUs. Notice how the metrics updated instantly! By hovering over these categories on our heatmap, you can see live dwells and sample-size data confidence badges (LOW / MEDIUM / HIGH). Store associates are isolated and filtered out using an HSV color uniform mask and majority-voting trajectories."*
* **4:15 - 5:00 ➔ AI Suggestions & Business Impact**
  * **What to Show:** Expand the AI Suggested Actions accordion drawer at the bottom of the landing page.
  * **What to Say:** *"Friction events generate structured AI suggested actions. These recommendations are saved in the database as serialized JSON objects containing expected business recoveries and reasoning metrics, rather than simple hardcoded alert strings."*

---

## ⏱️ Playbook B: The 10-Minute Deep Dive
*Focus: Z-Score anomalies, queue severities, and backend REST APIs.*

* **0:00 - 4:00 ➔ The 5-Minute Flow**
  * Execute the steps in the 5-Minute Pitch to ingest the data and populate the live dashboard metrics.
* **4:00 - 7:00 ➔ Stateful Anomalies & Temporal Escalation**
  * **What to Show:** Navigate to the **Diagnostics Console** and scroll down to the anomaly alerts table.
  * **What to Say:** *"We run automated anomaly checks statefully. We apply a standard statistical Z-Score window. If traffic or wait times exceed a Z-score of 2.0, alerts are raised. If a queue bottleneck remains unresolved in our database for over 10 minutes, the queue severity engine automatically escalates the alert from Warning to Critical, forcing cashier reinforcement actions."*
* **7:00 - 9:00 ➔ Active REST APIs Verification**
  * **What to Show:** Open Swagger UI at 🔗 http://localhost:8000/docs. Expand and execute `GET /api/health` and `GET /api/dashboard`. Highlight the JSON schema, the `stale_feed` boolean, and the trace IDs.
  * **What to Say:** *"FastAPI automatically hosts our interactive REST API schemas. Notice the detailed JSON payloads. Every HTTP request header is stamped with a unique trace ID, allowing us to debug logs from the UI console directly to database commits."*
* **9:00 - 10:00 ➔ Wrap-up & Financial Recovery**
  * **What to Show:** Return to the dashboard and highlight the "Revenue Leakage" card.
  * **What to Say:** *"By quantifying exactly how much cash is lost due to queue abandonment, we empower floor managers to deploy express checkouts statefully, saving thousands in lost daily conversions."*

---

## ⏱️ Playbook C: The 15-Minute Technical Masterclass
*Focus: Database tables, code structures, and production cloud hosting.*

* **0:00 - 9:00 ➔ The 10-Minute Flow**
  * Execute the steps in the 10-Minute Presentation, demonstrating the dashboard, heatmaps, and live Swagger API responses.
* **9:00 - 12:00 ➔ Relational Database Inspection**
  * **What to Show:** Open a terminal or database GUI showing the PostgreSQL container tables. Query the `visitors`, `sessions`, and `events` tables to show the active database records.
  * **What to Say:** *"Here is our active PostgreSQL 16 database. You can see the visitor track IDs, uniform staff flags, session exit times, and spatial event classifications. Notice how our indexing strategy clusters timestamp rows to ensure instant sub-10ms aggregates."*
* **12:00 - 14:00 ➔ Multi-Cloud Deployment Blueprints**
  * **What to Show:** Open `DEPLOYMENT.md` or explain the split-cloud architecture.
  * **What to Say:** *"In production environments, we deploy a Split-Cloud Architecture. The static React assets are served via Vercel for instant loading, the PostgreSQL database is hosted on a managed Railway instance, and the FastAPI backend runs on a high-CPU Railway instance. By using an optimized frame-skip of 5, the edge YOLO pipeline consumes minimal CPU resources, negating the need for expensive NVIDIA GPUs."*
* **14:00 - 15:00 ➔ Technical Q&A & Code Quality**
  * **What to Show:** Open code files like `backend/app/services/cv_pipeline.py` or highlight the 100% test coverage check.
  * **What to Say:** *"Our codebase has 100% unit test coverage passing successfully inside our containers. The entire system is built for GDPR compliance, edge latency efficiency, and high scalability."*

---

## 📝 Presenter Cheat Sheet (Quick Actions)

| Step | Presenter Action | Highlight Metrics | Highlight Edge Cases |
| :---: | :--- | :--- | :--- |
| **1** | Open http://localhost:3000 | • Empty dashboard states<br>• System Status "Nominal" | • Division-by-zero safety<br>• Database starts at absolute zero |
| **2** | Upload Excel, CSV, and MP4 | • Live file processing status | • Dynamic video length reading<br>• Database wipes clean before runs |
| **3** | Process & Open Dashboard | • Updated Footfall, Customer counts | • Camera Stale Feed watchdog clears |
| **4** | Navigate to `/heatmap` | • Zone attraction percentages | • LOW/MEDIUM/HIGH data confidence badges<br>• Employee HSV hue filtering |
| **5** | Navigate to `/health` | • CPU uptime, Trace IDs | • trace_id mapping middleware |
| **6** | Open http://localhost:8000/docs | • Swagger endpoint payloads | • API JSON schema schemas |
