## 1. Baseline and Compatibility

- [x] 1.1 Inventory every service and platform integration suite, build tag, Make target, live dependency, environment-variable prerequisite, skip path, migration runner, hard-coded image, and current CI invocation in a retained machine-readable matrix; classify each entry as `present`, `external-only`, or `not-configured`.
- [x] 1.2 Map the new capability's scenarios to the existing `harden-shipping-dispatch-and-compose-evidence` and `complete-cloud-deployment-and-cicd-readiness` changes so Shipping assertions, local lifecycle, hosted execution, and cloud-readiness ownership do not overlap.
- [x] 1.3 Recheck `github.com/testcontainers/testcontainers-go v0.43.0` and the separate `github.com/testcontainers/testcontainers-go/modules/compose v0.43.0` release, Compose, network, wait, cleanup, Reaper, client `Close`, and reuse APIs against official documentation; compile a minimal Go 1.26.5 fixture and retain the compatibility record.
- [x] 1.4 Verify the canonical PostgreSQL, Kafka, Debezium, Temporal, Redis, Mailpit, and required service images from `deploy/tools.env` for native `linux/arm64` and `linux/amd64`, retaining any explicitly approved emulation fallback and trade-off.
- [x] 1.5 Measure current service integration durations, Docker resource use, skip counts, and failure diagnostics to establish the before-change baseline and initial concurrency budget.
- [x] 1.6 Render the focused Shipping Compose files with `docker compose ... config --quiet`, record the 16-service topology and local build images, and define the exact source-revision/build-provenance checks required before Testcontainers startup.

## 2. Test-only Harness Foundation

- [x] 2.1 Create the Go 1.26.5 `tests/ecosystem-verification` module with fixture, Compose, evidence, validation, and acceptance packages, importing no service module or service-private package.
- [x] 2.2 Implement repository-root and `deploy/tools.env` discovery with an allowlisted image/config model; add tests for missing roots, missing pins, malformed values, path traversal, and untrusted image or Compose-file input.
- [x] 2.3 Implement collision-resistant run IDs, label-safe stack/network identities, source revision and dirty-state capture, host-platform capture, and run-scoped artifact paths; add deterministic and concurrent uniqueness tests.
- [x] 2.4 Implement user-defined network and generic-container lifecycle helpers with aliases, bounded contexts, mapped endpoints, ownership tracking, diagnostic capture, and cleanup registration; add failure and cleanup tests.
- [x] 2.5 Implement the canonical PostgreSQL fixture using the pinned image, final-server wait, service-owned migration callback, successful query proof, isolated database/schema state, and bounded teardown; add success, migration-failure, timeout, and rollback tests.
- [x] 2.6 Implement Testcontainers Compose-stack construction with an explicit stack identifier, exact stack files, repository environment injection, per-service waits, service-container lookup, and scoped down behavior that removes owned orphans and volumes but not shared images.
- [x] 2.7 Add structured harness logging and bounded redaction for DSNs, passwords, Docker authentication data, provider payloads, and secret-shaped environment values; add positive and negative redaction tests.
- [x] 2.8 Add a diagnostic override contract that records declared and effective images, disables authoritative status, and rejects implicit substitution or container reuse in CI, release, recovery, and evidence modes.
- [x] 2.9 Add provider-policy tests that distinguish optional `SkipIfProviderIsNotHealthy` usage from explicitly selected integration targets, which must fail closed, and ensure every Compose run calls `Down` followed by `Close` with Reaper/ownership outcome recording.

## 3. Evidence Contract and Validators

