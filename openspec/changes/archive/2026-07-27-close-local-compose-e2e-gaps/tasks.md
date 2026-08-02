## 1. Shipping contract and application behavior

- [x] 1.1 Add shared Shipping application-port tests proving HTTP and Nexus dispatch use the same versioned integration-fact contract.
- [x] 1.2 Update the Postgres adapter transaction to persist one shipment row and one dispatch outbox fact for HTTP dispatch.
- [x] 1.3 Implement `GET /api/v1/shipments/{id}` with persisted-state mapping and typed not-found responses.
- [x] 1.4 Register and test `/health/startup` using the service health registry and setup-completion state.
- [x] 1.5 Add HTTP regression tests for lifecycle reads, startup transitions, replay, and zero duplicate side effects.
- [x] 1.6 Add Nexus regression tests proving replay and outbox behavior remain compatible with the existing contract version.

## 2. Health and Compose image correctness

- [x] 2.1 Add platform health tests that require live, ready, and startup routes for every advertised HTTP service.
- [x] 2.2 Update the arm64 Compose overlay so platform-built OTel image identity is preserved while applying only the platform constraint.
- [x] 2.3 Add static validation that every resolved healthcheck executable exists in both supported image architectures.
- [x] 2.4 Rebuild and inspect the custom OTel image for `/bin/wget`, collector health endpoint reachability, and linux/arm64 metadata.
- [x] 2.5 Add Compose validation coverage for image-identity drift between base and arm64 models.

## 3. CDC and Temporal convergence

- [x] 3.1 Separate Debezium process readiness from connector registration and tune the bounded local startup budget for plugin discovery.
- [x] 3.2 Make connector initialization report `created`, `unchanged`, or `reconciled` and retain the last prerequisite/API error on timeout.
- [x] 3.3 Add connector/task and Kafka offset evidence for a uniquely identified HTTP and Nexus outbox event.
- [x] 3.4 Make Temporal Nexus endpoint reconciliation rerunnable after an already-created endpoint and retain successful exit evidence.
- [x] 3.5 Add integration tests for slow Debezium startup, connector timeout diagnostics, rerun idempotency, and endpoint convergence.

## 4. Full local operational-readiness gate

- [x] 4.1 Define a unique-project Compose readiness command that starts the canonical eight-service model and waits for all required roles and one-shot initializers.
- [x] 4.2 Extend the readiness manifest schema with image/platform inventory, health state, one-shot exit codes, workflow results, persistence counts, connector state, and Kafka offsets.
- [x] 4.3 Add real HTTP lifecycle operations covering dispatch, replay, completion, cancellation, readback, and unknown-resource handling.
- [x] 4.4 Add real Temporal/Nexus operations covering terminal status, operation identity, replay, latency, and bounded failure thresholds.
- [x] 4.5 Add Postgres and Kafka assertions proving the outbox-to-topic path and zero duplicate side effects.
- [x] 4.6 Keep focused Nexus pilot evidence explicitly labeled and reject it as a substitute for full-stack readiness.
- [x] 4.7 Capture bounded diagnostics before cleanup and scope shutdown/reset to the isolated Compose project.
- [x] 4.8 Require LGTM startup and telemetry assertions for the canonical full-stack gate, while keeping the focused core profile separately labeled.

## 5. Verification, documentation, and rollout

- [x] 5.1 Update the Shipping README and runbook with the read/startup contracts, HTTP-versus-Nexus outbox behavior, and focused/full evidence distinction.
- [x] 5.2 Update Compose operator documentation with Debezium convergence timing, arm64 image requirements, retry behavior, and rollback steps.
- [x] 5.3 Add security and redaction assertions for retained connector, workflow, and failure diagnostics.
- [x] 5.4 Run focused Shipping and platform tests, Compose validation, local CDC tests, and strict OpenSpec validation.
- [x] 5.5 Run the full local operational-readiness gate on a clean isolated project and retain the passing manifest.
- [x] 5.6 Document rollback verification and confirm no cloud deployment or production state is changed.
