# Local Compose Operational Readiness

## Purpose

Define the evidence-backed full-stack Compose readiness gate and distinguish it
from focused local acceptance pilots.

## Requirements

### Requirement: Full local operational readiness is evidence-backed

The canonical local readiness gate SHALL start an isolated full Compose project,
wait for all required service healthchecks and one-shot initializers, execute
real HTTP, Temporal/Nexus, Postgres, and Kafka operations, and write a
machine-readable manifest containing image identities, health state, workflow
results, replay results, side-effect counts, connector/task state, topic
metadata, and failure diagnostics.

#### Scenario: Full local gate passes

- **WHEN** all required services converge and representative real operations complete within their thresholds
- **THEN** the gate exits zero, marks the manifest passed, and retains the exact project and image evidence

#### Scenario: Health-only stack is incomplete

- **WHEN** a required role is absent, a one-shot initializer exits non-zero, or a real operation cannot be observed end to end
- **THEN** the gate exits non-zero and records the failed role, operation, and diagnostics

#### Scenario: Cleanup is scoped

- **WHEN** the operator runs normal shutdown after verification
- **THEN** only the isolated project is stopped and unrelated Compose projects, images, and volumes remain untouched

### Requirement: Focused Nexus acceptance remains separately labeled

The local Nexus pilot SHALL remain runnable without the full eight-service
stack, but its manifest MUST identify itself as focused acceptance and MUST
not be accepted as full local operational readiness.

#### Scenario: Focused pilot passes

- **WHEN** the synthetic Nexus caller and HTTP idempotency cohort pass
- **THEN** the focused manifest records both cohorts and their side-effect counts with a focused status

#### Scenario: Full readiness is requested from focused evidence

- **WHEN** an operator attempts to use a focused manifest as the full-stack readiness input
- **THEN** validation rejects it and requires the full operational manifest

### Requirement: Testcontainers ecosystem evidence remains supplemental

Testcontainers service-integration and focused-ecosystem manifests SHALL remain
supplemental to the canonical eight-service Compose readiness manifest. The
full local readiness gate MUST continue to render and start the complete
repository topology, verify every required role and initializer, execute its
cross-service operations, retain exact image and project evidence, and perform
its ownership-aware cleanup. A Testcontainers-managed subset MUST NOT satisfy
the canonical full-stack requirement.

#### Scenario: Focused Testcontainers Shipping cohort passes

- **WHEN** the focused Shipping cohort passes all HTTP, Nexus, PostgreSQL, Kafka, Debezium, and Temporal assertions
- **THEN** its manifest is accepted as `focused-ecosystem` supplemental evidence
- **AND** full local readiness still requires a separate passing `canonical-full-stack` manifest

#### Scenario: Full readiness receives only service integration evidence

- **WHEN** an operator supplies one or more `service-integration` manifests without a canonical full-stack manifest
- **THEN** full-readiness validation exits non-zero and reports the missing evidence class

#### Scenario: Canonical and focused evidence disagree

- **WHEN** focused evidence passes but the canonical Compose gate reports a missing role, failed initializer, broken cross-service operation, or cleanup failure
- **THEN** local operational readiness remains failed
- **AND** both evidence results are retained without promoting the focused result

#### Scenario: Canonical Compose lifecycle is unchanged

- **WHEN** the Testcontainers verification capability is rolled back or unavailable
- **THEN** `make local-operational-readiness` remains independently runnable with its existing full-stack ownership, evidence, diagnostics, and cleanup contract

### Requirement: Focused Compose parity is validated at the same source revision

A Testcontainers-managed Compose cohort SHALL identify the exact repository
Compose files, environment pins, source revision, selected services, build
contexts, and local image identities it uses. The repository MUST retain a
parity check that rejects missing required overlays, unexpected service
definitions, omitted one-shot initializers, build-context drift, local-image
provenance drift, or identity drift between the focused cohort and the direct
Compose configuration for the same revision.

#### Scenario: Focused cohort resolves expected topology

- **WHEN** the focused Shipping cohort renders its Compose stack
- **THEN** the retained topology includes the expected base, Shipping, Nexus, and evidence inputs at the exact source revision

#### Scenario: Required overlay is omitted

- **WHEN** a focused cohort is configured without an overlay required by its declared assertions
- **THEN** parity validation exits non-zero before the cohort is accepted

#### Scenario: Testcontainers and direct Compose use different pins

- **WHEN** the focused Testcontainers stack and direct Compose rendering resolve different image references for the same required service
- **THEN** parity validation fails and identifies the service and both references

#### Scenario: Focused build context or initializer differs

- **WHEN** the focused Testcontainers model uses a different build context, local image source revision, or one-shot initializer result than direct Compose rendering
- **THEN** parity validation fails before behavioral evidence is accepted
- **AND** the manifest identifies the affected service or initializer
