## Context

The local Temporal/Nexus pilot proved real workflow and HTTP idempotency, but
the surrounding Compose audit found that the documented Shipping read/startup
surface is incomplete, HTTP dispatch and Nexus dispatch do not share identical
outbox behavior, and the arm64 overlay can select the upstream OTel image
instead of the repository-built image containing the health probe. Debezium
plugin discovery also takes several minutes on the local single-CPU container;
the current dependency timeout can fail while the connector is still
converging. The full eight-service startup needs evidence that distinguishes a
focused pilot from canonical readiness.

## Goals / Non-Goals

**Goals:**

- Make Shipping’s documented HTTP and health contracts executable and
  persistence-backed.
- Ensure both HTTP and Nexus dispatch paths atomically persist the aggregate
  change and versioned outbox integration fact under the service’s ownership.
- Make arm64 Compose resolve the custom OTel image and keep health probes valid.
- Make Debezium, topics, connector registration, and Nexus reconciliation
  bounded, idempotent, and diagnosable.
- Add a full-stack local evidence gate with real operations and retained
  artifacts.

**Non-Goals:**

- Changing production/cloud deployment topology or introducing a remote
  Temporal authorizer.
- Changing public Nexus operation names, event versions, or Kafka delivery
  guarantees.
- Making HTTP reads a new cross-service dependency for Order.
- Replacing Debezium or Kafka with another transport.

## Decisions

1. **One Shipping application contract for all entry points.** The HTTP
   adapter and Nexus activity will call the same application port and
   transaction boundary. The port returns a versioned integration fact; the
   Postgres adapter persists the shipment and outbox row atomically. This
   avoids a separate HTTP-only event mapping and preserves idempotent replay.

2. **Explicit health state, not route aliases.** Shipping will use the shared
   health registry to expose live, ready, and startup semantics. Startup stays
   false until migrations, topics, connector registration, and worker setup
   complete; read routes use the repository port and return a stable
   not-found response.

3. **Arm64 overlay preserves image identity.** The arm64 file will set only
   platform constraints for the collector and will not replace the
   `platform-otel-collector:local` image with the upstream image. The custom
   Dockerfile remains the sole owner of the copied BusyBox probe.

4. **Readiness waits for convergence, not a fixed optimistic sleep.**
   Debezium health and REST readiness are polled with a bounded budget
   appropriate to plugin discovery. Connector registration and endpoint
   reconciliation remain idempotent and rerunnable; a timeout retains logs,
   connector status, topic metadata, and last error.

5. **Evidence is a first-class local artifact.** The canonical gate records
   resolved Compose, image/platform inventory, container health and one-shot
   exit codes, real HTTP/Nexus lifecycle results, Postgres side-effect counts,
   connector/task status, and Kafka topic/offset evidence. Focused Nexus pilot
   evidence remains separately labeled.

6. **Tests cover both static and live behavior.** Unit tests cover route and
   transaction behavior; container-backed acceptance covers Compose
   convergence, replay, outbox-to-Kafka delivery, and failure diagnostics.
   No cloud credentials or cloud deployment are required.

## Risks / Trade-offs

- [Risk] Longer Debezium startup increases local feedback time → use bounded
  readiness budgets, progress output, and cached images while failing with
  actionable diagnostics.
- [Risk] Adding an outbox write to HTTP dispatch changes observable event
  volume → preserve the existing event schema/version and add idempotency
  assertions before enabling the full-stack gate.
- [Risk] Recreating Compose services can invalidate old evidence → every gate
  uses a unique project name and records the exact project and image digests.
- [Risk] The collector image must remain available for linux/arm64 →
  validate the built image platform before startup and retain an explicit
  emulation fallback only as a diagnostic mode.

## Migration Plan

1. Add route, application-port, transaction, health, and outbox tests.
2. Update Compose image selection and readiness scripts.
3. Run focused Shipping/Nexus acceptance, then the full local operational gate.
4. Retain manifests and diagnostics; rollback by disabling the new gate and
   reverting the application/Compose changes without changing stored event
   versions.

## Resolved Decisions

- `GET /api/v1/shipments/{id}` SHALL expose the carrier tracking number
  already returned by dispatch responses. It is an existing documented
  Shipping contract field, not a new secret-bearing value.
- The canonical full-stack readiness gate SHALL include LGTM and require
  telemetry assertions. The focused core profile may omit LGTM only when its
  manifest is labeled focused and cannot satisfy full-stack readiness.
