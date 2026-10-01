# ADR 004: CAP Theorem & PACELC Trade-offs for Telemetry vs Transactional Data

## Status
**Accepted**

## Context
A connected-vehicle intelligence platform processes two distinct data categories with opposing trade-off requirements:
1. **Transactional Data (Billing, Fleets, Alerts, Work Orders, Access Control)**: Requires strict ACID consistency.
2. **High-Volume Telemetry Streams (Location, Speed, Battery, Temperature)**: Requires high write availability and sub-second ingestion latency.

## Decision
We enforce a split CAP/PACELC policy:
- **Transactional Core (PostgreSQL)**: Configured as **CP (Consistency / Partition Tolerance)** under CAP, and **PC/EC (Consistency over Latency)** under PACELC. Financial records, vehicle ownership, active alerts, and work orders must never be stale or corrupted.
- **Raw Telemetry Stream (MongoDB / In-Memory Buffer)**: Configured as **AP (Availability / Partition Tolerance)** under CAP, and **PA/EL (Availability & Low Latency over Consistency)** under PACELC. Raw vehicle location and speed data prioritize high ingest availability over strict global synchronization.

## Consequences
- **Positive**: Prevents ingestion bottlenecks while ensuring 100% data integrity for business-critical operational workflows.
- **Negative**: Telemetry logs may experience short eventual consistency propagation delays.
