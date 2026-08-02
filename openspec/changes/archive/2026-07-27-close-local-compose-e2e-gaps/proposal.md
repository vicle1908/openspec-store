## Why

The local Compose verification exposed several contract gaps that make a
healthy-looking stack misleading: documented Shipping read and startup
endpoints are unavailable, HTTP-created shipments do not consistently produce
the owned outbox fact, the arm64 overlay can replace the custom OTel image with
an image that fails its health probe, and Debezium startup can exceed the
dependency gate while still converging successfully. The canonical eight
service Compose path also needs a bounded, repeatable end-to-end gate so local
verification distinguishes a focused Temporal/Nexus pilot from full-stack
readiness.

## What Changes

- Add the documented Shipping startup health endpoint and shipment read
  operation, including persistence-backed lifecycle responses.
- Make HTTP shipment dispatch use the same versioned integration-fact/outbox
  contract as Nexus dispatch, preserving idempotency and at-least-once CDC.
- Preserve the custom OTel collector image and health probe across arm64
  Compose overlays.
- Make Debezium, topic provisioning, connector registration, and Temporal
  Nexus reconciliation converge with bounded startup waits and idempotent
  reruns.
- Add a canonical local operational-readiness gate that starts the full
  Compose model, records one-shot exit codes, verifies all advertised service
  health routes, exercises real HTTP, Temporal/Nexus, Postgres, and Kafka
  operations, and retains failure diagnostics.
- Document the distinction between focused Nexus acceptance and full-stack
  Compose readiness, including rollback and cleanup behavior.

## Capabilities

### New Capabilities

- `local-compose-operational-readiness`: Full-stack local Compose startup,
  convergence, real-operation verification, evidence retention, and bounded
  failure handling.

### Modified Capabilities

- `shipping-service`: Require the documented startup/read endpoints and a
  shared outbox integration-fact path for HTTP and Nexus dispatch.
- `platform-health`: Require health probes to match the actual runtime image
  and expose live, ready, and startup semantics consistently.
- `local-cdc-registration`: Require deterministic Debezium startup, connector
  convergence, topic existence, and observable outbox-to-Kafka evidence.
- `local-service-verification`: Extend local verification from process health
  to real lifecycle, replay, persistence, and event-publishing operations.
- `local-development-orchestration`: Make the canonical Compose and arm64
  overlays preserve service image identity and bounded dependency ordering.

## Impact

- Shipping HTTP adapters, application ports, persistence/outbox mapping, and
  health routing.
- `deploy/docker-compose.yaml`, `deploy/docker-compose.arm64.yaml`,
  `deploy/Dockerfile.otel-collector`, service overlays, and readiness scripts.
- Debezium connector initialization, Kafka topic provisioning, Temporal Nexus
  endpoint reconciliation, and Compose evidence artifacts.
- Existing REST and Nexus contracts remain backward compatible; the change
  fills documented routes and aligns both dispatch entry points on the same
  versioned event behavior.
- Local startup may take longer while waiting for Debezium plugin convergence,
  but must fail with actionable diagnostics rather than silently accepting a
  partial stack.
