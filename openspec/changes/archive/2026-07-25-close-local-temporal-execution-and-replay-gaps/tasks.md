## 1. Establish the Verification Baseline

- [x] 1.1 Mark the affected local Temporal implementation and verification status annotations as `PARTIAL`, without changing cloud or CI/CD status.
- [x] 1.2 Add one canonical machine-readable inventory of all eight services, nine task queues, registered Workflow types, canonical Activity types only, current input/output contract versions, explicit versioning behavior, current-code replay fixtures, execution canaries, and determinism-checker module paths.
- [x] 1.3 Add inventory validation tests that fail with a service and type diagnostic when a Workflow registration, canonical Activity call, contract-version validator, replay fixture, execution canary, versioning behavior, or checker path is absent or mismatched.
- [x] 1.4 Run the existing focused Temporal architecture, deterministic-replay, and worker tests and retain pre-change failures separately from unrelated repository baseline failures.
- [x] 1.5 Add a project-scoped clean-slate preflight that fails when prior local Temporal executions or histories remain, and document the disposable namespace/project reset required before the new workers start.

## 2. Complete the Shared Temporal Runtime

- [x] 2.1 Extend `platform/temporal.ActivityOptions` validation to require positive Start-To-Close and Schedule-To-Close bounds, enforce Start-To-Close not exceeding Schedule-To-Close, allow optional Schedule-To-Start, and require finite retry attempts of at least three.
- [x] 2.2 Add a typed conversion from validated platform options to SDK `workflow.ActivityOptions` that preserves every supplied timeout, retry attempt, backoff, and non-retryable error type, with focused mapping and rejection tests.
- [x] 2.3 Add heartbeat-policy validation and tests so Heartbeat Timeout is accepted only for implementations that record progress and stop on Activity-context cancellation.
- [x] 2.4 Extend the shared worker wrapper with non-blocking Start/Stop, bounded `WorkerStopTimeout`, readiness transitions, `OnFatalError` propagation, and lifecycle and timeout tests.
- [x] 2.5 Define the minimal injectable Temporal termination-client interface, implement real SDK termination with typed Not Found mapping, and cover success, missing execution, transport failure, reason propagation, and client close behavior.
- [x] 2.6 Replace the no-op `temporal-workflow terminate` path with the injectable implementation and add a local integration test that verifies a blocking Workflow reaches Terminated state with the supplied reason.
- [x] 2.7 Fix `tools/workflowaudit` to load every inventoried Go module, report discovered Workflow packages/functions, and fail when a non-empty inventory produces zero discoveries.
- [x] 2.8 Add deterministic negative fixtures containing `time.Now` and prove both the repository auditor and upstream Temporal `workflowcheck` reject them without relying on a stale analyzer cache.
- [x] 2.9 Add a root Temporal verification target that runs the validated determinism gates with the canonical allowlist for every inventoried Workflow source directory.
- [x] 2.10 Add reusable worker-option validation for `DisableRegistrationAliasing: true`, duplicate checks enabled, explicit per-Workflow versioning behavior, and bounded shutdown.
- [x] 2.11 Run `make -C platform verify` and resolve failures introduced by the shared runtime changes.

## 3. Repair Payment Worker Execution

- [x] 3.1 Wire the payment worker role to its real database pool, unit of work, command handlers, and `NewActivities` constructor, rejecting every missing required dependency before polling.
- [x] 3.2 Change payment Workflow call sites to the canonical dotted `.v1` Activity constants and register capture, refund, capture-event, and refund-event handlers consistently; do not register bare-name aliases.
- [x] 3.3 Replace direct `time.Now` with deterministic Workflow or Activity-result time and add current contract-version fields plus pre-side-effect validation to payment Workflow and Activity payloads.
- [x] 3.4 Register both payment Workflows with explicit Auto Upgrade behavior, registration aliasing disabled, and duplicate checks enabled.
- [x] 3.5 Migrate the payment worker role from blocking `Run` to the shared Start/Stop lifecycle, including bounded shutdown, fail-closed readiness, and fatal-error propagation.
- [x] 3.6 Add focused payment tests proving nil-dependency rejection, canonical-name equality, old-name rejection, current contract-version enforcement, determinism, and successful capture/refund execution.
- [x] 3.7 Run `make -C services/payment-service verify-pr`.

## 4. Repair Inventory Worker Execution

