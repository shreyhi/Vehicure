# ADR 005: Security, RBAC, Tenant Isolation, & Data Masking

## Status
**Accepted**

## Context
Connected vehicle data contains sensitive location tracks, driver behavior patterns, and commercial fleet secrets. Regulators (GDPR, India DPDP, UNECE R155) mandate strict data protection, audit logging, tenant isolation, and location privacy masking.

## Decision
1. **OAuth2 / JWT Authentication & RBAC**: Enforce Role-Based Access Control (`Fleet_Manager`, `Service_Technician`, `Auditor`).
2. **Tenant Isolation**: Isolate fleet data at the API database query layer using strict `fleet_id` filtering.
3. **Data Masking**: Automatically fuzz location GPS coordinates (`latitude/longitude` rounded to 3 decimal places) for non-administrative API roles.
4. **Comprehensive Audit Trail**: Record all user actions, rule evaluations, and ML predictions in `audit_logs` table.

## Consequences
- **Positive**: Complete compliance with global privacy regulations and protection against multi-tenant data leakage.
- **Negative**: Slight overhead for JWT verification and location fuzzing middlewares.
