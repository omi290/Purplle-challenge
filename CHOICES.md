# 🧠 CHOICES.md — Engineering Decisions & Tradeoffs

## Overview

This document records every significant engineering decision made during the development of Apex Retail Intelligence OS, including AI-assisted decisions, rejected alternatives, and tradeoffs.

---

## 1. Architecture: Monolith vs. Microservices

### Decision: **Single FastAPI Monolith**

### Reasoning
| Factor | Monolith | Microservices |
|--------|----------|---------------|
| Complexity | Low | High |
| Deployment | `docker compose up` | Kubernetes, service mesh |
| Latency | In-process calls | Network calls + serialization |
| Debugging | Single process | Distributed tracing needed |
| Demo readiness | Immediate | Days of setup |
| Hackathon fit | ✅ Perfect | ❌ Overkill |

### Rejected Alternatives
- **Microservices with Kafka**: Too complex for scope. Would require Kubernetes, service discovery, and distributed tracing.
- **Serverless (AWS Lambda)**: Vendor lock-in, cold start issues for CV model loading, complex deployment.
- **Django Monolith**: FastAPI's async support and automatic OpenAPI docs give it an edge for API-first design.

### Tradeoff
Sacrificing horizontal scalability for simplicity and development speed. A monolith handles the expected load (single store) easily.

---

## 2. Object Detection: YOLOv8 Model Selection

### Decision: **YOLOv8 Nano (yolov8n.pt)**

### Reasoning
| Model | mAP50 | Inference (ms) | Size (MB) | Memory |
|-------|-------|----------------|-----------|--------|
| YOLOv8n | 37.3 | 1.2 | 6.2 | Low |
| YOLOv8s | 44.9 | 2.1 | 21.5 | Medium |
| YOLOv8m | 50.2 | 5.8 | 49.7 | High |
| YOLOv8l | 52.9 | 9.0 | 83.7 | Very High |

### Why Nano
- **Docker-friendly**: Small download, fast container builds
- **CPU-viable**: Runs on machines without GPU
- **Person detection**: For counting people (class 0), nano accuracy is sufficient
- **Frame skip compensates**: Processing every 5th frame means tracking quality matters more than per-frame accuracy

### Rejected Alternatives
- **YOLOv5**: Older, YOLOv8 has better accuracy-speed tradeoff
- **SSD MobileNet**: Lower accuracy for similar speed
- **Faster R-CNN**: Too slow for real-time processing
- **DETR (Transformer)**: Higher accuracy but 10x slower, needs GPU

### Tradeoff
Lower per-frame accuracy traded for:
- Faster processing speed
- Lower memory usage
- Docker image size reduction
- CPU-only compatibility

---

## 3. Multi-Object Tracking: ByteTrack

### Decision: **ByteTrack via Supervision library**

### Reasoning
ByteTrack handles low-confidence detections better than alternatives by associating every detection box, not just high-confidence ones. This is critical in retail settings where:
- Occlusion is common (shelving, displays)
- Customers may be partially visible
- Crowd density varies

### Rejected Alternatives
- **DeepSORT**: Requires Re-ID model (additional complexity + model download), slower
- **SORT**: Simpler but loses tracks in occlusion
- **Custom tracker**: Reinventing the wheel, higher bug risk
- **StrongSORT**: Best accuracy but requires separate appearance model

### Why Supervision Library
- Bundles ByteTrack with clean Python API
- Handles coordinate format conversions
- Provides annotation utilities for debugging
- Well-maintained, compatible with YOLOv8

---

## 4. Staff Detection: Color Heuristic vs. CLIP

### Decision: **Color-based uniform detection (primary) with CLIP (optional)**

### Reasoning

| Method | Accuracy | Speed | Dependencies | Robustness |
|--------|----------|-------|--------------|------------|
| CLIP zero-shot | ~85% | Slow (2-5s/frame) | Large model (400MB+) | Context-dependent |
| Color HSV | ~70% | Fast (<1ms) | None | Lighting-dependent |
| Fine-tuned classifier | ~95% | Medium | Training data needed | Best |