- [x] 4.1 Wire the inventory worker role to its real database pool, unit of work, command handlers, idempotency dependencies, and `NewActivities` constructor, rejecting missing dependencies before polling.
- [x] 4.2 Change inventory Workflow call sites to the canonical dotted `.v1` Activity constants and register reserve, release, confirm, and event handlers consistently; do not register bare-name aliases.
- [x] 4.3 Replace direct `time.Now` with deterministic Workflow or Activity-result time and add current contract-version fields plus pre-side-effect validation to inventory Workflow and Activity payloads.
- [x] 4.4 Register all three inventory Workflows with explicit Auto Upgrade behavior, registration aliasing disabled, and duplicate checks enabled.
- [x] 4.5 Migrate the inventory worker role to the shared Start/Stop lifecycle, including bounded shutdown, fail-closed readiness, and fatal-error propagation.
- [x] 4.6 Add focused inventory tests proving nil-dependency rejection, canonical-name equality, old-name rejection, current contract-version enforcement, determinism, and successful reserve/release/confirm execution.
- [x] 4.7 Run `make -C services/inventory-service verify-pr`.

## 5. Repair Shipping Worker Execution

- [x] 5.1 Wire the shipping worker role to its real database pool, unit of work, command handlers, idempotency dependencies, and `NewActivities` constructor, rejecting missing dependencies before polling.
- [x] 5.2 Change shipping Workflow call sites to the canonical dotted `.v1` Activity constants and register dispatch, cancel, and event handlers consistently; do not register bare-name aliases.
- [x] 5.3 Replace direct `time.Now` with deterministic Workflow or Activity-result time and add current contract-version fields plus pre-side-effect validation to shipping Workflow and Activity payloads.
- [x] 5.4 Register both shipping Workflows with explicit Auto Upgrade behavior, registration aliasing disabled, and duplicate checks enabled.
- [x] 5.5 Migrate the shipping worker role to the shared Start/Stop lifecycle, including bounded shutdown, fail-closed readiness, and fatal-error propagation.
- [x] 5.6 Add focused shipping tests proving nil-dependency rejection, canonical-name equality, old-name rejection, current contract-version enforcement, determinism, and successful dispatch/cancel execution.
- [x] 5.7 Run `make -C services/shipping-service verify-pr`.

## 6. Implement the Catalog Temporal Workflow

- [x] 6.1 Wire the catalog worker role with the same catalog-owned query service, `SetPriceHandler`, PostgreSQL repositories, unit of work, clock, ID generator, and optional quote cache used by the API role.
- [x] 6.2 Repair catalog `FindHistoryByProduct` pagination so its opaque cursor freezes a request-time cutoff and advances by deterministic `(effective_at, price_id)` keyset order; test that newly inserted prices cannot shift or repeat pages.
- [x] 6.3 Implement versioned discovery and reissue Activity payloads: discovery calls `GetPriceHistory` with stable pages of at most 100, and reissue calls `SetPriceHandler` with historical economic fields plus a Workflow-ID/source-Snapshot-ID idempotency key.
- [x] 6.4 Implement deterministic multi-step `PriceRollbackWorkflow` code using `workflow.Context`, `workflow.Now`, the frozen page cursor, issued count, one retry-safe reissue per selected snapshot, and bounded Continue-As-New under `PriceRollbackWorkflow.v1`.
- [x] 6.5 Prove catalog reissue preserves amount, currency, tax class, and effective window while atomically creating a new snapshot and outbox event and returning an accurate issued count.
- [x] 6.6 Wire catalog worker dependencies, register the Workflow and complete Activity set with explicit Auto Upgrade behavior, aliasing disabled, and duplicate checks enabled on `catalog.admin.v1`; add a starter with explicit Workflow ID conflict/reuse policy.
- [x] 6.7 Move the catalog worker to the shared Start/Stop lifecycle with bounded shutdown, fail-closed readiness, and fatal-error propagation.
- [x] 6.8 Replace misleading ordinary-function “workflow” tests with deterministic multi-step Workflow, pagination-freeze, Continue-As-New, partial-retry, idempotency, Activity ownership, registration, starter, nil-dependency, contract-version, and terminal-state tests.
- [x] 6.9 Run `make -C services/catalog-service verify-pr`.

## 7. Align Activity Policies and Heartbeats

