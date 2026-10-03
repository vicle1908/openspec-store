# Proposal: Workspace Dependencies Modernization and Toolchain Reconciliation

## Why
Following comprehensive evaluation of the Go microservices and SHB banking ecosystems, several key libraries have newer stable releases that enhance observability, performance, and memory management:
- OpenTelemetry Go logging API graduated from experimental v0.22.0 to v1.0 General Availability (v1.47.0), enabling stable trace-log correlation via OTLP and `otelslog`.
- ConnectRPC v1.21.0, otelpgx v0.12.0, goose v3.28.0, go-redis v9.22.0, and ulid v2.1.2 provide bug fixes and improved connection pooling.
- 35 historical references to Go 1.26.5 persist in guidelines, Dockerfiles, and preflight scripts despite runtime alignment to Go 1.27.1.
- In `shb-core`, OpenTelemetry SDK/API dependency constraints are capped at `<=1.44.0`, blocking adoption of Python OTel 1.45.0.

## What Changes
- Upgrade OpenTelemetry Go modules to v1.47.0 across platform and services, adopting GA `otel/log`.
- Upgrade ConnectRPC (v1.21.0), otelpgx (v0.12.0), goose (v3.28.0), go-redis (v9.22.0), and ulid (v2.1.2).
- Reconcile stale Go 1.26.5 metadata in `services/AGENTS.md`, `platform/AGENTS.md`, `tools.env`, Dockerfiles, and preflight scripts to Go 1.27.1.
- Expand `opentelemetry-api` and `opentelemetry-sdk` upper bounds in `shb-core` to `<=1.45.0`.

## Impact
- **Services Affected**: All 8 microservices (`catalog`, `customer`, `inventory`, `notification`, `order`, `payment`, `reporting`, `shipping`), shared `platform/` module, and `shb-core`.
- **Breaking Changes**: Zero. Full backwards compatibility is preserved across all APIs and events.
