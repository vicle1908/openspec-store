# platform-verification Specification

## Purpose
The platform implements Normative scenarios have automated evidence Every normative scenario in this change SHALL map to at least one stable verification ID in a machine-readable traceability manifest. Each entry SHALL identify the owning capability, test tier, executable c
## Requirements
### Requirement: Normative scenarios have automated evidence

> **Status**: IMPLEMENTED. Traceability manifest exists; normative scenarios mapped to verification IDs.

Every normative scenario in this change SHALL map to at least one stable verification ID in a machine-readable traceability manifest. Each entry SHALL identify the owning capability, test tier, executable command or test name, required environment, and evidence artifact. A scenario SHALL NOT be considered implemented when its mapped verification is missing, skipped without an approved exception, or failing.

#### Scenario: Implementation task is completed
- **WHEN** a task claims to implement a normative requirement
- **THEN** its mapped verification IDs pass and their evidence is linked from the task or CI run

### Requirement: Pull requests pass deterministic fast gates

> **Status**: IMPLEMENTED. CI gates exist for formatting, architecture, tests, Buf lint, migration parsing.

Every pull request SHALL pass formatting, generated-code cleanliness, dependency and architecture checks, Buf lint and breaking checks, migration parsing, unit tests, race-enabled tests for concurrent packages, and required integration tests. CI SHALL use the pinned Go toolchain, SHALL disable result caching for release-significant test runs, and SHALL publish machine-readable test and coverage output.

#### Scenario: Pull request changes command concurrency
- **WHEN** a pull request changes command handling, repository concurrency, consumer receipt handling, or worker lifecycle code
- **THEN** the relevant race-enabled and integration suites run and block merge on failure

### Requirement: Critical behavior is verified by properties and faults

> **Status**: PARTIAL. Fuzz tests exist in platform packages; fault injection may be partial.

The verification suite SHALL include table-driven invariant tests and fuzz targets for untrusted parsers and boundary validation. It SHALL inject the defined crash windows between database commit, CDC publication, workflow start, receipt transition, and Kafka offset commit. Every injected failure SHALL converge after restart without losing a committed Order event or repeating a committed business effect.

#### Scenario: Orchestrator crashes after workflow start
- **WHEN** the orchestrator starts the deterministic workflow and terminates before marking the receipt `started` or committing the Kafka offset
- **THEN** redelivery reconciles the existing workflow, marks the receipt `started`, commits the offset, and does not create a second workflow execution

### Requirement: Current contracts, clean-slate fixtures, and workflows remain deterministic

The local verification gate SHALL run the configured current-contract checks,
migrate a fresh PostgreSQL database to head, and replay every current-code
Temporal Event History fixture against the current Workflow code using Temporal
`WorkflowReplayer`. Fixtures SHALL be version controlled and MUST be updated
only through an explicit deterministic-behavior review.

A same-input Workflow test environment rerun SHALL NOT satisfy Event History
replay. The gate SHALL report replay results per service and Workflow type and
SHALL fail if an expected fixture is missing, skipped, regenerated during the
test, post-processed after export, or nondeterministic. Fixture generation SHALL
use synthetic non-sensitive local inputs so the original history bytes can
remain immutable. Clean-slate preflight SHALL fail when old local executions or
histories remain.

#### Scenario: Current code changes Workflow commands

- **WHEN** the current implementation modifies Workflow control flow, Activity invocation,
  timer, child Workflow, signal, update, Continue-As-New behavior, or Workflow
  data types
- **THEN** the current-code fixture is intentionally regenerated and replayed
  without nondeterminism before local acceptance can pass

#### Scenario: Same-input rerun is insufficient

- **WHEN** a Workflow has behavioral tests but no current-code Event History
  replay
- **THEN** the deterministic-replay gate reports replay coverage missing
- **AND** the Workflow capability remains partial

#### Scenario: Deterministic fixture changes

- **WHEN** a current-code Event History fixture is added, replaced, or removed
- **THEN** the change includes an explicit deterministic-behavior review record
  with its source Workflow type and revision
- **AND** the normal test command does not rewrite the fixture

#### Scenario: Determinism gate negative control

- **WHEN** deterministic replay verification runs
- **THEN** an intentional nondeterministic Workflow fixture is rejected by the
  configured checker
