# Master Technical Guide: Vehicure Connected Vehicle Intelligence Platform

Welcome to the comprehensive master documentation for **Vehicure** — Predictive Vehicle Health & Maintenance Intelligence Platform built for the **Motorq Connected Vehicle Intelligence Hackathon**.

This document serves as the complete technical manual covering the platform's architectural design, directory structure, file-by-file explanations, datastore implementations, machine learning engine, containerization setup, and end-to-end operational workflow.

---

## 📋 Table of Contents
1. [Executive Summary & Product Vision](#1-executive-summary--product-vision)
2. [End-to-End System Architecture & Data Flow](#2-end-to-end-system-architecture--data-flow)
3. [Exhaustive Directory & File-by-File Breakdown](#3-exhaustive-directory--file-by-file-breakdown)
   - [Root Configuration & Deployment Files](#31-root-configuration--deployment-files)
   - [Backend Service (`backend/`)](#32-backend-service-backend)
   - [Frontend Dashboard (`frontend/`)](#33-frontend-dashboard-frontend)
   - [Hackathon Documentation Pack (`solution_document/`)](#34-hackathon-documentation-pack-solution_document)
   - [Monitoring Config (`prometheus/`)](#35-monitoring-config-prometheus)
4. [Technology Stack & Frameworks Deep-Dive](#4-technology-stack--frameworks-deep-dive)
5. [Polyglot Database Architecture (Postgres + Redis + Mongo)](#5-polyglot-database-architecture-postgres--redis--mongo)
6. [Predictive ML Engine & Hybrid Rule Engine](#6-predictive-ml-engine--hybrid-rule-engine)
7. [Containerization & Cloud Infrastructure (Docker, Nginx, Prometheus)](#7-containerization--cloud-infrastructure-docker-nginx-prometheus)
8. [How to Run, Test, and Demonstrate the Platform](#8-how-to-run-test-and-demonstrate-the-platform)

---

## 1. Executive Summary & Product Vision

Vehicure is an enterprise-grade Predictive Vehicle Health & Maintenance Intelligence Platform engineered to monitor large connected-vehicle fleets (**100,000+ simulated vehicles in real time**).

The platform addresses a critical challenge in modern Software-Defined Vehicle (SDV) logistics: **turning high-velocity telematic firehoses into real-time failure predictions and automated preventive maintenance workflows before catastrophic breakdowns occur.**

### Core Platform Capabilities
- **100,000+ Vehicle Scale:** Simulates 100K connected vehicles generating location, speed, engine temperature, battery voltage, odometer, DTC diagnostic codes, and driving maneuvers.
- **Real-Time Validation & Deduplication:** Filters duplicate events using a double-hashing **Bloom Filter** and Redis sequence sets; buffers out-of-order payloads.
- **Polyglot Storage:** Combines **PostgreSQL** (3NF transactional core), **MongoDB** (raw telemetry document store), and **Redis** (in-memory state cache & Bloom filter).
- **Hybrid Predictive Engine:** Merges domain rules (engine temp spikes, low battery voltage, cylinder misfires `P0300`/`P0301`, coolant faults `P0217`) with a **scikit-learn Random Forest Classifier** to compute Health Scores (0-100), Risk Levels (CRITICAL/HIGH/MEDIUM/LOW), and Failure Probabilities (%).
- **Empirical ML Evaluation:** Evaluates Random Forest against a Logistic Regression baseline (**Precision: 95.7%**, **Recall: 74.3%**, **F1: 83.6%**, **ROC-AUC: 86.2%**, **Inference Latency: 0.42 ms**).
- **Human-Designed Enterprise UI:** 7-page React SaaS dashboard built with Vite, Recharts, and TailwindCSS, providing fleet managers with instant risk explainability and one-click preventive work order generation.

---

## 2. End-to-End System Architecture & Data Flow

```
+-----------------------------------------------------------------------------------+
|                        100,000+ VEHICLE TELEMETRY SIMULATOR                       |
|    (Normal Driving, Bursty 3x Spikes, Duplicate Sequences, Fault Injections)      |
+-----------------------------------------------------------------------------------+
                                          │
                                          ▼
+-----------------------------------------------------------------------------------+
|                        INGESTION & VALIDATION ENGINE                              |
|  - Schema Validation (Pydantic & ISO 3779 VIN Regex)                              |
|  - Idempotency Deduplication (Bloom Filter FPR=0.001 + Redis Set)                 |
|  - Out-of-Order Sequence Buffer                                                   |
+-----------------------------------------------------------------------------------+
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
+-----------------------------------+           +-----------------------------------+
|     MONGODB RAW TELEMETRY STORE   |           |    REAL-TIME FEATURE EXTRACTOR    |
|   (Unstructured Log Retention)    |           |  (Rolling Windows & Deltas)       |
+-----------------------------------+           +-----------------------------------+
                                                                  │
                                                ┌─────────────────┴─────────────────┐
                                                ▼                                   ▼
                                +-------------------------------+   +-------------------------------+
                                |      DOMAIN RULE ENGINE       |   |  SCIKIT-LEARN ML ENGINE (RF)  |
                                | (Temp Spikes, Batt, DTC Codes)|   | (Multi-Sensor Failure Prob %) |
                                +-------------------------------+   +-------------------------------+
                                                │                                   │
                                                └─────────────────┬─────────────────┘
                                                                  ▼
                                                +-----------------------------------+
                                                |   COMBINED RISK CALCULATOR        |
                                                | Risk Score = 0.4*Rule + 0.6*ML    |
                                                +-----------------------------------+
                                                                  │
                                                                  ▼
                                                +-----------------------------------+
                                                |      ALERT ENGINE & WORK ORDERS   |
                                                | (Auto-generates Work Orders)      |
                                                +-----------------------------------+
                                                                  │
                                                                  ▼
                                                +-----------------------------------+
                                                |   POSTGRESQL 3NF RELATIONAL STORE |
                                                | (Fleets, Vehicles, Alerts, Orders)|
                                                +-----------------------------------+
                                                                  │
                                                                  ▼
                                                +-----------------------------------+
                                                |   FASTAPI BACKEND & SSE STREAM    |
                                                +-----------------------------------+
                                                                  │
                                                                  ▼
                                                +-----------------------------------+
                                                |    REACT ENTERPRISE SAAS DASHBOARD|
                                                +-----------------------------------+
```

---

## 3. Exhaustive Directory & File-by-File Breakdown

Below is the detailed technical description of every single file in the repository:

### 3.1 Root Configuration & Deployment Files
* [**`README.md`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/README.md): Master documentation providing setup guides (Docker & local), quick start commands, architecture summary, and a step-by-step 5-minute live hackathon demo script.
* [**`docker-compose.yml`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/docker-compose.yml): Multi-container orchestrator bringing up PostgreSQL 15, Redis 7, MongoDB 6, FastAPI Backend, Nginx React Frontend, and Prometheus monitoring.
* [**`MASTER_PROJECT_EXPLANATION.md`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/MASTER_PROJECT_EXPLANATION.md): This master technical manual explaining the complete workings of the project.

---

### 3.2 Backend Service (`backend/`)
* [**`backend/requirements.txt`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/requirements.txt): Lists Python dependencies (`fastapi`, `uvicorn`, `scikit-learn`, `sqlalchemy`, `aiosqlite`, `redis`, `pymongo`, `prometheus-client`, `pytest`, `pandas`, `numpy`).
* [**`backend/Dockerfile`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/Dockerfile): Container build definition for backend Python environment.
* [**`backend/app/main.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/app/main.py): Primary FastAPI app setup configuring CORS middleware, request latency tracker, lifespan startup database seeding, and Prometheus `/metrics` endpoint.
* [**`backend/app/config.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/app/config.py): Application settings loading environment variables, database URIs, threshold settings, and CORS origins.
* [**`backend/app/utils/vin_generator.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/app/utils/vin_generator.py): Realistic 17-character ISO 3779 compliant VIN generator with checksum calculation and support for OEM WMIs (Volvo, Subaru, Stellantis, Ford, Tesla, Mercedes-Benz).
* [**`backend/app/utils/bloom_filter.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/app/utils/bloom_filter.py): In-memory double-hashing Bloom Filter (`false_positive_rate=0.001`) for fast deduplication checks.
* [**`backend/app/models/db_models.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/app/models/db_models.py): Declarative SQLAlchemy models for Third Normal Form (3NF) tables: `Fleet`, `Vehicle`, `Driver`, `DtcCatalog`, `Alert`, `MaintenanceOrder`, and `AuditLog`.
* [**`backend/app/models/schemas.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/app/models/schemas.py): Pydantic data schemas defining validation shapes for telemetry events, vehicle summaries, alerts, analytics, system health, and work orders.
* [**`backend/app/database/init_db.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/app/database/init_db.py): Async database bootstrapper that creates database tables and seeds 100,000 synthetic vehicles across 5 OEM fleets.
* [**`backend/app/database/redis_store.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/app/database/redis_store.py): Redis adapter for vehicle state caching and idempotency sequence tracking (with in-memory fallback).
* [**`backend/app/database/mongo_store.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/app/database/mongo_store.py): MongoDB adapter for storing raw unstructured telemetry events (with ring-buffer fallback).
* [**`backend/app/services/simulator.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/app/services/simulator.py): Configurable 100K+ vehicle telemetry simulator generating live telemetry, 3x burst spikes, duplicate events, out-of-order sequences, and critical fault anomalies.
* [**`backend/app/services/validator.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/app/services/validator.py): Ingestion validator verifying VIN structure, DTC code formats, and executing Bloom filter deduplication.
* [**`backend/app/services/rule_engine.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/app/services/rule_engine.py): Domain Rule Engine evaluating engine overheating, low battery voltage, DTC codes, and harsh driving to produce human-readable risk bullet points.
* [**`backend/app/services/ml_engine.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/app/services/ml_engine.py): Scikit-learn Machine Learning service that trains a Random Forest Classifier, evaluates it against a Logistic Regression baseline, and computes failure probability %.
* [**`backend/app/services/alert_engine.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/app/services/alert_engine.py): Alert lifecycle engine managing active alerts and auto-triggering preventive maintenance work orders.
* [**`backend/app/services/metrics_tracker.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/app/services/metrics_tracker.py): Metrics tracker calculating target vs actual TPS, processing latencies ($p50 \le p95 \le p99$), REST API latency, and consumer lag.
* [**`backend/app/api/fleet.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/app/api/fleet.py): Fleet Overview API router (`/api/fleet/overview`, `/api/fleet/vehicles`).
* [**`backend/app/api/monitoring.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/app/api/monitoring.py): Live telemetry streaming API router (`/api/monitoring/stream` SSE and `/api/monitoring/ws` WebSocket).
* [**`backend/app/api/health.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/app/api/health.py): Health overview and top at-risk vehicle ranking API router (`/api/health/summary`, `/api/health/top-risk`).
* [**`backend/app/api/alerts.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/app/api/alerts.py): Alerts management API router (`/api/alerts`, `/api/alerts/{id}/resolve`, `/api/alerts/{id}/create-work-order`).
* [**`backend/app/api/analytics.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/app/api/analytics.py): Analytics and ML evaluation metrics API router (`/api/analytics`).
* [**`backend/app/api/vehicle.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/app/api/vehicle.py): Vehicle details inspector API router (`/api/vehicles/{vin}`).
* [**`backend/app/api/maintenance.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/app/api/maintenance.py): Preventive maintenance work order API router (`/api/maintenance`).
* [**`backend/app/api/system.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/app/api/system.py): System health, latency percentiles, and infrastructure metrics API router (`/api/system/health`).
* [**`backend/app/api/simulator_api.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/app/api/simulator_api.py): Simulator stress control API router (`/api/simulator/config`, `/api/simulator/start`, `/api/simulator/stop`).
* [**`backend/tests/test_backend.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/tests/test_backend.py): Pytest unit tests for VIN validation, Bloom filter, rule engine, ML model, and simulator.
* [**`backend/tests/test_api.py`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/backend/tests/test_api.py): Pytest integration tests for all FastAPI REST endpoints.

---

### 3.3 Frontend Dashboard (`frontend/`)
* [**`frontend/vite.config.js`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/frontend/vite.config.js): Vite bundler configuration with TailwindCSS plugin and API proxy forwarding.
* [**`frontend/Dockerfile`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/frontend/Dockerfile): Multi-stage Docker build producing an optimized Nginx static hosting image.
* [**`frontend/nginx.conf`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/frontend/nginx.conf): Nginx configuration serving React static assets and proxying `/api` calls to the backend.
* [**`frontend/src/index.css`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/frontend/src/index.css): Enterprise SaaS stylesheet defining restrained slate/zinc themes, custom scrollbars, and card styling.
* [**`frontend/src/services/api.js`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/frontend/src/services/api.js): Frontend HTTP client providing API calls and resilient fallbacks.
* [**`frontend/src/components/Navbar.jsx`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/frontend/src/components/Navbar.jsx): Top header with brand logo, live events/sec counter, and system status indicator.
* [**`frontend/src/components/Sidebar.jsx`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/frontend/src/components/Sidebar.jsx): Navigation sidebar linking to all 7 main pages.
* [**`frontend/src/components/StatusBadge.jsx`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/frontend/src/components/StatusBadge.jsx): Status badge component for Critical, High, Medium, and Low risk pills.
* [**`frontend/src/components/MetricCard.jsx`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/frontend/src/components/MetricCard.jsx): Reusable metric display card component with trend badges.
* [**`frontend/src/pages/FleetOverview.jsx`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/frontend/src/pages/FleetOverview.jsx): Main dashboard with KPIs, 7-day health trend chart, risk breakdown, and prioritized vehicle table.
* [**`frontend/src/pages/LiveMonitoring.jsx`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/frontend/src/pages/LiveMonitoring.jsx): Real-time incoming telemetry stream table with pause/resume controls.
* [**`frontend/src/pages/VehicleHealth.jsx`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/frontend/src/pages/VehicleHealth.jsx): Vehicle health score grid with search and risk category filters.
* [**`frontend/src/pages/AlertsPage.jsx`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/frontend/src/pages/AlertsPage.jsx): Enterprise alert inbox with alert resolution and work order creation buttons.
* [**`frontend/src/pages/AnalyticsPage.jsx`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/frontend/src/pages/AnalyticsPage.jsx): Analytics page displaying ML model evaluation metrics vs baseline, top DTC faults, and mileage impact.
* [**`frontend/src/pages/VehicleDetails.jsx`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/frontend/src/pages/VehicleDetails.jsx): Vehicle profile inspector displaying Health Score gauge, Failure Probability, **Main Risk Reasons**, Recommended Action, and telemetry charts.
* [**`frontend/src/pages/SystemHealth.jsx`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/frontend/src/pages/SystemHealth.jsx): Infrastructure monitoring page with ingestion TPS, $p50/p95/p99$ latencies, datastore statuses, and real-time simulator controls.
* [**`frontend/src/App.jsx`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/frontend/src/App.jsx): Root React application component managing navigation state.

---

### 3.4 Hackathon Documentation Pack (`solution_document/`)
* [**`solution_document/SOLUTION_DOCUMENT.md`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/solution_document/SOLUTION_DOCUMENT.md): Completed Hackathon Solution Document matching the Motorq template format & requirement traceability matrix.
* [**`solution_document/ARCHITECTURE.md`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/solution_document/ARCHITECTURE.md): System Architecture Diagram, Data Flow Diagram, C4 Context & Container Diagrams (Mermaid).
* [**`solution_document/DATABASE_ERD_3NF.md`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/solution_document/DATABASE_ERD_3NF.md): 3NF Database ER Diagram & EXPLAIN ANALYZE SQL query plan optimizations.
* [**`solution_document/SECURITY_THREAT_MODEL.md`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/solution_document/SECURITY_THREAT_MODEL.md): STRIDE Threat Model & OWASP API Top 10 Mitigation Matrix.
* [**`solution_document/PERFORMANCE_AND_EVIDENCE.md`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/solution_document/PERFORMANCE_AND_EVIDENCE.md): Measured Performance Latencies, ML Evaluation Report, and Pytest Evidence.
* [**`solution_document/ADRs/ADR-001-polyglot-storage.md`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/solution_document/ADRs/ADR-001-polyglot-storage.md): ADR 001 - Polyglot Storage Strategy.
* [**`solution_document/ADRs/ADR-002-event-streaming-and-idempotency.md`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/solution_document/ADRs/ADR-002-event-streaming-and-idempotency.md): ADR 002 - Event Streaming & Deduplication.
* [**`solution_document/ADRs/ADR-003-hybrid-predictive-risk-engine.md`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/solution_document/ADRs/ADR-003-hybrid-predictive-risk-engine.md): ADR 003 - Hybrid Predictive Engine (Rules + ML).
* [**`solution_document/ADRs/ADR-004-cap-theorem-and-pacelc-tradeoffs.md`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/solution_document/ADRs/ADR-004-cap-theorem-and-pacelc-tradeoffs.md): ADR 004 - CAP Theorem & PACELC Trade-offs.
* [**`solution_document/ADRs/ADR-005-security-and-tenant-isolation.md`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/solution_document/ADRs/ADR-005-security-and-tenant-isolation.md): ADR 005 - Security, RBAC, & Tenant Isolation.

---

### 3.5 Monitoring Config (`prometheus/`)
* [**`prometheus/prometheus.yml`**](file:///c:/Users/shrey/OneDrive/Desktop/vehicure/prometheus/prometheus.yml): Prometheus scraper configuration pulling metrics from FastAPI `/metrics`.

---

## 4. Technology Stack & Frameworks Deep-Dive

| Technology Layer | Framework / Tool | Purpose in Vehicure |
| :--- | :--- | :--- |
| **Backend API** | Python 3.10 + FastAPI | High-concurrency async REST server, typed Pydantic validation, OpenAPI documentation generation. |
| **ASGI Web Server** | Uvicorn | High-throughput asynchronous server running the FastAPI app. |
| **Frontend UI** | React 18 + Vite | Enterprise SaaS user interface, fast hot module replacement, optimized production bundle. |
| **UI Styling** | TailwindCSS + Lucide Icons | Clean restrained enterprise aesthetics, neutral slate/zinc surfaces, small rounded corners. |
| **Charts & Visualization**| Recharts | Interactive Area, Line, and Bar charts for health trends, latency percentiles, and fault histograms. |
| **Relational Core** | PostgreSQL 15 / SQLite | Third Normal Form (3NF) relational store for transactional entities (Fleets, Vehicles, Work Orders). |
| **NoSQL Telemetry Store** | MongoDB 6.0 | Document store retaining raw, high-volume unstructured telematics event logs. |
| **Cache & Deduplication**| Redis 7.0 + Bloom Filter | In-memory vehicle state caching and $O(1)$ duplicate sequence detection bit arrays. |
| **Machine Learning** | Scikit-learn | Random Forest Classifier trained to predict multi-sensor vehicle failure probability %. |
| **Metrics Exporter** | Prometheus Client | Standardized `/metrics` endpoint exposing throughput, percentiles, and error counts. |
| **Containerization** | Docker & Docker Compose | Multi-container orchestration powering local and cloud-ready infrastructure. |

---

## 5. Polyglot Database Architecture (Postgres + Redis + Mongo)

To handle 100,000+ connected vehicles without write amplification or lock contention, Vehicure uses a **Polyglot Persistence Pattern**:

```
+-----------------------------------------------------------------------------------+
|                                 POLYGLOT STORAGE MAP                              |
+--------------------------+----------------------------+---------------------------+
|      PostgreSQL (3NF)    |          MongoDB           |          Redis            |
|   (Transactional Core)   |   (Raw Telemetry Store)    |   (State Cache & Dedup)   |
+--------------------------+----------------------------+---------------------------+
| - Fleets                 | - Raw Event Payload Logs   | - Recent Vehicle State    |
| - Vehicles               | - Time-Series Telematics   | - Bloom Filter Bit Array  |
| - Drivers                | - Historical Signal Replay | - Sequence ID Deduplication|
| - DTC Catalog            |                            | - Metrics Aggregation     |
| - Alerts                 |                            |                           |
| - Maintenance Orders     |                            |                           |
| - Audit Logs             |                            |                           |
+--------------------------+----------------------------+---------------------------+
```

### Why this design?
1. **Preventing SQL Write Amplification:** Direct ingestion of 100,000 events/sec into a relational table would collapse B-tree indexes. High-volume raw events go to MongoDB and Redis cache first.
2. **Strict ACID Compliance:** Fleets, subscriptions, alerts, and maintenance work orders are stored in PostgreSQL 3NF tables to ensure strict transactional integrity.
3. **Sub-Millisecond Read Latency:** Live dashboard state updates are served directly from Redis in-memory cache.

---

## 6. Predictive ML Engine & Hybrid Rule Engine

Vehicure uses a **Hybrid Predictive Engine** combining expert domain rules with machine learning:

$$\text{Combined Risk Score} = 0.4 \times \text{Rule Penalty} + 0.6 \times \text{ML Failure Probability}$$

```
                                +-----------------------------+
                                |  Telemetry Sensor Payload   |
                                +--------------+--------------+
                                               |
                       ┌───────────────────────┴───────────────────────┐
                       ▼                                               ▼
     +-----------------------------------+           +-----------------------------------+
     |        DOMAIN RULE ENGINE         |           |    SCIKIT-LEARN ML ENGINE (RF)    |
     | Evaluates Hard Thresholds:        |           | Multi-Sensor Predictor:           |
     | - Engine Temp > 105°C             |           | - Engine Temp, Battery Voltage    |
     | - Battery Voltage < 11.5 V        |           | - Odometer, DTC Count, Speed      |
     | - Active DTC Codes (P0300, P0217) |           | - Harsh Driving Maneuvers         |
     | - Harsh Braking & Acceleration    |           | - Failure Probability (0-100%)    |
     +-----------------+-----------------+           +-----------------+-----------------+
                       │                                               │
                       └───────────────────────┬───────────────────────┘
                                               ▼
                             +-----------------------------------+
                             |     COMBINED VEHICLE RISK SCORE   |
                             |  Health Score = 100 - Risk Score  |
                             |  Risk Level: CRITICAL/HIGH/MED/LOW|
                             +-----------------------------------+
```

### Measured ML Performance vs Baseline
The Random Forest model was evaluated on a dataset of **15,000 synthetic telematics feature samples** against a **Logistic Regression baseline**:

* **RandomForest Model:** Precision: **95.7%** | Recall: **74.3%** | F1-Score: **83.6%** | ROC-AUC: **86.2%** | Inference Latency: **0.42 ms**
* **LogisticRegression Baseline:** Precision: **78.5%** | Recall: **72.0%** | F1-Score: **75.1%** | ROC-AUC: **81.2%**

---

## 7. Containerization & Cloud Infrastructure (Docker, Nginx, Prometheus)

Vehicure is containerized for single-command deployment:

* **`docker-compose.yml`**: Spins up 6 services: `postgres`, `redis`, `mongodb`, `backend`, `frontend` (Nginx), and `prometheus`.
* **Nginx Reverse Proxy (`frontend/nginx.conf`)**: Serves static compiled React bundle on port 80/3000 and proxies `/api` calls directly to `backend:8000`.
* **Prometheus Metrics (`prometheus/prometheus.yml`)**: Scrapes performance metrics every 5s from backend `/metrics`.

---

## 8. How to Run, Test, and Demonstrate the Platform

### Running the Application

#### Option A: Docker Compose (Recommended)
```bash
docker-compose up --build
```
- **React Dashboard UI:** [http://localhost:3000](http://localhost:3000)
- **FastAPI API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Prometheus Metrics:** [http://localhost:9090](http://localhost:9090)

#### Option B: Local Development
```bash
# 1. Start Backend
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000

# 2. Start Frontend
cd frontend
npm install
npm run dev
```

### Running Test Suite
```bash
cd backend
python -m pytest tests/ -v
```
*Executes all 14 automated unit and API integration tests (`14/14 PASSED`).*
