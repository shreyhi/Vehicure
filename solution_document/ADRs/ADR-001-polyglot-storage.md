# ADR 001: Polyglot Persistence Strategy (PostgreSQL + MongoDB + Redis)

## Status
**Accepted**

## Context
At 100,000+ connected vehicles streaming 1 telemetry event per second, the platform ingests over 8.6 TB/day of raw telemetry data. Attempting to store all raw telemetry in a single SQL database causes severe write amplification (updating multiple B-tree indexes), connection pool exhaustion, and starving transactional API queries. However, transactional entities (Fleets, Vehicles, Alerts, Work Orders, Audit Logs) require strict ACID guarantees and 3NF normalization.

## Decision
We adopt a **Polyglot Persistence Architecture**:
1. **PostgreSQL (3NF Core)**: Stores relational transactional entities requiring ACID compliance (Fleets, Vehicles, Drivers, DTC Catalog, Alerts, Maintenance Orders, Audit Logs).
2. **MongoDB (Raw Telemetry Store)**: Stores raw, unstructured JSON telemetry payloads at high ingest volume.
3. **Redis (In-Memory State & Deduplication)**: Caches recent vehicle operating state (`vehicle:{vin}:state`) and manages Bloom Filter bit arrays for sequence deduplication.

## Consequences
- **Positive**: Prevents SQL write amplification under high-volume telematics stream. Sub-millisecond dashboard state reads via Redis cache. Clean separation of analytical time-series logs from core transactional records.
- **Negative**: Increased infrastructure operational complexity managing three datastores. Eventual consistency window between raw MongoDB log writes and PostgreSQL alert states.
