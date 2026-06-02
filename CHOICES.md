# 🗳️ CHOICES.md — Architectural Decisions Log

> This document details the technical options considered, the AI recommendations, the final choices, and the tradeoffs behind the core subsystems of **Apex Retail Intelligence OS**.

---

## 🔍 1. YOLO Choice (Object Detection)

* **Options Considered:**
  1. YOLOv8 Nano (`yolov8n.pt`)
  2. YOLOv8 Medium (`yolov8m.pt`)
  3. Faster R-CNN (ResNet50 backbone)
* **AI Recommendation:** YOLOv8 Nano (`yolov8n.pt`) for edge-efficiency.
* **What I Chose:** **YOLOv8 Nano (`yolov8n.pt`)**
* **Why I Chose It:**
  YOLOv8 Nano has a tiny memory footprint of only **6.2 MB** and runs in **sub-15ms** per frame on a standard edge CPU, making it perfectly optimized for local retail servers. Larger models (Medium/Faster R-CNN) offer slightly higher mean Average Precision (mAP) for small objects, but they require dedicated NVIDIA GPU hardware to achieve real-time frame rates, adding massive infrastructure costs.
* **Tradeoffs:**
  Accepts a minor 3-4% drop in bounding box confidence for extremely small or heavily occluded shoppers in exchange for an 80% reduction in hardware costs and zero GPU dependencies.

---

## 👥 2. ByteTrack Choice (Multi-Object Association)

* **Options Considered:**
  1. ByteTrack (Supervision)
  2. DeepSORT (Deep Simple Online and Realtime Tracking)
  3. Traditional SORT (Simple Online and Realtime Tracking)
* **AI Recommendation:** ByteTrack for handling occlusions without Re-ID overhead.
* **What I Chose:** **ByteTrack**
* **Why I Chose It:**
  DeepSORT requires a separate deep learning Re-Identification (Re-ID) neural network to extract appearance features, which adds over 400 MB to the download package and increases latency by 30ms per frame. Traditional SORT is lightweight but immediately loses tracks and double-counts shoppers during temporary occlusions (e.g., behind shelving pillars). ByteTrack resolves both issues by using Kalman filters to estimate shopper velocity and Hungarian IoU associations to retain identities through occlusions.
* **Tradeoffs:**
  If a customer leaves the camera frame entirely and re-enters, ByteTrack treats them as a new visitor. We handle this in our business engine by correlating session timings.

---

## 💾 3. Database Choice (Persistence Layer)

* **Options Considered:**
  1. PostgreSQL 16 (Relational Database)
  2. MongoDB (NoSQL Document Store)
  3. SQLite (Embedded Database)
* **AI Recommendation:** PostgreSQL for relational integrity and transactional correlation.
* **What I Chose:** **PostgreSQL 16 (via SQLAlchemy ORM)**
* **Why I Chose It:**
  Retail analytics relies heavily on relational transactions (e.g., joining tracking event timestamps with POS cashier receipts to calculate conversions). MongoDB struggles with complex multi-table joins, while SQLite lacks concurrent connection scaling for live multi-camera environments. PostgreSQL provides robust transactional ACID compliance, JSON schema columns, and advanced clustering indexes.
* **Tradeoffs:**
  Requires active schema migration management (Alembic) and database connections configuration, which we fully automate in our Dockerized environment.

---

## 📡 4. API Choice (Backend Framework)

* **Options Considered:**
  1. FastAPI (Python)
  2. Express.js (Node.js)
  3. Django Rest Framework (Python)
* **AI Recommendation:** FastAPI for speed and native Pydantic data validation.
* **What I Chose:** **FastAPI**
* **Why I Chose It:**
  FastAPI is built on Starlette and Uvicorn, placing it among the fastest Python web frameworks, capable of handling thousands of concurrent requests. It automatically generates interactive Swagger API documentation and enforces robust data validation using Pydantic schemas. Django is heavily bloated, while Express.js would require a separate runtime from our core Python computer vision pipelines.
* **Tradeoffs:**
  FastAPI requires manual structuring of dependency injections (e.g., database session scopes), which we resolved by implementing standard, clean, reusable routers.

