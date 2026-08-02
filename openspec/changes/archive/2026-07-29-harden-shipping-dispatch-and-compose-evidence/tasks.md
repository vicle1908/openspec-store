## 1. Durable Shipping ledger and migration

- [x] 1.1 Inventory every `dispatch_operations`, Shipment, HTTP idempotency, and legacy Activity reader/writer and document the compatibility mapping before editing.
- [x] 1.2 Add the forward Shipping migration for `lease_token`, `lease_expires_at`, and `attempt_count`, with indexes/constraints and idempotent rerun behavior.
- [x] 1.3 Extend the application ports and operation model with canonical claim outcomes, `ErrOperationInProgress`, lease ownership, reconciliation, retained outcomes, and terminal-state semantics without importing pgx or Temporal types.
- [x] 1.4 Implement insert-or-reload claiming, expired-lease compare-and-swap acquisition, and token-guarded reconciling/completion/failure transitions in the PostgreSQL adapter using short transactions only.
- [x] 1.5 Add repository integration tests for concurrent same-fingerprint claims, conflicting fingerprints, expired lease recovery, stale-token rejection, terminal immutability, and one-row/one-outbox constraints.

## 2. Shipping application behavior

- [x] 2.1 Refactor the dispatch command handler to use the shared ledger claim protocol before any carrier call and to return replay, in-progress, conflict, reconciliation, and execute outcomes through typed application errors.
- [x] 2.2 Keep provider I/O outside database transactions, use the stable operation provider key, call `LookupDispatch` before retrying unknown outcomes, and finalize Shipment, ledger result, and outbox atomically under the current lease token.
- [x] 2.3 Add handler tests for concurrent HTTP/Activity-equivalent calls, crash-after-provider recovery, provider lookup, retryable taxonomy, and rejection of stale finalization.
- [x] 2.4 Update the HTTP adapter to map exact replays to the retained `201` response/body, fingerprint conflicts to `409`, active ownership to `409` plus `Retry-After`, and reconciliation/transient failures to documented retryable statuses without leaking internals.
- [x] 2.5 Add public HTTP integration tests that assert same-key replay, conflicting input, concurrent duplicate behavior, carrier-call count, Shipment count, operation count, and outbox count.

## 3. Temporal/Nexus adapter contract

- [x] 3.1 Compute the canonical dispatch fingerprint once in the application boundary and use the full fingerprint with the operation ID in the handler Workflow ID.
- [x] 3.2 Set `WorkflowIDConflictPolicy=USE_EXISTING` and `WorkflowIDReusePolicy=ALLOW_DUPLICATE` in the workflow-backed Nexus start options and preserve typed retryable/non-retryable error classification.
- [x] 3.3 Add Nexus tests for concurrent exact starts attaching to one running Workflow, post-completion ledger replay, different-fingerprint non-attachment, and cancellation/retry identity propagation.
- [x] 3.4 Add operation, fingerprint, correlation, causation, lease, route, and exact local run/project fields to structured logs, metrics, Workflow memo/search attributes, and pilot evidence with payload redaction.
- [x] 3.5 Update the Nexus/Temporal runbook and ADR references to distinguish logical-effect guarantees from at-least-once external invocation and to record the self-hosted callback/authorization boundary.
- [x] 3.6 Update the Shipping worker/bootstrap wiring and its integration tests so the shared carrier adapter, Nexus service registration, and task-queue worker use the same application contract and evidence identity.

## 4. Carrier adapter and runtime health

- [x] 4.1 Protect all shared state in `carrier.StubAdapter` with a mutex and private locked helpers, preserving deterministic results and snapshot semantics.
- [x] 4.2 Add `go test -race` coverage for concurrent execute, lookup, cancel, dispatch, and calls-snapshot operations using the shared stub instance.
- [x] 4.3 Register a bounded, redacted Shipping `database` check backed by `pgxpool.Pool.Ping` for readiness and startup while keeping liveness dependency-free and remote Nexus/Kafka checks separate.
- [x] 4.4 Add health tests for healthy and database-down states, liveness during outage, timeout classification, HTTP status, and absence of DSNs, passwords, hostnames, SQL, or provider payloads.