- [x] 7.1 Inventory every `ExecuteActivity` call across the eight services and migrate it to validated platform options; record any order-service policy exception explicitly.
- [x] 7.2 Preserve order's existing remote-Activity timeout behavior, remove unsatisfied heartbeat settings or add real progress recording, and cover the resulting policy with focused tests.
- [x] 7.3 Map notification's validated retry count and overall timeout into SDK options and either implement periodic progress heartbeats or remove its unsupported Heartbeat Timeout.
- [x] 7.4 Add reporting's bounded Schedule-To-Close and finite retry policy and implement cancellation-aware progress recording for work that retains a Heartbeat Timeout.
- [x] 7.5 Align customer purge and GDPR export options with optional Schedule-To-Start semantics and add cancellation tests for any heartbeating Activity.
- [x] 7.6 Apply bounded timeout, retry, and heartbeat rules to payment, inventory, shipping, and catalog Activity call sites with operation-specific non-retryable error mappings.
- [x] 7.7 Extend architecture verification so every inventoried Activity call has Start-To-Close, Schedule-To-Close, finite `MaximumAttempts >= 3`, and a heartbeat implementation when Heartbeat Timeout is present.
- [x] 7.8 Add or align current-version fields and pre-side-effect validation for notification, customer, reporting, catalog, payment, inventory, and shipping Activity inputs/outputs; reject older versions without legacy decoders.
- [x] 7.9 Run the focused `verify-pr` target for order, notification, customer, and reporting services.

## 8. Establish True Event History Replay

- [x] 8.1 Add the version-controlled `test/replay/fixtures/temporal/<workflow-type>/` convention, fixture metadata schema, deterministic-behavior review record, synthetic-input rules, and derived-summary redaction rules.
- [x] 8.2 Add a non-default local-only fixture-generation command that records Workflow ID, run ID, type, source revision, and rationale, refuses non-synthetic fixture inputs, and never rewrites exported history payloads.
- [x] 8.3 Make clean-slate reset remove prior local payment, inventory, and shipping executions and histories before new workers start; do not export or retain migration evidence.
- [x] 8.4 Capture representative current-code synthetic JSON Event Histories for every inventoried Workflow type, including available success, retry, timer, cancellation, compensation, and Continue-As-New paths.
- [x] 8.5 Replace each faux replay test with `worker.NewWorkflowReplayer`, `ReplayWorkflowHistoryFromJSONFile` or `client.HistoryFromJSON`, current type registration, and immutable fixture replay; retain useful fresh-environment reruns under functional-test names.
- [x] 8.6 Add controlled negative replay tests proving unintended command reordering and current payload-version changes are rejected without adding legacy decoders.
- [x] 8.7 Run every service deterministic-replay suite with `go test -count=1` and prove that normal test execution does not modify current-code fixtures.

## 9. Add Local Workflow Execution Acceptance

- [x] 9.1 Define and test the versioned `temporal-workflow-execution.json` schema with redacted service, namespace, queue, Workflow type, Workflow ID, run ID, terminal state, duration, and diagnostic fields.
- [x] 9.2 Implement a dedicated local Temporal canary harness that reads the canonical inventory and starts every advertised Workflow directly with isolated fixture identifiers.
- [x] 9.3 Define prerequisite setup through service-owned boundaries, current contract version, stable idempotency key, explicit Workflow ID conflict/reuse policy, timeout, expected terminal state, and cleanup for every canary.
- [x] 9.4 Run the direct execution matrix after infrastructure readiness in `dev-smoke`, permit only dependency-safe parallelism, and fail on unknown types, missing Activities, panic, timeout, or unexpected terminal state.
- [x] 9.5 Bind both worker-infrastructure and Workflow-execution evidence into the aggregate exact-source manifest with the same worktree digest, Compose project, namespace, and run identity.
- [x] 9.6 Add acceptance regression tests proving that poller convergence or indirect HTTP/CDC smoke cannot pass aggregate local readiness when a direct Workflow case is missing or fails.
- [x] 9.7 Reuse the same Workflow execution inventory for the local kind smoke path without adding cloud deployment or CI/CD behavior.

## 10. Synchronize Local Documentation and Status

- [x] 10.1 Update the Temporal local runbook to distinguish infrastructure readiness from execution readiness and document history export, replay review, worker lifecycle, heartbeat, and force-termination procedures.
- [x] 10.2 Update catalog architecture documentation and its owning ADR to describe the implemented multi-step rollback, frozen cursor, existing `GetPriceHistory` and `SetPriceHandler` boundaries, and preserved public contracts and service data ownership.
- [x] 10.3 Update local development and evidence documentation with the execution-canary matrix, artifact locations, diagnostics, cleanup, and rollback steps.
- [x] 10.4 Restore affected main-spec status annotations from `PARTIAL` only after focused replay, execution, Compose, kind, and exact-source validation evidence passes.
- [x] 10.5 Confirm the change contains no cloud topology, production security, CI/CD, image-promotion, or GitOps implementation and leaves `complete-cloud-deployment-and-cicd-readiness` active and separate.