- **AND** the positive gate fails if the negative control unexpectedly passes

### Requirement: The local topology is reproducible

> **Status**: IMPLEMENTED. Smoke suite exists; Compose configuration rendered and health checks verified.

The smoke suite SHALL render Compose configuration, start the pinned stack from empty volumes, wait for health rather than fixed sleeps, verify idempotent infrastructure initialization, execute the Order creation-to-workflow path, restart with retained volumes, and tear down cleanly. Required images SHALL be checked for the target architectures before a pin is accepted.

#### Scenario: Clean checkout on arm64
- **WHEN** the smoke suite runs from a clean checkout with empty volumes on a supported arm64 host
- **THEN** all required services become healthy without emulation or manual setup and the end-to-end probe completes

### Requirement: Security verification blocks known reachable risk

> **Status**: PARTIAL. govulncheck configured; SBOM generation may be partial.

Pull requests and release candidates SHALL run `govulncheck` for reachable Go vulnerabilities, scan repository and built-image dependencies and configuration with the pinned scanner, detect committed secrets, and produce an SBOM for the release image. A release SHALL contain no unapproved reachable High or Critical vulnerability; every exception SHALL identify an owner, rationale, compensating control, and expiry date.

#### Scenario: Reachable High vulnerability is detected
- **WHEN** a scanner reports a reachable High vulnerability in the candidate application
- **THEN** the release gate fails unless a non-expired, reviewed exception is recorded

### Requirement: Performance and recovery have measurable release gates

> **Status**: PARTIAL. Performance gates defined; k6 tests may be partial.

A release candidate SHALL pass version-controlled k6 smoke and reference-load scenarios on a declared environment. The MVP reference gate SHALL sustain 25 successful create-order requests per second for five minutes with HTTP error rate below 1%, create-order latency p95 below 500 ms and p99 below 1 s, and committed-order-to-workflow-start latency p95 below 10 s with no lost events. Recovery tests SHALL verify eventual drain after broker, connector, orchestrator, worker, and database interruptions. These local reference thresholds SHALL NOT be represented as production SLOs.

#### Scenario: Reference load exceeds an asynchronous latency threshold
- **WHEN** committed-order-to-workflow-start p95 is 10 seconds or greater, an event is lost, or any k6 threshold fails
- **THEN** the release gate fails and retains request, outbox, connector, consumer, and workflow diagnostics

### Requirement: Verification evidence is reproducible and retained

> **Status**: IMPLEMENTED. Evidence recorded with commit SHA, versions, architecture; 365-day retention.

Each CI verification run SHALL record commit SHA, dirty-state indicator, tool and image versions or digests, architecture, random or shuffle seed, commands, start and end times, and pass/fail status. Release evidence SHALL include JUnit or Go JSON results, coverage, Buf reports, migration results, replay results, security reports and SBOM, Compose service state and logs on failure, and k6 summaries. Pull-request evidence SHALL be retained for at least 30 days and release evidence for at least one year.

#### Scenario: Verification failure is investigated
- **WHEN** a required gate fails
- **THEN** an engineer can identify the exact source revision, environment, command, seed, failed verification ID, and relevant diagnostics without rerunning the job

### Requirement: Phase completion is evidence gated

> **Status**: IMPLEMENTED. Phase completion requires all tasks checked and normative scenarios mapped.

A phase SHALL be complete only when all tasks are checked, every in-scope normative scenario is mapped and passing, required gates have evidence, no required test is silently skipped, and all temporary exceptions have an owner and expiry. Manual exploratory checks MAY supplement but SHALL NOT replace required automated evidence.

#### Scenario: MVP release candidate is proposed
- **WHEN** the team proposes the MVP as ready for release
- **THEN** the traceability manifest has no unmapped or failing in-scope scenario and the PR, compatibility, smoke, security, recovery, and reference-load gates all pass

### Requirement: Release gate requires rollback rehearsal

> **Status**: PARTIAL. Rollback rehearsal target exists; rehearsal execution may be partial.

A release candidate SHALL pass `make test-rollback-rehearsal` against the immediately previous release fixture before the tag can be annotated as shippable.

#### Scenario: Release tag without a passed rehearsal
- **WHEN** the release-evidence workflow runs `make test-rollback-rehearsal` and the rehearsal reports `failed` or `planned`
- **THEN** the workflow exits non-zero, the year-long artifact is NOT published, and the tag is not annotated as shippable

