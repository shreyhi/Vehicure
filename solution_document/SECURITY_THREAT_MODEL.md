# Security Threat Model & Risk Assessment (STRIDE)

This document presents the **STRIDE** Security Threat Model and OWASP API Security Top 10 mitigations for the **Vehicure** platform.

---

## 1. STRIDE Threat Matrix

| Threat Category | Risk Description | Attack Vector | Mitigation Strategy in Vehicure |
| :--- | :--- | :--- | :--- |
| **Spoofing** | Unauthorized vehicle device impersonating a legitimate VIN to feed false telematics | Fake telematics payload submission | ISO 3779 VIN validation + Bloom filter sequence idempotency check |
| **Tampering** | Modification of vehicle telemetry events or DTC alert flags in transit | Man-in-the-middle packet alteration | TLS 1.3 encryption in transit + SHA-256 payload checksums |
| **Repudiation** | Driver or technician denying performed maintenance or rule override | Unauthorized action execution | Append-only `audit_logs` table tracking user, timestamp, & action details |
| **Information Disclosure**| Unintended exposure of real-time vehicle GPS location tracks | Unauthorized API queries | Location fuzzing (lat/lon rounding) + tenant isolation via `fleet_id` |
| **Denial of Service**| Bursty telemetry flood overwhelming backend API servers | 3x burst traffic spikes | Asynchronous stream processing, Redis caching, & rate-limiting middleware |
| **Elevation of Privilege**| Standard technician performing fleet-wide configuration overrides | API endpoint manipulation | OAuth2 / JWT Role-Based Access Control (RBAC) enforced on FastAPI endpoints |

---

## 2. OWASP API Security Top 10 Mitigation Summary

1. **API1: Broken Object Level Authorization (BOLA)**: Mitigated by enforcing strict `fleet_id` verification on all `/api/fleet/*` and `/api/vehicles/{vin}` endpoints.
2. **API2: Broken Authentication**: Mitigated using OAuth2 Bearer Tokens with JWT signature verification.
3. **API3: Broken Object Property Level Authorization**: Pydantic schemas explicitly enforce strict request/response data shapes.
4. **API4: Unrestricted Resource Consumption**: Rate limiting on FastAPI routers & paginated responses (default `limit=50`).
5. **API5: Broken Function Level Authorization**: RBAC middleware restricting administrative actions (simulator config overrides) to admin roles.