### Implementation Choice
We default to the color heuristic because:
1. **No additional model download**: Keeps Docker image small
2. **Real-time capable**: <1ms per detection vs 2-5s for CLIP
3. **Purplle staff wear identifiable uniforms**: Color-based detection works well for known uniform colors
4. **CLIP available as upgrade**: Users can switch to CLIP by setting `STAFF_DETECTION_METHOD=clip`

### Rejected Alternatives
- **CLIP-only**: Download size + inference time makes it unsuitable as default
- **Fine-tuned ResNet**: Would need labeled training data from the specific store
- **Pose estimation**: Staff posture differs from customers but too unreliable

### Tradeoff
Lower accuracy (70% vs 85%) traded for zero additional dependencies and real-time speed. Configurable to upgrade.

---

## 5. Database: PostgreSQL vs. Alternatives

### Decision: **PostgreSQL 16**

### Reasoning
| Feature | PostgreSQL | SQLite | MySQL | MongoDB |
|---------|-----------|--------|-------|---------|
| JSON support | ✅ Native | ⚠️ Limited | ✅ | ✅ Native |
| Concurrent writes | ✅ | ❌ | ✅ | ✅ |
| Docker ready | ✅ | ✅ (file) | ✅ | ✅ |
| Analytics queries | ✅ Window funcs | ⚠️ | ⚠️ | ❌ |
| Time-series | ✅ | ❌ | ❌ | ⚠️ |
| Alembic support | ✅ | ✅ | ✅ | ❌ |

### Rejected Alternatives
- **SQLite**: No concurrent writes, unsuitable for API + CV pipeline writing simultaneously
- **MongoDB**: Schema-less is wrong fit for structured retail data; poor for aggregation queries
- **TimescaleDB**: Overkill for scope, adds dependency complexity
- **ClickHouse**: Excellent for analytics but poor for transactional writes

---

## 6. Anomaly Detection: Z-Score vs. ML Models

### Decision: **Statistical Z-Score with rolling windows**

### Reasoning
Z-score anomaly detection is:
- **Interpretable**: "This value is 3 standard deviations above normal"
- **No training data needed**: Works immediately on first day
- **Configurable thresholds**: Easy to tune per metric type
- **Deterministic**: Same input always produces same output

### Rejected Alternatives
- **Isolation Forest**: Requires sufficient historical data to train
- **LSTM Autoencoder**: Complex, needs GPU, overkill for hourly metrics
- **Prophet (Facebook)**: Time-series specific, heavy dependency
- **Simple thresholds**: Too rigid, doesn't adapt to varying baselines

### Tradeoff
Less sophisticated detection traded for immediate usability without training data. Z-scores adapt naturally as data accumulates.

---

## 7. Frontend Framework: React + Vite

### Decision: **React 18 + Vite 5 + Tailwind CSS 3**

### Reasoning
| Factor | React+Vite | Next.js | Vue | Angular |
|--------|-----------|---------|-----|---------|
| Setup speed | ✅ Fast | ⚠️ SSR overhead | ✅ Fast | ❌ Slow |
| Bundle size | Small | Medium | Small | Large |
| Ecosystem | ✅ Largest | ✅ Large | ⚠️ Medium | ⚠️ Medium |
| Recharts compat | ✅ Native | ✅ | ⚠️ Wrapper | ⚠️ Wrapper |
| Static deploy | ✅ Nginx | ⚠️ Node server | ✅ | ✅ |

### Why Not Next.js
- SSR adds complexity without benefit (SPA dashboard)
- Requires Node.js server in production
- Static export possible but negates SSR advantage

### Tradeoff
No server-side rendering traded for simpler deployment (static files + Nginx).

---

## 8. Charting Library: Recharts

### Decision: **Recharts 2.12**

### Reasoning
| Library | React Integration | Customization | Bundle Size | Learning Curve |
|---------|------------------|---------------|-------------|----------------|
| Recharts | ✅ Native | ✅ Good | 150KB | Low |
| D3.js | ⚠️ Manual | ✅ Unlimited | 240KB | High |
| Chart.js | ⚠️ Wrapper | ⚠️ Medium | 170KB | Low |
| Nivo | ✅ Native | ✅ Good | 300KB | Medium |
| Victory | ✅ Native | ✅ Good | 200KB | Medium |