- [x] 3.1 Define `microservices.testcontainers-ecosystem/v1` as JSON Schema with source, run, cohort, evidence class, platform, topology, images, checks, child artifacts, timings, diagnostics, ownership, and cleanup fields.
- [x] 3.2 Implement atomic manifest and child-artifact writing with SHA-256 references and deterministic ordering; add tests for interrupted writes and duplicate artifact identities.
- [x] 3.3 Implement validation for allowed evidence classes, exact source/run/stack identity, freshness, required checks, image pins and platforms, child hashes, skipped tests, redaction, ownership, and cleanup.
- [x] 3.4 Add negative controls for missing identity, cross-run and cross-project artifacts, stale evidence, altered hashes, unexpected image substitution, unsupported architecture, secret leakage, skipped required tests, and failed cleanup.
- [x] 3.5 Extend Compose acceptance validation to accept Testcontainers manifests only as supplemental references and to reject `service-integration` or `focused-ecosystem` evidence as a replacement for `canonical-full-stack`.
- [x] 3.6 Add a same-revision Compose parity validator that compares selected Testcontainers stack files, services, environment pins, and resolved images with direct Compose rendering; cover omitted overlays and pin drift.
- [x] 3.7 Store the schema at `verification/schemas/testcontainers-ecosystem-v1.schema.json`, define its required source/build/initializer/cleanup fields, and add a validator command that accepts only the two focused evidence classes.

## 4. Service Integration Migration

- [x] 4.1 Migrate customer-service PostgreSQL integration tests from their service-local Testcontainers setup to the shared canonical fixture, preserving migrations, suite isolation, cleanup, and all existing assertions.
- [x] 4.2 Migrate inventory-service PostgreSQL integration tests and `internal/testutil` users to the shared canonical fixture, removing hard-coded PostgreSQL 17 fallback behavior.
- [x] 4.3 Migrate payment-service PostgreSQL integration tests and `internal/testutil` users to the shared canonical fixture, preserving CRUD, rollback, and connection-pool assertions.
- [x] 4.4 Migrate shipping-service PostgreSQL integration tests and `internal/testutil` users to the shared canonical fixture, preserving dispatch-ledger concurrency, lease, terminal-state, Shipment, operation, and outbox assertions.
- [x] 4.5 Convert order-service integration tests from an externally supplied `ORDER_TEST_POSTGRES_DSN` prerequisite to the shared fixture while preserving clean-slate migration, down/up round-trip, and failure diagnostics.
- [x] 4.6 Convert notification-service integration tests from `NOTIFICATION_TEST_DATABASE_URL` skip behavior to the shared fixture and canonical migration path, preserving repository, idempotency, retry, and cleanup assertions.
- [x] 4.7 Convert catalog-service PostgreSQL and Redis integration suites from fixed localhost assumptions to explicit pinned fixtures or the existing Redis cluster overlay, preserving cluster, ACL, expiration, and repository behavior.
- [x] 4.8 Convert reporting-service integration tests from the default localhost database to the shared fixture, preserving projection, freshness, reconciliation, and transaction assertions.
- [x] 4.9 Convert the platform Kafka integration suite from an optional `KAFKA_BROKERS` skip to a declared focused broker fixture, including metadata, produce/consume, header, retry, and unavailable-broker assertions.
- [x] 4.10 Align Testcontainers module dependencies and local replacements across the affected test modules, run `go mod tidy` only in those modules, and prove no production package imports the test-only harness.
- [x] 4.11 Add per-service evidence writing and skip detection so an explicitly selected integration target fails for a missing suite, missing fixture, skipped required test, absent manifest, or incomplete cleanup.
- [x] 4.12 Prove default `go test ./...`, service `verify-pr`, and root `verify-pr` do not start Testcontainers or live application fixtures after the migration; document existing short-lived Docker tool-container checks (such as Buf) separately rather than treating them as integration evidence.
- [x] 4.13 For services whose current integration tests have no Make target, add an explicit target or classify the suite as `not-configured`/`external-only` in the inventory; never count an absent command as a passing integration result.

## 5. Focused Shipping Ecosystem Cohort

