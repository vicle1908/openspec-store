## ADDED Requirements

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