#### Scenario: Release tag with a passed rehearsal
- **WHEN** the release-evidence workflow runs `make test-rollback-rehearsal` and the rehearsal reports `passed`
- **THEN** the rehearsal outcome is recorded as `passed` in the evidence manifest and the tag may be annotated as shippable

### Requirement: Release-cadence workflow is version-controlled and discoverable

> **Status**: PARTIAL. Release workflow exists; version control and discoverability may be partial.

The `.github/workflows/release-evidence.yml` workflow SHALL be committed to the repository, SHALL declare its trigger, permissions, and required checks inline, and SHALL be visible in the repository's Actions tab alongside `verify.yml`.

#### Scenario: Reviewer audits the release workflow
- **WHEN** a reviewer reads `.github/workflows/release-evidence.yml` during a release-process audit
- **THEN** the workflow's `on:` trigger, `permissions:` block, retention policy, and gate list are visible without leaving the file and match the design's release-cadence decisions

### Requirement: Cross-service smoke test verifies end-to-end flow

> **Status**: IMPLEMENTED. Cross-service smoke test exists; exercises create-customer through reporting-projection.

A Phase-2 release SHALL pass the canonical cross-service smoke test that
exercises create-customer → create-product → create-order (Order calls Catalog
for price quote, Customer for reference) → process-payment (in-module stub) →
notification-fires → reporting-projection-updates. The authoritative local
entry point is `make dev-smoke`; `make dev-evidence` SHALL retain the exact
timestamped smoke report and project-bound evidence manifest.

#### Scenario: Cross-service smoke test publishes evidence under artifacts
- **WHEN** `make dev-smoke` runs successfully inside the isolated Compose project
- **THEN** it writes a passing `artifacts/verification/local/cross-service-smoke-<timestamp>.json` report containing stage results and the final projection state

#### Scenario: Compose evidence binds the exact smoke report
- **WHEN** `make dev-evidence` runs with the exact passing smoke report
- **THEN** it writes a `microservices.compose-acceptance/v1` manifest that hashes the smoke report, worker readiness, Compose state, resolved model, and image inventory

#### Scenario: Cross-service smoke test fails when any service's projection is stale
- **WHEN** any service's projection lags the expected state by more than 5000 ms
- **THEN** the smoke test fails with `cross-service projection lag: <service>=<ms>ms > 5000ms`

### Requirement: Phase 2 traceability manifest is committed before any Phase-2 code lands

> **Status**: IMPLEMENTED. Traceability manifest extended with Phase-2 entries; committed before code.

The verification manifest SHALL be extended with at least one entry per Phase-2 scenario before any service module is touched. Each entry starts at `status: planned` and flips to `status: implemented` once its target test passes.

#### Scenario: Traceability manifest has PV-100..PV-110 entries
- **WHEN** the manifest is committed alongside the first Phase-2 PR
- **THEN** the manifest contains entries for `PV-100` through `PV-110` covering the cross-service call paths in `internal/application/commands/create_order.go`

#### Scenario: Traceability manifest has PV-200..PV-260 entries
- **WHEN** the manifest is committed alongside the PR-1 (platform module) PR
- **THEN** the manifest contains at least one entry per `### Requirement` in `platform-observability`, `platform-kafka-harness`, `platform-temporal-versioning`, `platform-cache`, and `platform-hexagonal-enforcement`

### Requirement: Release evidence retention (Phase 2 extended)

> **Status**: IMPLEMENTED. Release evidence retained 365 days; PR evidence retained 30 days.

The release evidence SHALL be retained for at least one year. Pull-request evidence SHALL be retained for at least 30 days.

#### Scenario: Release tag publishes year-long evidence
- **WHEN** a `v*` tag is pushed and `.github/workflows/release-evidence.yml` runs
- **THEN** the workflow uploads `artifacts/verification/${{ github.sha }}` as a GitHub Actions artifact with `retention-days: 365`, confirmed by `grep -E 'retention-days:\s*365' .github/workflows/release-evidence.yml`