- [x] 5.1 Define the exact base, Shipping, Nexus, smoke/evidence, and any required observability Compose inputs for the focused cohort and make the parity validator fail when a required input is omitted.
- [x] 5.2 Implement the Testcontainers-managed Shipping stack with unique identity, exact run/evidence environment, bounded waits for one-shot initializers and long-running roles, same-project absence proof, and scoped teardown.
- [x] 5.3 Extract or reuse one canonical Shipping assertion driver with explicit HTTP, Nexus, PostgreSQL, Kafka, Debezium, Temporal, run, and stack inputs so direct Compose and Testcontainers do not encode divergent domain expectations.
- [x] 5.4 Exercise new HTTP dispatch, exact retained replay, conflicting fingerprint, and concurrent duplicate calls, asserting public responses, `Retry-After`, stable error codes, and one logical carrier effect.
- [x] 5.5 Exercise concurrent HTTP and Nexus duplicates, Workflow attach/replay behavior, operation and fingerprint identity, terminal Workflow state, and typed retryable/non-retryable outcomes.
- [x] 5.6 Inject the crash-after-provider window, wait for lease expiry, verify lookup-before-execute with the same provider idempotency key, and assert no second logical carrier effect.
- [x] 5.7 Exercise completion and cancellation through public boundaries and verify terminal Shipment and operation states cannot regress.
- [x] 5.8 Inspect PostgreSQL for exact Shipment, completed operation, attempt, and dispatch-outbox counts and correlate them with the cohort's operation identity.
- [x] 5.9 Inspect Debezium connector/task state and consume the exact `shipping.events.v1` event from Kafka, verifying event identity, contract version, ordering metadata, and at-least-once-safe deduplication.
- [x] 5.10 Inspect Temporal namespace, endpoint, worker registration, Workflow ID/run ID, and terminal state for the exact cohort identity.
- [x] 5.11 Emit the focused Shipping child manifest and link its counts and identities into `microservices.testcontainers-ecosystem/v1` evidence without marking the canonical full-stack gate passed.
- [x] 5.12 Add focused failure tests for PostgreSQL, Kafka, Debezium, Temporal, initializer, service-readiness, cross-run evidence, and cleanup outages, retaining redacted diagnostics for each boundary.
- [x] 5.13 Verify the Testcontainers Compose module builds `shipping-service:local` and `platform-otel-collector:local` from allowlisted contexts at the selected revision, records image IDs/digests and build commands, checks all one-shot initializer exit statuses, and closes the Compose/Testcontainers clients after scoped teardown.

## 6. Ownership, Concurrency, and Security Controls

- [x] 6.1 Add lifecycle tests for a pre-existing requested identity, owned cleanup, retained diagnostic stack, cleanup failure, and unrelated container/network/volume preservation.
- [x] 6.2 Add concurrent-run tests that prove unique identities, endpoints, databases, networks, volumes, artifacts, and teardown across supported lightweight service fixtures.
- [x] 6.3 Add resource-budget enforcement that serializes the heavy Shipping cohort, bounds lightweight fixture concurrency, and fails preflight with measured diagnostics rather than partially starting an unsafe cohort.
- [x] 6.4 Add tests proving container reuse is disabled for authoritative evidence and any explicit local reuse mode is labeled diagnostic-only and rejected by acceptance validators.
- [x] 6.5 Add security tests proving arbitrary images, external Compose files, unrelated host mounts, Docker credentials, production secrets, and raw DSNs or provider payloads cannot enter authoritative runs or retained evidence.
- [x] 6.6 Add log-size and artifact-retention bounds that preserve manifests and failure-first diagnostics without retaining unbounded container output.

## 7. Repository Targets and CI Definition

