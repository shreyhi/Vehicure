# Vehicure — Predictive Vehicle Health & Maintenance Intelligence Platform

[![Build & Test Status](https://img.shields.io/badge/pytest-14%20passed-emerald)](./solution_document/PERFORMANCE_AND_EVIDENCE.md)
[![ML Precision](https://img.shields.io/badge/ML%20Precision-95.7%25-blue)](./solution_document/PERFORMANCE_AND_EVIDENCE.md)
[![License](https://img.shields.io/badge/license-MIT-slate)](#)

> **Motorq Connected Vehicle Intelligence Hackathon Submission**  
> **Domain:** Connected Vehicles · IoT · Big Data · Enterprise Architecture  

Vehicure is an enterprise predictive vehicle health and maintenance intelligence platform built to monitor **100,000+ connected vehicles** in real time. It ingests high-volume telematics streams, validates and deduplicates events using Bloom filters, applies a hybrid predictive engine (Domain Rules + Scikit-Learn Random Forest ML model), explains failure risk reasons, and triggers automated preventive maintenance work orders.

---

## 🚀 Quick Start (Local Setup)

### Option A: One-Command Setup with Docker Compose (Recommended)
```bash
docker-compose up --build
```
* **React Dashboard UI:** [http://localhost:3000](http://localhost:3000) (or [http://localhost:5173](http://localhost:5173) in dev)
* **FastAPI Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Prometheus Metrics:** [http://localhost:9090](http://localhost:9090)

---

### Option B: Local Development Setup

#### 1. Backend Setup (Python 3.10)
```bash
cd backend
pip install -r requirements.txt
python -m pytest tests/ -v           # Run 14 automated unit & API tests
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup (React + Vite)
```bash
cd frontend
npm install
npm run dev                          # Starts Vite dev server at http://localhost:5173
```

---

## 🏗️ Core Architecture Overview

```
                          100,000+ Vehicles Telemetry Simulator
                                            ↓
                            Validation & Bloom Filter Dedup
                                            ↓
                   ┌────────────────────────┴────────────────────────┐
                   ↓                                                 ↓
      Real-Time Feature Extractor                        MongoDB Unstructured Store
                   ↓                                           (Raw Log Retention)
         ┌─────────┴─────────┐
         ↓                   ↓
   Domain Rule Engine   Predictive ML Model (RF)
         ↘                   ↙
         Combined Risk Calculator (Score 0-100, Fail Prob %)
                     ↓
             Alert Engine & Preventive Maintenance Triggers
                     ↓
       PostgreSQL 3NF Core Store (Fleets, Vehicles, Alerts, Work Orders)
                     ↓
             FastAPI REST & SSE / WebSocket Endpoints
                     ↓
         React Enterprise Fleet Management Dashboard
```

---

## 📊 Measured Performance & Metrics Summary

1. **Throughput Metrics:**
   - **Target Ingestion Rate:** `50.0 events/sec`
   - **Actual Measured Throughput:** `27.6 events/sec` (Live stream delivery rate)
2. **Latency Hierarchy:**
   - **Processing Latencies:** $p50 = 3.2\text{ms} \le p95 = 12.4\text{ms} \le p99 = 26.8\text{ms}$
   - **REST API Response Latency (p95):** `18.2 ms` (Optimized < 200 ms target)
3. **Machine Learning Model Evaluation:**
   - **RandomForest Model:** Precision: **95.7%** | Recall: **74.3%** | F1-Score: **83.6%** | ROC-AUC: **86.2%** | Inference Latency: **0.42 ms**
   - **LogisticRegression Baseline:** Precision: **78.5%** | Recall: **72.0%** | F1-Score: **75.1%** | ROC-AUC: **81.2%**

---

## 📁 Repository Structure & Documentation Index

- [`MASTER_PROJECT_EXPLANATION.md`](./MASTER_PROJECT_EXPLANATION.md): Complete Master Technical Manual explaining all tools, workings, files, datastores, and subservices.
- [`solution_document/SOLUTION_DOCUMENT.md`](./solution_document/SOLUTION_DOCUMENT.md): Completed Hackathon Solution Document & Feature Traceability Matrix.
- [`solution_document/ARCHITECTURE.md`](./solution_document/ARCHITECTURE.md): System Architecture, Data Flow, C4 Context & Container Diagrams (Mermaid).
- [`solution_document/DATABASE_ERD_3NF.md`](./solution_document/DATABASE_ERD_3NF.md): 3NF Database ER Diagram & EXPLAIN ANALYZE Query Optimizations.
- [`solution_document/SECURITY_THREAT_MODEL.md`](./solution_document/SECURITY_THREAT_MODEL.md): STRIDE Threat Model & OWASP API Top 10 Mitigations.
- [`solution_document/PERFORMANCE_AND_EVIDENCE.md`](./solution_document/PERFORMANCE_AND_EVIDENCE.md): Measured Performance Latencies, ML Evaluation Report, and Pytest Evidence.
- [`solution_document/ADRs/`](./solution_document/ADRs/): 5 Architecture Decision Records (ADR 001–005).

## 📄 Submission Materials

- 🎥 **Demo Video:** [Watch Vehicure Demo](YOUR_VIDEO_FILE_LINK)
- 📑 **Solution Document:** [View Vehicure Solution Document](YOUR_PDF_FILE_LINK)

## 📄 Submission Materials

- 🎥📑 **Demo Video & Solution Document:** [Google Drive Submission Folder](https://drive.google.com/drive/folders/1cDE6TlgsrnmWxdyN11dAPFf-k4r3aong?usp=sharing)