## 11. Complete Local Verification

- [x] 11.1 Run `gofmt` on changed Go files and rerun all affected platform and service focused tests.
- [x] 11.2 Run `make compose-validate` and `make validate-agent-guidance`.
- [x] 11.3 Run the root Temporal determinism, inventory, architecture, deterministic-replay, clean-slate-preflight, and execution-evidence gates.
- [x] 11.4 From a clean local state, run `make preflight`, `make dev-up`, `make dev-smoke`, `make dev-evidence`, collect failure diagnostics if needed, and finish with `make dev-down`.
- [x] 11.5 From a clean local state, run `make kind-up`, `make kind-smoke`, retain local kind evidence and diagnostics, and finish with the documented kind teardown.
- [x] 11.6 Run `make validate-deployment` for the exact source state and retain its manifest without interpreting this local validation as cloud readiness.
- [x] 11.7 Run `make verify-pr`, separate pre-existing unrelated baseline failures from regressions, and resolve every failure caused by this change.
- [x] 11.8 Run `openspec validate --strict --all`, verify the completed change against its proposal, design, specs, and tasks, and record the final spec-sync assessment before archive.

## 12. Close Post-Verification Gaps

- [x] 12.1 Repair order, notification, customer, and reporting production workers so every canonical Workflow registration declares Auto Upgrade, registration aliasing is disabled, duplicate checks remain enabled, shutdown is bounded, and fatal polling errors reach the owning runtime.
- [x] 12.2 Propagate catalog rollback `RequestedAt` through discovery and the query/repository boundary so the initial opaque cursor freezes that exact cutoff and later cursors remain authoritative; add focused regression coverage.
- [x] 12.3 Place a read-only clean-slate one-shot gate between namespace bootstrap and every current-only local worker, add clean/stale negative controls, and run the determinism negative control from the canonical root Temporal target.
- [x] 12.4 Strengthen the canonical inventory validator to compare production registration calls, explicit Workflow versioning, worker safety options, duplicate-check policy, canonical Activity registrations, and Workflow source identities; prove representative mismatches fail.
- [x] 12.5 Extend the local termination integration test to assert Terminated status and the operator reason in Event History, and run it through canonical Compose smoke.
- [x] 12.6 Regenerate affected current-code replay evidence when required, rerun focused and repository-wide gates, retain exact-source local/deployment evidence, and verify the change is archive-ready.

## Final Spec-Sync Assessment

- All five delta specs validate strictly and remain required for the eventual
  sync/archive: `platform-verification`,
  `per-service-temporal-registration`, and
  `platform-temporal-versioning`, `architecture-test-expansion`, and
  `platform-hexagonal-enforcement`.
- The deltas contain eight added and eleven modified requirements. Their
  change-only requirements are not yet fully present in the main specs, so the
  archive workflow must sync all three deltas rather than treating the restored
  local status annotations as a complete spec sync.
- No delta conflict is known. Cloud deployment and CI/CD requirements remain in
  the separate active `complete-cloud-deployment-and-cicd-readiness` change.

## 13. Close Architecture-Gate and Traceability Gaps

- [x] 13.1 Correct customer and catalog architecture checks so domain purity
  may inspect transitive dependencies while application infrastructure rules
  inspect direct source imports and still reject owned adapter imports.
- [x] 13.2 Add a service-filtered canonical Temporal inventory check and make
  all eight service architecture suites run real worker-versioning and
  upstream determinism verification through their existing `verify-pr` gates.
- [x] 13.3 Remove stale customer, catalog, notification, and reporting Temporal
  deferrals and update their verification traceability to the implemented
  architecture tests.
- [x] 13.4 Add coherent delta requirements for
  `architecture-test-expansion` and `platform-hexagonal-enforcement` so archive
  sync removes obsolete no-worker claims and records the Temporal
  orchestration boundary.
- [x] 13.5 Run platform verification, all eight focused architecture suites,
  affected service `verify-pr` gates, root Temporal verification, strict
  OpenSpec validation, and exact-source documentation/deployment evidence
  checks.