#### Scenario: Pull request publishes 30-day evidence
- **WHEN** `.github/workflows/verify.yml` runs on a pull request
- **THEN** the workflow uploads the per-SHA evidence directory as a GitHub Actions artifact with `retention-days: 30`, confirmed by `grep -E 'retention-days:\s*30' .github/workflows/verify.yml`

#### Scenario: Phase-2 platform verification runs across modules in dependency order
- **WHEN** `make verify-release` runs against the multi-module platform after PR-7 (cross-service verification gates) lands
- **THEN** the platform module's `make platform-verify` runs first, each service module's `make verify-pr` runs after the platform passes, and the LGTM overlay is brought up during `test-e2e` so every service's OTel-emitted data lands in Tempo/Mimir/Loki

### Requirement: Phase 2 cross-service verifications are mapped to the verification manifest (extended)

> **Status**: IMPLEMENTED. PV-100..PV-110 and PV-200..PV-260 mapped to commands and evidence.

The verification manifest SHALL map cross-service verifications PV-100..PV-110 (introduced by Phase 2) and platform verifications PV-200..PV-260 to concrete commands and evidence paths.

#### Scenario: PV-100 covers Order Service captures customer reference snapshot
- **WHEN** the verification manifest is built for the cross-service scope
- **THEN** `PV-100` maps to `make test-e2e::test_cross_service_order_with_customer_snapshot` with evidence `artifacts/verification/local/e2e-customer-snapshot.json`

#### Scenario: PV-200 covers OTel SDK wires up in every service
- **WHEN** the verification manifest is built for the platform scope
- **THEN** `PV-200` maps to `make platform-verify::test_observability_tracer_initialised` with evidence `artifacts/verification/local/observability-tracer.json`

#### Scenario: verify-traceability reports zero unmapped Phase-2 scenarios
- **WHEN** `go run ./cmd/verify-traceability verification/traceability.yaml` runs after the Phase-2 traceability entries are added
- **THEN** the command exits 0 with no `unmapped scenario` lines for any capability whose prefix is `platform-`, `notification-`, `customer-`, `catalog-`, or `reporting-`

### Requirement: OpenSpec validation is part of the release gate (Phase 2 extended)

> **Status**: PARTIAL. OpenSpec validation configured; strict mode enforcement may be partial.

The release gate SHALL include a step that runs `openspec validate --strict --all` and rejects the release if any active change fails validation.

#### Scenario: openspec validate --strict --all is green before release tag
- **WHEN** the release-evidence workflow runs against a `v*` tag
- **THEN** `openspec validate --strict --all` runs and the workflow fails the tag if the command exits non-zero

### Requirement: Cross-service smoke test

The cross-service smoke test SHALL exercise the scenario below before each release; the release-evidence workflow SHALL refuse to tag a release when the scenario fails.

#### Scenario: Customer row appears in reporting projection within 5 seconds

This scenario is exercised by the cross-service smoke test (`tests/cross-service-smoke/`).

### Requirement: Cross-service smoke test

The cross-service smoke test SHALL exercise the scenario below before each release; the release-evidence workflow SHALL refuse to tag a release when the scenario fails.

#### Scenario: Customer row appears in reporting projection within 5 seconds

This scenario is exercised by the cross-service smoke test (`tests/cross-service-smoke/`).

### Requirement: Cross-service smoke test

The cross-service smoke test SHALL exercise the scenario below before each release; the release-evidence workflow SHALL refuse to tag a release when the scenario fails.

#### Scenario: Customer row appears in reporting projection within 5 seconds

This scenario is exercised by the cross-service smoke test (`tests/cross-service-smoke/`).

### Requirement: Cross-service smoke test

The cross-service smoke test SHALL exercise the scenario below before each release; the release-evidence workflow SHALL refuse to tag a release when the scenario fails.

#### Scenario: Customer row appears in reporting projection within 5 seconds

This scenario is exercised by the cross-service smoke test (`tests/cross-service-smoke/`).

### Requirement: Cross-service smoke test

The cross-service smoke test SHALL exercise the scenario below before each release; the release-evidence workflow SHALL refuse to tag a release when the scenario fails.

#### Scenario: Customer row appears in reporting projection within 5 seconds

This scenario is exercised by the cross-service smoke test (`tests/cross-service-smoke/`).

### Requirement: Cross-service smoke test