---

## 📊 5. Dashboard Choice (Frontend Console)

* **Options Considered:**
  1. React SPA (Vite + TailwindCSS)
  2. Next.js App Router
  3. Streamlit (Python Dashboard)
* **AI Recommendation:** React SPA for custom glassmorphic rendering and low latency.
* **What I Chose:** **React SPA (compiled with Vite & styled with Vanilla CSS/Tailwind)**
* **Why I Chose It:**
  Streamlit is easy to build in Python but is extremely rigid, reloading the entire page on user interactions and offering no path for a custom, premium design. Next.js adds massive server-side rendering (SSR) overhead that is unnecessary for local retail edge consoles. React with Vite compiles into ultra-lightweight static assets that load in sub-200ms and render premium glassmorphic cards.
* **Tradeoffs:**
  Requires separate container routing via Nginx in production, which we fully configure in our Docker multi-stage builds.

---

## 👥 6. Staff Detection Choice (Uniform Isolation Heuristic)

* **Options Considered:**
  1. HSV-based Color Mask + CLIP (Zero-shot)
  2. Separate CNN Uniform Classifier (ResNet18)
  3. Manual Staff Tagging (RFID badges)
* **AI Recommendation:** HSV-based color masking + Majority Voting for lightweight edge filtering.
* **What I Chose:** **HSV-based Color Mask + Majority Voting**
* **Why I Chose It:**
  A separate CNN uniform classifier adds over 80 MB to the model footprint, increases latency by 15ms per cropped shopper, and requires a GPU to run efficiently. RFID badges require manual hardware overhead. HSV color masking extracts crop hues instantly on standard CPUs. We combine this with a **Majority Voting** algorithm across the shopper's timeline to filter out temporary shadows or occlusion noise.
* **Tradeoffs:**
  If staff members change uniform colors (e.g., holiday seasons), the HSV range parameters must be updated in configuration files, which we make easily accessible via backend settings.

---

## ⚙️ 7. Zone Detection Choice (Spatial Event Ingestion)

* **Options Considered:**
  1. Polygon Intersection via Layout Spreadsheets (`.xlsx`)
  2. Custom OpenCV Canvas drawing (manual pixel boundaries)
  3. Bluetooth/Wi-Fi RSSI beacons
* **AI Recommendation:** Polygon boundary parsing from Excel layouts for operational flexibility.
* **What I Chose:** **Spreadsheet-Parsed Polygon Boundaries**
* **Why I Chose It:**
  Manual OpenCV canvas drawing requires developers to hardcode coordinate pixels, causing the app to crash if camera angles change slightly. Beacons add massive hardware installation costs. Parsing layout spreadsheets (`store_layout.xlsx`) allows retail managers to redefine categories (Skincare, Makeup, Billing) in Excel, and the backend automatically recalculates bounding polygons on the fly.
* **Tradeoffs:**
  Requires managers to keep layout files formatted correctly, which we handle by applying robust parser validation guards and safe defaults.

---

## 🚀 8. Deployment Choice (Hosting Strategy)

* **Options Considered:**
  1. Edge Monolith Docker + Managed Cloud PostgreSQL (Railway/Render)
  2. Centralized AWS Cloud (EC2 + RDS + ECR)
  3. Serverless Functions (AWS Lambda)
* **AI Recommendation:** Split-hosting: static frontend on Vercel/Render, edge-processing backend, and managed database on Railway.
* **What I Chose:** **Split-Hosting (Static Frontend on Render/Vercel + Backend on Railway + Managed Postgres)**
* **Why I Chose It:**
  Hosting deep learning YOLO models on serverless functions causes massive cold starts and latency spikes. Railway provides seamless multi-container staging, automatic SSL, and dedicated managed Postgres 16 instances. By keeping the React static build on Vercel or Render and hosting the FastAPI backend on Railway, we ensure the frontend loads instantly while the backend has dedicated resources for CV calculations.
* **Tradeoffs:**
  Requires configuring cross-origin resource sharing (CORS), which we fully resolve using FastAPI middleware.
