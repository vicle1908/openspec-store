## ADDED Requirements

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

## MODIFIED Requirements

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
