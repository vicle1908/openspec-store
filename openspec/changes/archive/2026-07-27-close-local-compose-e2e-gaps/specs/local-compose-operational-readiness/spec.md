## ADDED Requirements

### Requirement: Full local operational readiness is evidence-backed

The canonical local readiness gate SHALL start an isolated full Compose project,
wait for all required service healthchecks and one-shot initializers, execute
real HTTP, Temporal/Nexus, Postgres, and Kafka operations, and write a
machine-readable manifest containing image identities, health state, workflow
results, replay results, side-effect counts, connector/task state, topic
metadata, and failure diagnostics.

#### Scenario: Full local gate passes

- **WHEN** all required services converge and representative real operations
  complete within their thresholds
- **THEN** the gate exits zero, marks the manifest passed, and retains the
  exact project and image evidence

#### Scenario: Health-only stack is incomplete

- **WHEN** a required role is absent, a one-shot initializer exits non-zero, or
  a real operation cannot be observed end to end
- **THEN** the gate exits non-zero and records the failed role, operation, and
  diagnostics

#### Scenario: Cleanup is scoped

- **WHEN** the operator runs normal shutdown after verification
- **THEN** only the isolated project is stopped and unrelated Compose projects,
  images, and volumes remain untouched

### Requirement: Focused Nexus acceptance remains separately labeled

The local Nexus pilot SHALL remain runnable without the full eight-service
stack, but its manifest MUST identify itself as focused acceptance and MUST
not be accepted as full local operational readiness.

#### Scenario: Focused pilot passes

- **WHEN** the synthetic Nexus caller and HTTP idempotency cohort pass
- **THEN** the focused manifest records both cohorts and their side-effect
  counts with a focused status

#### Scenario: Full readiness is requested from focused evidence

- **WHEN** an operator attempts to use a focused manifest as the full-stack
  readiness input
- **THEN** validation rejects it and requires the full operational manifest
