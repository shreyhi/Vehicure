# Architecture Documentation: Vehicure Platform

This document details the system design, C4 architecture models, data flow pipelines, and deployment topology for the **Vehicure** Connected Vehicle Intelligence Platform.

---

## 1. System Architecture Diagram

```mermaid
flowchart TD
    subgraph Edge ["Edge Layer (Simulated Telemetry)"]
        SIM["100,000+ Vehicle Simulator"]
        BURST["Bursty Load Generator (3x)"]
        NOISE["Fault & Anomaly Injector"]
        SIM --> BURST
        SIM --> NOISE
    end

    subgraph Ingestion ["Ingestion & Validation Layer"]
        VAL["Validation Engine (VIN Regex & Schema)"]
        BLOOM["Bloom Filter Deduplication (0.1% FPR)"]
        SEQ["Out-of-Order Sequence Buffer"]
        SIM --> VAL
        VAL --> BLOOM
        BLOOM --> SEQ
    end

    subgraph Streaming ["Event Streaming & Polyglot Storage"]
        KAFKA["Kafka Event Bus (vehicle.telemetry)"]
        REDIS["Redis State Cache (State & Deduplication Sets)"]
        MONGO["MongoDB (Raw Telemetry Event Log Store)"]
        SEQ --> KAFKA
        KAFKA --> REDIS
        KAFKA --> MONGO
    end

    subgraph Processing ["Real-Time Intelligence & ML Engine"]
        FEAT["Feature Extractor (Rolling Windows & Deltas)"]
        RULE["Domain Rule Engine (Engine Temp, Batt, DTC)"]
        ML["RandomForest ML Classifier (Failure Probability)"]
        RISK["Risk Score Aggregator (Health 0-100, Risk Level)"]
        ALERT_ENG["Alert Engine & Preventive Work Order Trigger"]

        KAFKA --> FEAT
        FEAT --> RULE
        FEAT --> ML
        RULE --> RISK
        ML --> RISK
        RISK --> ALERT_ENG
    end

    subgraph RelationalCore ["Relational Core (3NF)"]
        PG[("PostgreSQL Core Store (Fleets, Vehicles, Alerts, Work Orders)")]
        ALERT_ENG --> PG
    end

    subgraph API ["API & Dashboard Layer"]
        API_SRV["FastAPI Backend Server"]
        WS["SSE / WebSocket Live Stream"]
        DASH["React Enterprise SaaS Dashboard"]

        PG --> API_SRV
        REDIS --> API_SRV
        API_SRV --> WS
        WS --> DASH
        API_SRV --> DASH
    end
```

---

## 2. C4 Context Diagram

```mermaid
C4Context
    title System Context Diagram for Vehicure Platform

    Person(fleet_mgr, "Fleet Manager", "Monitors 100K+ vehicle fleet health, inspects failure risks, schedules preventive maintenance.")
    System(vehicure, "Vehicure Intelligence Platform", "Collects vehicle telematics, detects anomalies in real-time, predicts failure risk, auto-triggers work orders.")
    SystemDb(oem_cloud, "OEM Telematics Clouds", "Volvo, Subaru, Stellantis, Ford, Tesla vehicle cloud data endpoints.")
    SystemDb(service_center, "Fleet Service Center Platform", "Third-party maintenance scheduling system.")

    Rel(oem_cloud, vehicure, "Streams raw vehicle telemetry events via Kafka / REST", "JSON")
    Rel(fleet_mgr, vehicure, "Monitors dashboard, views explanations, manages alerts", "HTTPS / WSS")
    Rel(vehicure, service_center, "Dispatches preventive maintenance work orders", "REST API")
```

---

## 3. C4 Container Diagram

```mermaid
C4Container
    title Container Diagram for Vehicure Platform

    Container(web_ui, "React Dashboard UI", "React, Vite, Recharts, TailwindCSS", "Provides enterprise fleet overview, live stream table, risk explanations, and system metrics.")
    Container(api_gateway, "FastAPI Backend Service", "Python 3.10, FastAPI, Pydantic", "Handles REST requests, SSE streams, authentication, and orchestrates services.")
    Container(simulator, "Vehicle Simulator Service", "Python, asyncio", "Generates realistic telemetry streams for 100,000+ vehicles with fault injection.")
    Container(ml_worker, "Predictive Risk Worker", "scikit-learn, NumPy", "Executes Random Forest model and domain rules to score vehicle failure risk.")

    ContainerDb(postgres, "Relational DB", "PostgreSQL (3NF)", "Stores fleets, vehicle profiles, active alerts, maintenance work orders, audit logs.")
    ContainerDb(mongo, "Raw Event DB", "MongoDB", "High-throughput store for raw unstructured telemetry events.")
    ContainerDb(redis, "State Cache", "Redis 7", "Stores vehicle recent state and Bloom filter deduplication keys.")

    Rel(web_ui, api_gateway, "Consumes APIs & SSE streams", "HTTP / SSE")
    Rel(simulator, api_gateway, "Streams synthetic telemetry events", "Internal async call / Kafka")
    Rel(api_gateway, ml_worker, "Invokes risk prediction", "In-Process / Worker")
    Rel(api_gateway, postgres, "Reads/Writes relational core data", "SQLAlchemy async")
    Rel(api_gateway, mongo, "Persists raw telemetry events", "PyMongo")
    Rel(api_gateway, redis, "Caches recent vehicle state & checks idempotency", "Redis Async")
```

---

## 4. Sequence Diagram: Anomaly Detection to Preventive Work Order

```mermaid
sequenceDiagram
    autonumber
    actor Vehicle as Connected Vehicle
    participant Sim as Vehicle Simulator
    participant Val as Validation & Bloom Filter
    participant Risk as Rule & ML Risk Engine
    participant DB as PostgreSQL (3NF)
    participant UI as React Fleet Dashboard
    actor Manager as Fleet Operations Manager

    Vehicle->>Sim: Emits Telemetry Event (Temp: 118°C, DTC: P0217, Batt: 10.8V)
    Sim->>Val: Validate Schema, VIN Check & Deduplicate
    Val-->>Sim: Valid & Unique Event Approved
    Sim->>Risk: Evaluate Domain Rules + Random Forest ML Model
    Risk->>Risk: Combined Risk Score = 88.4/100 (CRITICAL, Fail Prob: 92%)
    Risk->>DB: Persist Vehicle State (Status: CRITICAL, Health: 11.6/100)
    Risk->>DB: Insert Active Critical Alert (ID: ALT-88412)
    DB-->>UI: Real-Time SSE Push: Critical Alert Notification
    UI->>Manager: Displays Alert: High Engine Temp (118°C) + DTC P0217
    Manager->>UI: Clicks "Trigger Preventive Work Order"
    UI->>DB: POST /api/alerts/ALT-88412/create-work-order
    DB->>DB: Creates Work Order (ID: WO-99120, Status: SCHEDULED)
    DB-->>UI: Work Order Confirmed
```
