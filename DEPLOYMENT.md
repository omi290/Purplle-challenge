# 🚀 DEPLOYMENT.md — Production Deployment Blueprint

> This document details the production cloud deployment specifications, cloud architecture recommendations, and step-by-step hosting instructions for **Apex Retail Intelligence OS**.

---

## 🏗️ 1. Multi-Cloud Architecture Evaluation

To host a deep learning retail computer vision system, we evaluated four cloud hosting strategies:

### Option A: Railway (Highly Recommended)
* **Description:** Modern, developer-focused cloud platform supporting multi-stage Docker builds, automatic SSL, and dedicated managed PostgreSQL 16 databases.
* **Pros:** Builds and runs the Docker Compose services directly from your Git repository. Auto-injects connection variables, scales easily, and offers high CPU memory capacities at low prices.
* **Cons:** Managed database limits on free tiers (solved by a standard Developer account).

### Option B: Render
* **Description:** Unified cloud platform for hosting web services, databases, and static frontends.
* **Pros:** Built-in static hosting (free) and straightforward Docker service setup.
* **Cons:** Slow build speeds for complex Python dependency trees and longer container cold starts.

### Option C: DigitalOcean (App Platform / Droplets)
* **Description:** Standard cloud provider utilizing Droplets (Linux VMs) or App Platforms.
* **Pros:** Highly predictable pricing, raw access to system kernels, and robust SSD storage.
* **Cons:** Manual infrastructure configuration (setting up reverse proxies, Docker registries, and SSL certs).

### Option D: AWS (ECS + RDS + S3)
* **Description:** Enterprise-grade cloud ecosystem.
* **Pros:** Infinitely scalable, high-speed regional CDNs, and dedicated GPU instance options.
* **Cons:** Massive billing overhead, configuration complexity, and excessive deployment setup time.

---

## 🔮 2. The Live URL Blueprint (Split-Cloud Architecture)

To maximize page load speeds and keep server costs down, we recommend a **Split-Cloud Architecture** which hosts each layer on its optimal environment:

```
                  +----------------------------------------------+
                  |                 Client UI                    |
                  |     Hosted on: Vercel or Render Static       |
                  |     (Free global CDNs, sub-200ms load)       |
                  +----------------------+-----------------------+
                                         |
                                         | REST Requests over HTTPS
                                         v
                  +----------------------------------------------+
                  |             FastAPI Web Server               |
                  |     Hosted on: Railway (Docker Container)    |
                  |     (Edge CPU optimized, autoscaled)         |
                  +----------------------+-----------------------+
                                         |
                                         | Scoped DB Session
                                         v
                  +----------------------------------------------+
                  |             PostgreSQL 16 Database           |
                  |     Hosted on: Railway Managed PG            |
                  |     (ACID compliant, indexed)                |
                  +----------------------------------------------+
```

### 1. Can the Frontend be hosted separately?
**YES.** The React frontend compiled with Vite is a collection of static HTML, CSS, and JS assets. It can be hosted for **free** on Vercel, Netlify, or Render Static Sites, leveraging global edge networks to load in under 200ms.

### 2. Can the Backend be hosted separately?
**YES.** The FastAPI backend runs as an independent Dockerized API server. It is hosted on Railway, listening for incoming REST API requests from the frontend and performing calculations.

### 3. Can the PostgreSQL database be hosted separately?
**YES.** PostgreSQL runs as a managed service (e.g. Railway Managed PostgreSQL, AWS RDS, or Neon Serverless). This keeps transactional records isolated, secure, and backed up.

### 4. Can YOLO processing remain backend-side?
**YES.** YOLOv8 Nano runs directly inside the FastAPI backend container. Because we apply a **5-frame Skip Optimization**, CPU usage remains extremely low (under 15% during video tracking), allowing the system to run on standard CPU cloud instances without requiring expensive GPUs.

---

## 🛠️ 3. Step-by-Step Deployment Instructions (Vercel + Railway)

This plan configures the production-grade split-cloud deployment.

### Part A: Deploy Managed PostgreSQL & Backend on Railway

1. **Create a Railway Account:**
   Go to [Railway.app](https://railway.app) and link your GitHub account.
2. **Launch a New Project:**
   * Click **New Project** ➔ **Provision PostgreSQL**. Railway spins up a dedicated PostgreSQL 16 instance.
   * Click **New Service** ➔ **Deploy from GitHub repo** ➔ Select your `Purplle-challenge` repository.
3. **Configure the Service Path:**
   In the service settings, set the **Root Directory** to `/backend` (so Railway builds only the backend container).
4. **Configure Environment Variables:**
   Under the service **Variables** tab, add:
   * `DATABASE_URL`: `${{ Postgres.DATABASE_URL }}` *(Railway automatically links your database connection string)*
   * `UPLOAD_DIR`: `/data/uploads`
   * `VIDEO_DIR`: `/data/videos`
   * `YOLO_MODEL`: `yolov8n.pt`
   * `FPS_SKIP`: `5`
   * `CORS_ORIGINS`: `https://your-frontend-domain.vercel.app` *(add your frontend domain here)*
   * `PORT`: `8000`
5. **Add Persistent Volume:**
   Under **Settings** ➔ **Volumes**, add a new **1 GB Volume** mounted to `/data` so that video uploads and layouts are saved statefully.
6. **Generate Public Domain:**
   Under **Settings** ➔ **Public Networking**, click **Generate Domain**. This gives you your backend API URL (e.g., `https://backend-production-xyz.up.railway.app`).

---

### Part B: Deploy the React Frontend on Vercel

1. **Create a Vercel Account:**
   Go to [Vercel.com](https://vercel.com) and link your GitHub account.
2. **Import Project:**
   * Click **Add New** ➔ **Project** ➔ Select your `Purplle-challenge` repository.
3. **Configure Build Settings:**
   * **Framework Preset:** `Vite`
   * **Root Directory:** `frontend`
   * **Build Command:** `npm run build`
   * **Output Directory:** `dist`
4. **Configure Environment Variables:**
   Under the environment variables tab, add:
   * `VITE_API_URL`: `https://backend-production-xyz.up.railway.app` *(your backend Railway public domain)*
5. **Deploy:**
   Click **Deploy**. Vercel compiles your assets and deploys your frontend globally (e.g., `https://apex-retail.vercel.app`).

---

## 📡 4. Verification Check

Once deployed, verify connectivity:
1. Navigate to your public frontend URL.
2. The UI console will display a green checkmark saying *"System Status Nominal"* (since the database starts clean).
3. Open the developer console (F12) and check the network tab; you will see all API requests communicating with your backend on Railway and returning trace IDs.
4. Upload your files and click process; the backend statefully processes the tracking files, wipes old datasets, and renders live shopper analytics on your public dashboard!