## 5. Compose lifecycle ownership

- [x] 5.1 Add a collision-resistant run identity and unique project derivation to the local readiness wrapper, honoring an explicit safe override only after exact preflight absence is proven.
- [x] 5.2 Bind `VALIDATION_RUN_ID` and `VALIDATION_COMPOSE_PROJECT` through preflight, Compose validation, startup, smoke, pilot, and acceptance; record `owned=false` until the exact resource check succeeds.
- [x] 5.3 Make cleanup project-scoped and ownership-aware, implement keep/retained and skipped-not-owned outcomes, and fail the outer run when cleanup fails while retaining diagnostics.
- [x] 5.4 Add shell tests with fake Docker/Make commands for pre-existing projects, owned cleanup, retained stacks, cleanup failure, and concurrent unique invocations.

## 6. Run-scoped evidence contracts

- [x] 6.1 Add schema-versioned `run_id` and `compose_project` fields to smoke, Worker, Workflow, Shipping-pilot, and Compose acceptance evidence writers and use exact run-named files/directories.
- [x] 6.2 Bind each Compose run’s evidence directory through `COMPOSE_RUN_EVIDENCE_DIR` and remove shared-root newest-file discovery from acceptance.
- [x] 6.3 Make acceptance validation require exact run/project identity, freshness, evidence class, and operation cohort for every referenced artifact; cleanup status remains an outer-run post-cleanup gate.
- [x] 6.4 Add validator tests for missing, stale, cross-run, cross-project, focused-vs-full, and cleanup-failed evidence, including two concurrent readiness runs.

## 7. Real local operational verification

- [x] 7.1 Extend the Shipping local integration harness to perform real dispatch, exact replay, conflicting request, concurrent HTTP/Nexus duplicate, lease-expiry recovery, completion/cancellation, PostgreSQL inspection, and Kafka/Debezium observation.
- [x] 7.2 Assert one carrier side effect, one Shipment transition, one completed operation, one dispatch outbox fact, terminal workflow status, typed errors, and exact run/project identity in the retained manifest.
- [x] 7.3 Verify local Temporal Server `1.31.2`, Go SDK `1.46.0`, pgx `5.10.0`, and every resolved Compose image for native `linux/arm64` and `linux/amd64`; record any approved emulation fallback rather than silently substituting an image.
- [x] 7.4 Run the focused Nexus pilot and the full eight-service readiness gate separately and reject focused evidence as a full-readiness input.

## 8. Architecture, compatibility, and documentation

- [x] 8.1 Update Shipping architecture/layering tests to assert domain/application packages remain free of Temporal, Nexus, pgx, SQL, Kafka, carrier SDK, and peer-private imports.
- [x] 8.2 Update the canonical Shipping, Temporal/Nexus, health, Compose, orchestration, and local-verification documentation to match the ledger, lease, health, identity, cleanup, and replay contracts.
- [x] 8.3 Record migration compatibility, configuration defaults, metrics/cardinality limits, security redaction, rollback routing, and cloud-readiness deferral in the owning ADR/runbooks.
- [x] 8.4 Check Go and package dependencies with the repository’s current module tooling, retain existing pins unless an official compatibility finding requires a reviewed change, and update sums only when needed.

## 9. Verification and handoff

- [x] 9.1 Run focused Shipping unit, integration, and race tests plus architecture and workflow replay checks; retain failure diagnostics and manifests.
- [x] 9.2 Run `make -C services/shipping-service verify-pr`, `make verify-pr`, `make compose-validate`, and `make local-operational-readiness` with the exact run/project evidence contract.
- [x] 9.3 Run `make validate-deployment` and `openspec validate --strict --all`; distinguish local evidence from hosted/cloud evidence and do not claim cloud readiness.
- [x] 9.4 Run `graphify update .` after code changes, inspect the affected handler/runtime/orchestration paths, and retain the final verification summary for OpenSpec verification/archive.