The cross-service smoke test SHALL exercise the scenario below before each release; the release-evidence workflow SHALL refuse to tag a release when the scenario fails.

#### Scenario: Customer row appears in reporting projection within 5 seconds

This scenario is exercised by the cross-service smoke test (`tests/cross-service-smoke/`).

### Requirement: Cross-service smoke test

The cross-service smoke test SHALL exercise the scenario below before each release; the release-evidence workflow SHALL refuse to tag a release when the scenario fails.

#### Scenario: Customer row appears in reporting projection within 5 seconds

This scenario is exercised by the cross-service smoke test (`tests/cross-service-smoke/`).

### Requirement: Cross-service smoke test

The cross-service smoke test SHALL exercise the scenario below before each release; the release-evidence workflow SHALL refuse to tag a release when the scenario fails.

#### Scenario: Customer row appears in reporting projection within 5 seconds

This scenario is exercised by the cross-service smoke test (`tests/cross-service-smoke/`).

### Requirement: Cross-service smoke test

The cross-service smoke test SHALL exercise the scenario below before each release; the release-evidence workflow SHALL refuse to tag a release when the scenario fails.

#### Scenario: Customer row appears in reporting projection within 5 seconds

This scenario is exercised by the cross-service smoke test (`tests/cross-service-smoke/`).

### Requirement: Cross-service smoke test

The cross-service smoke test SHALL exercise the scenario below before each release; the release-evidence workflow SHALL refuse to tag a release when the scenario fails.

#### Scenario: Customer row appears in reporting projection within 5 seconds

This scenario is exercised by the cross-service smoke test (`tests/cross-service-smoke/`).

### Requirement: Cross-service smoke test

The cross-service smoke test SHALL exercise the scenario below before each release; the release-evidence workflow SHALL refuse to tag a release when the scenario fails.

#### Scenario: Customer row appears in reporting projection within 5 seconds

This scenario is exercised by the cross-service smoke test (`tests/cross-service-smoke/`).

### Requirement: Cross-service smoke test contract for each new service

The `tests/cross-service-smoke/` directory SHALL include a contract test for each of the three new services introduced by the `extract-business-domains-and-dedicated-workflow-orchestration` change. Each contract test SHALL:

1. Start the service's `*-api` container in the smoke stack.
2. Make at least one HTTP call to a write endpoint (e.g., `POST /api/v1/payments/{intent_id}/capture` for the payment contract).
3. Assert that the HTTP call returns the expected response (e.g., `200 OK` with `status: "captured"`).
4. Assert that the corresponding outbox event is published to the service's Kafka topic within 10 seconds.
5. Assert that the service's `*-worker` container's `/health/ready` returns `200 OK` during the test.

The contract test SHALL be named `Test<Service>Contract` and SHALL live in `tests/cross-service-smoke/<service>_contract_test.go`.

#### Scenario: TestPaymentContract passes

- **WHEN** the smoke stack is up and `TestPaymentContract` runs
- **THEN** the test calls `POST /api/v1/payments/{intent_id}/capture` against `payment-api:8083`
- **AND** the test asserts a `200 OK` response with `status: "captured"`
- **AND** the test asserts a `payment_capture` event on `payments.events.v1` within 10 seconds
- **AND** the test asserts `payment-worker`'s `/health/ready` returns `200 OK`

#### Scenario: TestInventoryContract passes

- **WHEN** the smoke stack is up and `TestInventoryContract` runs
- **THEN** the test calls `POST /api/v1/inventory/reservations` against `inventory-api:8084`
- **AND** the test asserts a `201 Created` response with `reservation_id`
- **AND** the test asserts an `inventory_reserved` event on `inventory.events.v1` within 10 seconds

#### Scenario: TestShippingContract passes

- **WHEN** the smoke stack is up and `TestShippingContract` runs
- **THEN** the test calls `POST /api/v1/shipments` against `shipping-api:8085`
- **AND** the test asserts a `201 Created` response with `shipment_id` and `tracking_number`
- **AND** the test asserts a `shipment_dispatched` event on `shipping.events.v1` within 10 seconds

### Requirement: Full orchestration test exercises the remote-activity saga

The `tests/cross-service-smoke/` directory SHALL include a `TestOrderFulfillmentWithRemoteActivities` test that runs the full `OrderFulfillmentWorkflow` against the real `payment-service`, `inventory-service`, `shipping-service`, and `notification-service` HTTP APIs. The test SHALL:

