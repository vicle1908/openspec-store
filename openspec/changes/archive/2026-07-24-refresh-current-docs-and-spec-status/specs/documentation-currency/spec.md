## ADDED Requirements

### Requirement: Documentation references current evidence contracts
Repository documentation SHALL identify the canonical commands, artifact
schemas, service inventories, and evidence boundaries used by the current
implementation. A dated value or readiness statement MUST identify its source
artifact and MUST NOT silently substitute a legacy command or path.

#### Scenario: Coverage documentation matches retained summaries
- **WHEN** the local verification guide publishes per-service coverage values
- **THEN** every value and its date match a passing `microservices.service-coverage/v1` summary retained by the repository

#### Scenario: Legacy smoke reference is detected
- **WHEN** documentation or a normative spec names a retired smoke command or artifact path as the readiness authority
- **THEN** the documentation consistency check fails and identifies the canonical `make dev-smoke` and exact-report contract

### Requirement: Documentation distinguishes platform and CDC service inventories
Documentation and normative specs MUST describe the eight deployable services
separately from the seven local CDC outbox owners. A service inventory change
MUST update every canonical index and affected status statement together.

#### Scenario: Eight-service topology is documented
- **WHEN** a document describes the complete platform or per-service runbook scope
- **THEN** it includes order, payment, inventory, shipping, notification, customer, catalog, and reporting

#### Scenario: Seven CDC owners are documented
- **WHEN** a document describes local Debezium outbox ownership
- **THEN** it lists order, payment, inventory, shipping, notification, customer, and catalog without requiring reporting to own an outbox

### Requirement: Readiness status is bounded by evidence level
Status annotations SHALL distinguish source-level implementation, local
acceptance, static deployment validation, and live cloud readiness. A local
manifest MUST NOT be used to claim staging, production, Argo CD, or rollback
readiness.

#### Scenario: Local evidence supports a bounded status
- **WHEN** a capability has passing local code, smoke, CDC, or deployment evidence
- **THEN** documentation may mark the corresponding local scope as implemented or locally accepted and links the retained evidence

#### Scenario: Cloud evidence is absent
- **WHEN** staging, production, or rollback evidence has not been retained for the exact source revision
- **THEN** the documentation keeps cloud readiness unverified and points to the active cloud-delivery change

### Requirement: Declared mirrored project skills remain identical
The repository SHALL maintain an explicit mirrored-skill set whose canonical
paths are under `.agents/skills` and whose mirror paths are under
`.codex/skills`. Each declared pair SHALL remain byte-for-byte identical. The
parity check MUST report the canonical and mirror paths without modifying either
file.

#### Scenario: Skill mirror is current
- **WHEN** the documentation and governance check runs
- **THEN** every declared mirrored skill has the same content hash in `.agents/skills` and `.codex/skills`

#### Scenario: Skill mirror drifts
- **WHEN** a mirrored skill differs from its canonical source
- **THEN** the check exits non-zero and identifies the skill requiring regeneration
