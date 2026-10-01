# ADR 002: Event Streaming, Deduplication, & Out-of-Order Handling

## Status
**Accepted**

## Context
Connected vehicle telematics streams frequently suffer from network disconnects, cellular retry bursts, duplicate message transmission, and out-of-order sequence arrival when reconnecting. Ingestion engines must process events idempotently without double-counting anomalies or state corruption.

## Decision
1. **Kafka Event Bus**: Use Apache Kafka topic `vehicle.telemetry` partitioned by `vin` as the durable messaging layer.
2. **Bloom Filter Deduplication**: Implement an in-memory double-hashing Bloom Filter (`expected_elements=1M`, `false_positive_rate=0.1%`) backed by Redis key sets (`vehicle:{vin}:seqs`) for O(1) duplicate sequence detection.
3. **Out-of-Order Sequence Buffer**: Maintain a per-vehicle rolling sequence buffer to reorder payloads before evaluating rolling telemetry deltas.

## Consequences
- **Positive**: Guaranteed idempotent processing regardless of duplicate stream re-transmissions. Zero performance degradation under 3x burst traffic spikes.
- **Negative**: Small memory overhead for Bloom filter bit arrays and sequence buffers.