1. Publish an `OrderCreated` event to `orders.events.v1` via the order-service's Kafka producer.
2. Wait for the `order-orchestrator` to consume the event and start an `OrderFulfillmentWorkflow`.
3. Wait for the workflow to make four HTTP calls (one per forward activity) to the three peer services (`ValidateInventoryActivityV1`, `ProcessPaymentActivityV1`, `ReserveInventoryActivityV1`, `MarkOrderShippedActivityV1`).
4. Assert that the workflow completes successfully.
5. Force a failure (e.g., kill the payment-service container after `ProcessPaymentActivityV1` has captured the payment) and verify the workflow enters the compensation path.
6. Assert that the compensation activities make two HTTP calls (Refund Payment via `payment.Client.Refund`, Release Inventory via `inventory.Client.Release`); the saga does NOT call Cancel Shipping because `MarkOrderShippedActivityV1` has no compensation in the current workflow (per `order-temporal-workflow` and `order-remote-activities` specs).
7. Assert that the workflow completes with the compensation result.
8. Assert that the OTel trace captures the full saga as a single trace.

#### Scenario: TestOrderFulfillmentWithRemoteActivities passes end-to-end

- **WHEN** the smoke stack is up and `TestOrderFulfillmentWithRemoteActivities` runs
- **THEN** the test verifies all eight assertions
- **AND** the test completes within 60 seconds

#### Scenario: TestOrderFulfillmentWithRemoteActivities detects saga compensation failure

- **WHEN** the test kills the payment-service container mid-saga (after `ValidateInventoryActivityV1` succeeds and before `ProcessPaymentActivityV1` completes)
- **THEN** the `ProcessPaymentActivityV1` activity returns a non-retryable error (or `ErrPeerUnavailable` from the open circuit breaker)
- **AND** the workflow enters the compensation path
- **AND** the compensation activities make HTTP calls to the inventory service (Release) but NOT to the shipping service (no Cancel Shipping activity is registered in the current saga)
- **AND** the workflow completes with the compensation result

### Requirement: Replay test for the remote-activity workflow

The `services/order-service/test/compatibility/order_fulfillment_replay_test.go` file SHALL be updated to include a recorded history that contains `ActivityTaskScheduled` events for `ValidateInventoryActivityV1`, `ProcessPaymentActivityV1`, `ReserveInventoryActivityV1`, `MarkOrderShippedActivityV1` (in that order — matching the saga sequence in `services/order-service/internal/adapters/temporal/workflow.go`), with the recorded inputs matching the protobuf-generated types from the new services' `contracts/` packages. The replay test SHALL run the new workflow code against the recorded history and SHALL pass.

#### Scenario: Replay test passes against recorded remote-activity history

- **WHEN** the test framework runs the replay test with a recorded history
- **THEN** the workflow produces the same result as the recorded history
- **AND** the test passes

#### Scenario: Replay test detects non-deterministic change in remote activity order

- **WHEN** the workflow code reorders the `ReserveInventoryActivityV1` and `ProcessPaymentActivityV1` activities
- **THEN** the replay test fails with a non-deterministic-replay error
- **AND** the test output points at the file and line of the reordered activity

### Requirement: Release gate runs the full cross-service smoke test

The `.github/workflows/verify.yml` CI pipeline SHALL run the full cross-service smoke test (including the four new contract tests and the full orchestration test) before the release is published. The release SHALL be blocked if any test fails or times out. The smoke test timeout SHALL be extended from 30m to 45m to accommodate the additional tests.

#### Scenario: CI release gate runs the full smoke test

- **WHEN** a release is published
- **THEN** the CI pipeline runs `make test-e2e-up` and `cd tests/cross-service-smoke && go test -count=1 -timeout=45m -v ./...`
- **AND** the release is blocked if any test fails or times out

### Requirement: Temporal acceptance separates infrastructure and execution evidence

Local Temporal acceptance SHALL produce separate versioned evidence for
infrastructure convergence and Workflow execution. Infrastructure evidence
SHALL cover namespace bootstrap, workflow and activity pollers, Worker
Deployment name, Build ID, and routing status. Execution evidence SHALL cover
every advertised Workflow type and record its service, namespace, task queue,
Workflow ID, run ID, expected terminal state, observed terminal state, duration,
and pass/fail result.

