## MODIFIED Requirements

### Requirement: Full local operational readiness is evidence-backed

The canonical local readiness gate SHALL start an isolated full Compose project,
wait for all required service healthchecks and one-shot initializers, execute
real HTTP, Temporal/Nexus, PostgreSQL, and Kafka operations, and write a
machine-readable manifest containing image identities, health state, workflow
results, replay results, side-effect counts, connector/task state, topic
metadata, failure diagnostics, `run_id`, and `compose_project`. The gate SHALL
bind validation and acceptance to that exact identity and SHALL reject an
artifact from another run or project. It SHALL never select a globally newest
artifact as a substitute for an explicitly named run.

#### Scenario: Full local gate passes

- **WHEN** all required services converge and representative real operations
  complete within their thresholds
- **THEN** the gate exits zero, marks the manifest passed, and retains the
  exact run ID, project, image evidence, and operation counts

#### Scenario: Health-only stack is incomplete

- **WHEN** a required role is absent, a one-shot initializer exits non-zero, or
  a real operation cannot be observed end to end
- **THEN** the gate exits non-zero and records the failed role, operation,
  identity, and diagnostics

#### Scenario: Artifact identity collides

- **WHEN** a smoke, Worker, Workflow, Shipping-pilot, or acceptance artifact
  has a missing or mismatched `run_id` or `compose_project`
- **THEN** acceptance exits non-zero and reports the exact identity mismatch
- **AND** no artifact from another run is considered evidence

#### Scenario: Cleanup failure fails closed

- **WHEN** the workload passes but project cleanup returns a non-zero status
- **THEN** the outer run exits non-zero
- **AND** the retained summary records `cleanup.status=failed` and the exact
  cleanup diagnostics

#### Scenario: Cleanup is scoped

- **WHEN** the operator runs normal shutdown after verification
- **THEN** only the owned isolated project is stopped and unrelated Compose
  projects, images, and volumes remain untouched

### Requirement: Focused Nexus acceptance remains separately labeled

The local Nexus pilot SHALL remain runnable without the full eight-service
stack, but its manifest MUST identify itself as focused acceptance and MUST
include the exact `run_id` and `compose_project` supplied by its caller. It
MUST not be accepted as full local operational readiness, and it MUST be
rejected when its identities do not match the enclosing acceptance run.

#### Scenario: Focused pilot passes

- **WHEN** the synthetic Nexus caller and HTTP idempotency cohort pass
- **THEN** the focused manifest records both cohorts, their side-effect counts,
  the exact run/project identity, and a focused status

#### Scenario: Full readiness is requested from focused evidence

- **WHEN** an operator attempts to use a focused manifest as the full-stack
  readiness input
- **THEN** validation rejects it and requires the full operational manifest

#### Scenario: Focused identity is stale

- **WHEN** the pilot manifest has a run or project identity different from the
  enclosing Compose acceptance run
- **THEN** validation rejects the pilot evidence before evaluating outcomes
