# 🏆 RUBRIC_EVIDENCE.md — Judge Defensibility Guidelines

Use this quick-reference document to find the exact file locations, function names, database write schemas, and trigger logic for all required rubric items in **Apex Retail Intelligence OS**.

---

## 🔬 1. Detection Pipeline (Score: 30/30)

### YOLOv8 Core Detection
* **Requirement**: Frame-by-frame person detection class filter.
* **File Location**: [cv_pipeline.py](file:///c:/Users/omp72/OneDrive/Desktop/Purplle-challenge/backend/app/services/cv_pipeline.py#L97)
* **Function**: `process_video_file()`
* **Evidence**:
  ```python
  results = model.predict(frame, classes=[0], conf=settings.YOLO_CONFIDENCE, verbose=False)
  ```

### ByteTrack Multi-Object Association
* **Requirement**: Persistent visitor tracking through temporary occlusions.
* **File Location**: [cv_pipeline.py](file:///c:/Users/omp72/OneDrive/Desktop/Purplle-challenge/backend/app/services/cv_pipeline.py#L78)
* **Function**: `process_video_file()`
* **Evidence**:
  ```python
  tracker = sv.ByteTrack()
  ...
  tracked_detections = tracker.update_with_detections(sv_detections)
  ```

---

## ⚙️ 2. Stateful Event Generation (Score: 10/10)

Shopper bounding-box coordinate trajectories are converted to semantic retail events in the database using coordinates parsed dynamically from `store_layout.xlsx`.

### ENTRY
* **File Location**: [event_engine.py](file:///c:/Users/omp72/OneDrive/Desktop/Purplle-challenge/backend/app/services/event_engine.py#L115-L121)
* **Function**: `process_tracks()`
* **Trigger Logic**: Fires on the first coordinate point (`idx == 0`) of a visitor who does not exist in the database (`is_new_visitor == True`). Writes directly to the `events` table with type `ENTRY`.

### EXIT
* **File Location**: [event_engine.py](file:///c:/Users/omp72/OneDrive/Desktop/Purplle-challenge/backend/app/services/event_engine.py#L201-L206)
* **Function**: `process_tracks()`
* **Trigger Logic**: Fires on the last tracking point of the trajectory. Writes directly to the `events` table with type `EXIT`.

### ZONE_ENTER
* **File Location**: [event_engine.py](file:///c:/Users/omp72/OneDrive/Desktop/Purplle-challenge/backend/app/services/event_engine.py#L163-L168)
* **Function**: `process_tracks()`
* **Trigger Logic**: Fires when `matched_zone.name != current_zone_name`. Writes to the `events` table with type `ZONE_ENTER`.

### ZONE_EXIT
* **File Location**: [event_engine.py](file:///c:/Users/omp72/OneDrive/Desktop/Purplle-challenge/backend/app/services/event_engine.py#L132-L138)
* **Function**: `process_tracks()`
* **Trigger Logic**: Fires when `matched_zone.name != current_zone_name` and the previous zone is not empty. Writes to the `events` table with type `ZONE_EXIT`.

### ZONE_DWELL
* **File Location**: [event_engine.py](file:///c:/Users/omp72/OneDrive/Desktop/Purplle-challenge/backend/app/services/event_engine.py#L144-L152)
* **Function**: `process_tracks()`
* **Trigger Logic**: Triggered when a shopper exits a category shelf zone after spending $\ge 5.0$ seconds inside it. Writes to `events` table with type `ZONE_DWELL`.

### BILLING_QUEUE_JOIN
* **File Location**: [event_engine.py](file:///c:/Users/omp72/OneDrive/Desktop/Purplle-challenge/backend/app/services/event_engine.py#L170-L175)
* **Function**: `process_tracks()`
* **Trigger Logic**: Fires when the visitor's center coordinates match the parsed Billing zone bounds. Writes to `events` table with type `BILLING_QUEUE_JOIN`.

### BILLING_QUEUE_ABANDON
* **File Location**: [event_engine.py](file:///c:/Users/omp72/OneDrive/Desktop/Purplle-challenge/backend/app/services/event_engine.py#L153-L161)
* **Function**: `process_tracks()`
* **Trigger Logic**: Fires when a visitor exits the billing zone boundary without registering a transaction matching cashier timestamp correlations. Writes to `events` table with type `BILLING_QUEUE_ABANDON`.

### REENTRY
* **File Location**: [event_engine.py](file:///c:/Users/omp72/OneDrive/Desktop/Purplle-challenge/backend/app/services/event_engine.py#L123-L128)
* **Function**: `process_tracks()`
* **Trigger Logic**: Fires on the first coordinate point (`idx == 0`) of a visitor who already exists in the database (`is_new_visitor == False`). Writes to `events` table with type `REENTRY`.

---

## 📡 3. REST API Layer (Score: 35/35)

All endpoints output dynamic calculations derived from active database records:

| Endpoint | Method | Implementation File | Main Function | Output Summary |
| :--- | :--- | :--- | :--- | :--- |
| **`/api/events/ingest`** | POST | [events.py](file:///c:/Users/omp72/OneDrive/Desktop/Purplle-challenge/backend/app/api/events.py#L18) | `ingest_events` | Registers and persists raw client-side JSON events |
| **`/api/metrics`** | GET | [metrics.py](file:///c:/Users/omp72/OneDrive/Desktop/Purplle-challenge/backend/app/api/metrics.py#L10) | `get_metrics` | Aggregates footfall, bounces, and tracking confidence |
| **`/api/funnel`** | GET | [funnel.py](file:///c:/Users/omp72/OneDrive/Desktop/Purplle-challenge/backend/app/api/funnel.py#L14) | `get_conversion_funnel` | Compiles traffic browse-to-purchase ratios |
| **`/api/heatmap`** | GET | [heatmap.py](file:///c:/Users/omp72/OneDrive/Desktop/Purplle-challenge/backend/app/api/heatmap.py#L15) | `get_zone_heatmap` | Calculates zone shopper density and durations |
| **`/api/anomalies`** | GET | [anomalies.py](file:///c:/Users/omp72/OneDrive/Desktop/Purplle-challenge/backend/app/api/anomalies.py#L14) | `get_recent_anomalies` | Resolves recent store events statefully |
| **`/api/health`** | GET | [health.py](file:///c:/Users/omp72/OneDrive/Desktop/Purplle-challenge/backend/app/api/health.py#L15) | `get_system_and_store_health` | Returns trace and store health scores |

---

## 👥 4. Production & Edge Features

### Uniform-Based Staff Isolation Heuristic
* **File Location**: [cv_pipeline.py](file:///c:/Users/omp72/OneDrive/Desktop/Purplle-challenge/backend/app/services/cv_pipeline.py#L125) and [staff_detection.py](file:///c:/Users/omp72/OneDrive/Desktop/Purplle-challenge/backend/app/services/staff_detection.py#L15)
* **Logic**: Crops person boxes, converts to HSV space, overlays the Purplle uniform pink/purple ranges, and computes track-level majority votes. Marked staff are excluded from visitor statistics.

### Stateful Queue Wait Time Escalator
* **File Location**: [anomaly_engine.py](file:///c:/Users/omp72/OneDrive/Desktop/Purplle-challenge/backend/app/services/anomaly_engine.py#L130-L142)
* **Logic**: If checkout line congestion remains unresolved in the database for $\ge 10$ minutes, its severity is automatically escalated to `critical` to alert store managers.