Execution acceptance SHALL use a dedicated local Temporal canary harness that
starts each Workflow directly from the canonical inventory. Each case SHALL
declare prerequisite setup through service-owned boundaries, a stable
idempotency key, its expected terminal state, a bounded timeout, and cleanup.
Indirect HTTP smoke coverage or poller presence alone MUST NOT satisfy a direct
Workflow case.

Aggregate local acceptance SHALL fail when either evidence class fails or is
missing. Evidence SHALL redact payloads and secrets and SHALL be bound into the
exact-source Compose or deployment-validation manifest.

#### Scenario: Pollers converge but Workflow execution fails

- **WHEN** infrastructure evidence passes but any advertised Workflow returns an
  unknown type, missing Activity, panic, timeout, or unexpected terminal state
- **THEN** execution evidence records the failing Workflow and diagnostic
- **AND** aggregate local acceptance fails

#### Scenario: Every Workflow execution passes

- **WHEN** the canonical local stack is ready and the execution matrix runs with
  isolated idempotent fixtures
- **THEN** every advertised Workflow reaches its expected terminal state
- **AND** the versioned execution evidence is retained and hashed by the
  aggregate manifest

#### Scenario: Indirect smoke does not substitute for direct execution

- **WHEN** the cross-service HTTP and CDC smoke passes but an advertised
  service-owned Workflow was never started directly
- **THEN** its execution-inventory entry remains missing
- **AND** aggregate Temporal execution acceptance fails

#### Scenario: Evidence belongs to the exact source state

- **WHEN** local Temporal acceptance completes
- **THEN** both evidence files record or are bound to the same source revision
  or worktree digest, Compose project, namespace, and run identity
- **AND** evidence from a different source state cannot establish readiness

### Requirement: Temporal verification inventory covers every Workflow owner

The local verification gate SHALL maintain a single inventory of every service,
task queue, registered Workflow type, Activity type, versioning behavior,
contract version, current-code replay fixture, determinism-checker package, and
execution acceptance case. The inventory SHALL contain only canonical Activity
names and SHALL reject aliases. Adding or removing a Workflow SHALL fail
verification until every inventory dimension is updated.

#### Scenario: New Workflow lacks deterministic replay and execution coverage

- **WHEN** source registration adds a Workflow type without a current-code
  fixture or execution acceptance entry
- **THEN** the local Temporal verification gate fails
- **AND** the diagnostic identifies the missing inventory dimensions

#### Scenario: Worker omits a referenced Activity

- **WHEN** Workflow code invokes an Activity type absent from the worker's
  registration inventory
- **THEN** the architecture or execution gate fails before local readiness is
  claimed

#### Scenario: Determinism checker covers every Workflow source

- **WHEN** the root Temporal verification gate runs
- **THEN** it invokes the deterministic Workflow checker for every inventoried
  Workflow source directory
- **AND** a Workflow owner missing from checker coverage fails the gate

#### Scenario: Checker discovers zero workflows

- **WHEN** the inventory is non-empty but package loading discovers zero
  Workflow packages or Workflow functions
- **THEN** verification fails with the unresolved module roots
- **AND** an empty discovery result is never reported as clean

#### Scenario: Canonical name differs from call site

- **WHEN** an `ExecuteActivity` string or constant differs from the canonical
  registration inventory
- **THEN** verification fails with the owning service, Workflow, call-site
  name, and registered name

#### Scenario: Contract version coverage is incomplete

- **WHEN** an inventoried Activity input or output lacks current-version
  validation
- **THEN** verification fails before local execution evidence can pass

### Requirement: Repository container integration is orchestrated and retained

The repository SHALL provide a root orchestration target that runs every
required service container-integration suite and each required focused
ecosystem cohort in a deterministic order with bounded concurrency. The target
MUST retain per-service and aggregate manifests, verify their schemas and
identities, and exit non-zero for any failed, skipped, missing, stale,
cross-run, uncleaned, or non-native unapproved result.

#### Scenario: All container integration cohorts pass

- **WHEN** the root aggregate container verification target runs on a supported Docker host
- **THEN** every declared service integration suite and focused cohort completes with matching source and run evidence
- **AND** the aggregate manifest reports the exact commands, images, durations, outcomes, and cleanup states