### Rejected Alternatives
- **D3.js**: Too low-level for rapid dashboard development
- **Chart.js**: Canvas-based, harder to style with CSS, not React-native
- **Apache ECharts**: Large bundle, overkill feature set

---

## 9. Event Processing: Synchronous vs. Queue

### Decision: **Synchronous processing with metrics caching**

### Reasoning
For a single-store deployment:
- Event volume is manageable (~1000-5000 events/day)
- Direct database writes are fast enough
- Metrics caching prevents recomputation
- No queue infrastructure needed

### Rejected Alternatives
- **Redis Queue + Worker**: Additional infrastructure for minimal benefit
- **Celery + RabbitMQ**: Massive overhead for single-store scale
- **Kafka**: Designed for millions of events/second, absurd for this use case
- **In-memory queue (asyncio)**: Fragile, loses events on crash

### Tradeoff
No event replay or guaranteed delivery traded for zero infrastructure overhead. Acceptable for single-store scope.

---

## 10. Revenue Leakage Detection: Time-Proximity Matching

### Decision: **Match billing zone visits to POS transactions by timestamp proximity**

### Reasoning
Without customer identification (no face recognition, no loyalty card scan), we correlate:
- Billing zone visit timestamp ± 5 minutes → POS transaction timestamp
- If no matching POS transaction → potential revenue leakage

### Limitations
- **False positives**: Customer browsed billing area but wasn't buying
- **False negatives**: Customer at billing matches to wrong POS transaction
- **Accuracy**: ~70-80% estimated, which is why every metric includes a confidence score

### Why Not Better Methods
- **Face recognition**: Privacy concerns, legal restrictions, complex
- **RFID/BLE**: Requires hardware installation
- **Receipt scanning**: Requires customer cooperation

---

## 11. AI Suggestions: Rule-Based vs. LLM

### Decision: **Rule-based mapping with template system**

### Reasoning
| Approach | Accuracy | Speed | Cost | Determinism |
|----------|----------|-------|------|-------------|
| Rule-based | ✅ High | ✅ <1ms | ✅ Free | ✅ Yes |
| GPT-4 API | ✅ High | ❌ 2-5s | ❌ $$$ | ❌ No |
| Local LLM | ⚠️ Medium | ❌ 5-30s | ✅ Free | ⚠️ Semi |

### Rejected Alternatives
- **OpenAI API**: Cost, latency, external dependency, API key management
- **Local LLaMA**: Requires GPU, 4GB+ RAM, slow inference
- **No suggestions**: Reduces product value significantly

### Tradeoff
Less creative/varied suggestions traded for deterministic, instant, free generation. Rule-based suggestions are actually preferred by retail managers who want consistent, actionable recommendations.

---

## 12. Docker Strategy: Multi-Stage Builds

### Decision: **Multi-stage builds for frontend, single-stage for backend**

### Frontend
```
Stage 1: node:20-alpine → npm install → npm run build
Stage 2: nginx:alpine → copy dist → serve
```
Result: ~25MB image (vs. ~1GB with node_modules)

### Backend
Single stage with `python:3.11-slim` because:
- Runtime needs all dependencies (ultralytics, torch, etc.)
- Multi-stage would save minimal space due to Python packages
- Layer caching on `requirements.txt` provides fast rebuilds

---

## Summary of Key Tradeoffs

| Decision | Optimized For | Sacrificed |
|----------|--------------|------------|
| Monolith | Simplicity, demo speed | Scalability |
| YOLOv8n | Speed, size | Detection accuracy |
| ByteTrack | Track continuity | Re-ID accuracy |
| Color staff detection | Speed, zero deps | Staff detection accuracy |
| Z-score anomalies | Interpretability, no training | Sophistication |
| Rule-based AI | Speed, determinism | Creativity |
| Synchronous processing | Simplicity | Throughput |
| Time-proximity matching | No extra hardware | Precision |

*Every tradeoff was made with the goal of delivering a complete, demo-ready system that runs with a single `docker compose up --build` command.*