- [x] 7.1 Add a machine-readable inventory of required service integration suites and focused cohorts with owner, command, build tag, dependencies, expected evidence class, artifact path, timeout, and concurrency weight.
- [x] 7.2 Add root and per-service targets for one service integration suite, all service container integration suites, the focused Shipping cohort, evidence validation, negative controls, and the aggregate container verification gate.
- [x] 7.3 Implement deterministic dependency ordering, bounded concurrency, Docker preflight, skip detection, child-manifest aggregation, and failure propagation in the root orchestration target.
- [x] 7.4 Add `.github/workflows/integration.yml` with the pinned Go toolchain, Docker-capable runner, relevant path triggers, manual dispatch, cache policy, service and focused targets, negative controls, and always-run evidence upload.
- [x] 7.5 Configure bounded 30-day pull-request integration evidence retention and ensure workflow logs distinguish configured workflow state from confirmed hosted execution and branch-protection enforcement.
- [x] 7.6 Run and retain initial macOS arm64 and Linux amd64 timing and resource baselines, then set the reviewed CI concurrency, timeout, and trigger cadence from measured results.
- [x] 7.7 After the cross-platform soak and negative controls pass, wire the aggregate container target into the agreed release-significant gate while preserving the live-service-free default pull-request target (including its separately reported tool-container checks).
- [x] 7.8 Make the inventory, target names, schema path, workflow artifact path, timeout, concurrency weight, and configured-versus-hosted execution state machine-readable so orchestration cannot silently infer coverage.

## 8. Traceability, Documentation, and Rollback

- [x] 8.1 Assign stable verification IDs to every new service-integration and focused-ecosystem scenario and update the owning traceability manifests with commands, environments, evidence classes, and artifact paths.
- [x] 8.2 Update the root README, local-service verification guide, service integration documentation, and operator runbook with target selection, prerequisites, evidence locations, diagnostics, resource limits, and cleanup behavior.
- [x] 8.3 Document the four verification layers and explicitly state that service and focused Testcontainers evidence cannot establish canonical full-stack, kind, cloud, staging, production, or Argo CD readiness.
- [x] 8.4 Document Testcontainers version compatibility, canonical image-pin ownership, architecture support, diagnostic overrides, Docker trust boundary, secret redaction, and container-reuse policy.
- [x] 8.5 Add and test rollback instructions that remove new target/workflow wiring and test-only dependencies while leaving `make local-operational-readiness`, application data, service migrations, and unrelated Docker resources intact.
- [x] 8.6 Update documentation-currency policy and validators so new targets, evidence schemas, workflow files, traceability entries, and runbook links cannot drift silently.

## 9. Verification and Handoff

- [x] 9.1 Run harness unit tests and every lifecycle, evidence, redaction, security, parity, and negative-control test with deterministic seeds and retained output.
- [x] 9.2 Run every migrated service and platform integration target individually, confirming zero required skips, canonical images and migrations, correct evidence, and successful cleanup.
- [x] 9.3 Run the focused Shipping ecosystem cohort and its failure matrix, then reconcile its passing evidence with tasks 7.1, 7.2, and 7.4 of `harden-shipping-dispatch-and-compose-evidence` without closing those tasks from health-only or mismatched evidence.
- [x] 9.4 Run `make verify-pr`, `make compose-validate`, and `make validate-deployment`; retain exact commands and distinguish local static, service integration, focused ecosystem, and deployment evidence.
- [x] 9.5 Run `make local-operational-readiness` separately and prove the canonical full-stack manifest remains required and independently passing; retain diagnostics rather than substituting focused evidence if resource preflight blocks the run.
- [x] 9.6 Run the Docker-capable integration workflow on Linux amd64 and retain its external run identity, or leave hosted execution and branch-protection claims explicitly incomplete when external access is unavailable.
- [x] 9.7 Run `graphify update .` after implementation changes and inspect the affected harness, Make, CI, service integration, Shipping driver, evidence-validator, and Compose relationships.
- [x] 9.8 Run `openspec validate --strict --all`, verify every in-scope scenario is mapped and passing, and publish a final summary of selected pins, platforms, commands, timings, evidence classes, skipped checks, open external proof, and rollback.
- [x] 9.9 Perform a final execution-readiness audit: every task has an owning path and focused command, every scenario has a traceability ID, required suites are not `not-configured`, canonical Compose readiness remains separate, and any unavailable hosted proof is explicitly marked incomplete.