#### Scenario: One service suite is absent

- **WHEN** the repository inventory declares a required integration suite whose command, build tag, fixture, or evidence is missing
- **THEN** root container verification exits non-zero and identifies the owning service and missing component

#### Scenario: Parallel execution exceeds its budget

- **WHEN** the configured resource or concurrency budget cannot safely run another cohort
- **THEN** orchestration queues or serializes the cohort within the declared timeout
- **AND** it does not attach to or reuse another run's resources

#### Scenario: Aggregate evidence references a failed cleanup

- **WHEN** a child manifest records failed or incomplete cleanup
- **THEN** aggregate validation fails even if the child's behavioral assertions passed

### Requirement: Container verification inventory and execution state are explicit

The root verification inventory SHALL record each suite or cohort's owner,
command, build tag, dependency set, expected evidence class, artifact path,
timeout, concurrency weight, and status as `present`, `external-only`, or
`not-configured`. Aggregate evidence MUST distinguish configured workflow
definitions from actually executed runs and MUST fail closed for required
entries that are missing, not configured, or only externally asserted.

#### Scenario: Required inventory entry has no executable command

- **WHEN** a required inventory entry has no runnable command, build tag, fixture, or evidence path
- **THEN** the aggregate target exits non-zero and identifies the incomplete entry
- **AND** no aggregate pass manifest is written

#### Scenario: Workflow is configured but not executed

- **WHEN** the repository contains the Docker-capable workflow definition but no matching hosted run artifact exists
- **THEN** local validation records the workflow as configured-but-unverified
- **AND** it does not convert that state into a passing hosted or release evidence class

### Requirement: Docker-capable CI executes container verification without implying cloud readiness

The repository SHALL declare a Docker-capable CI workflow for relevant
integration changes and manual execution. The workflow MUST use the pinned Go
toolchain, run the service integration and focused ecosystem targets, execute
their negative controls and evidence validators, and upload bounded evidence
on success or failure. The workflow definition and any local result MUST NOT be
represented as confirmed hosted execution, branch-protection enforcement, or
cloud readiness without separate retained external evidence.

#### Scenario: Relevant integration change triggers the workflow

- **WHEN** a change affects the harness, service adapters, migrations, selected Compose files, Shipping lifecycle, or evidence validators
- **THEN** the CI workflow runs the required container verification targets and publishes the per-revision artifact bundle

#### Scenario: Container verification fails in CI

- **WHEN** a required service or focused cohort fails
- **THEN** the workflow exits non-zero and uploads manifests, test output, container state, and redacted logs needed to diagnose the exact revision

#### Scenario: Workflow file exists without a hosted run

- **WHEN** reviewers can inspect the workflow definition but no matching hosted execution artifact is retained
- **THEN** the repository reports the workflow as configured but unverified
- **AND** it does not claim branch-protection, release, staging, or production readiness

#### Scenario: Default pull-request gate runs without live service fixtures

- **WHEN** the standard root pull-request verification target runs outside the container-integration workflow
- **THEN** it remains free from live infrastructure requirements
- **AND** container verification remains a separately named required check according to its declared cadence

### Requirement: Container verification scenarios are traceable

Every normative service-integration and focused-ecosystem scenario SHALL map to
a stable verification identifier, executable command or test name, required
environment, evidence class, and artifact path. A scenario MUST remain
incomplete when its verification is skipped, failing, unmapped, or supported
only by a different evidence class.

#### Scenario: Shipping focused scenario is implemented

- **WHEN** the Shipping ecosystem cohort is claimed complete
- **THEN** each dispatch, replay, conflict, concurrency, recovery, completion, cancellation, persistence, CDC, and Temporal scenario maps to passing focused evidence for the exact source revision

#### Scenario: Service integration scenario maps to full-stack smoke only

- **WHEN** a required service adapter scenario has no service-integration verification and maps only to a full-stack health or smoke result
- **THEN** traceability validation reports the adapter scenario incomplete

#### Scenario: Focused scenario maps to canonical full-stack evidence

- **WHEN** a focused cohort scenario is additionally exercised by the canonical full-stack gate
- **THEN** traceability records both evidence classes without treating either artifact as interchangeable
