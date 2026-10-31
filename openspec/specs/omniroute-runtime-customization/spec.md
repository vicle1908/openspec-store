# omniroute-runtime-customization Specification

## Purpose
Define evidence-backed operating boundaries for workstation customizations and independently evaluated optional capabilities without treating documentation or dependency presence as deployment proof.

## Requirements

### Requirement: Versioned Deployment and Customization Evidence
The operating record SHALL identify the source revision, deployed image identity, configuration authority, local overrides, and verification state separately, and SHALL distinguish observations from proposals and unverified capabilities.

#### Scenario: Reviewing an image with local runtime changes
- **WHEN** an operator reviews a deployed image built from upstream sources with local runtime modifications
- **THEN** the record SHALL identify both the upstream image and the modifications, without describing a clean source checkout as an unmodified running application.

#### Scenario: Evaluating an upstream update
- **WHEN** a new upstream release becomes available
- **THEN** the record SHALL preserve the previously validated identity until the candidate's compatibility is established, rather than requiring immediate parity with a moving branch.

### Requirement: Persistent Data and Recoverable Updates
The workstation deployment SHALL retain its database in the existing Docker-managed named volume and SHALL require verified backup and recovery evidence before a storage or deployment cutover.

#### Scenario: Recreating the application container
- **WHEN** the application container is recreated with the existing named volume
- **THEN** the documented procedure SHALL preserve that volume, rebind any replaced single-file host mounts, and verify retained data without claiming that the storage choice prevents every form of corruption.

#### Scenario: Failed post-deployment verification
- **WHEN** an upgrade fails a required verification gate
- **THEN** the operating record SHALL report failure, retain recovery references, and state whether rollback requires operator action; it SHALL NOT report automatic recovery or uninterrupted availability without evidence.

### Requirement: Compatibility Behavior and Patch Retirement Gates
The compatibility ledger SHALL map each local modification to its intended behavior, affected versions, verification evidence, upstream replacement status, and removal condition. Marker checks SHALL supplement rather than replace behavioral verification.

#### Scenario: Retiring one upstreamed fix
- **WHEN** a validated upstream release supplies a replacement for a local modification
- **THEN** only that modification SHALL become eligible for retirement after its behavior passes verification, and unrelated modifications SHALL remain accounted for.

#### Scenario: Missing required compatibility state
- **WHEN** a candidate deployment cannot demonstrate a required compatibility condition or a target chunk file for a required marker is absent or renamed
- **THEN** it SHALL fail closed rather than silently skipping verification, SHALL NOT be promoted as compatible, and SHALL report the failed condition explicitly.

### Requirement: Hybrid Retrieval Evaluation and Isolation
The evaluation plan SHALL compare lexical and semantic retrieval using the same authorized query set and corpus, including embedding generation, filtering, ranking, reranking, and fallback costs where applicable. It SHALL retain the existing hybrid deployment until an alternative satisfies the documented acceptance criteria and receives cutover approval.

#### Scenario: Comparing local and external vector backends
- **WHEN** an evaluator compares supported local hybrid retrieval with Qdrant-backed retrieval
- **THEN** the report SHALL include relevance, end-to-end latency, resource use, configuration, and sample conditions; isolated keyword-query timings SHALL NOT be presented as equivalent semantic-search performance.

#### Scenario: Deleted, expired, or differently owned memories
- **WHEN** retrieval evaluates deleted or expired records or records outside the caller's authorized owner scope
- **THEN** those records SHALL NOT appear in returned candidates or injected context, including on fallback paths.

#### Scenario: Vector backend failure
- **WHEN** an evaluated vector backend fails or has no usable vectors
- **THEN** the report SHALL identify the fallback actually used and its quality impact rather than counting lexical fallback as successful semantic retrieval.

### Requirement: Independent Optional Capability Readiness
Optional capabilities SHALL be assessed independently against a named use case, supported deployment path, prerequisites, security boundary, resource budget, and observable acceptance criteria. Unverified candidates SHALL NOT be described as enabled or production-ready.

#### Scenario: Installed dependency without runtime assets
- **WHEN** an ML or browser package resolves but its required model assets or executable is absent
- **THEN** readiness SHALL remain unverified until the required execution succeeds through the supported runtime path.

#### Scenario: Optional pack installation source
- **WHEN** an optional pack installation procedure is documented
- **THEN** it SHALL distinguish indexed local pack archives from registry package installation and SHALL identify whether the operation targets the host, desktop application, or container.

#### Scenario: Selecting an optional extension
- **WHEN** one optional extension is selected for evaluation
- **THEN** its activation SHALL NOT require unrelated extensions merely because they were grouped into an enterprise profile.

### Requirement: Relay Backend Boundary and Failure Semantics
The Bifrost evaluation record SHALL limit its integration claims to supported relay routes, distinguish native inference processing from relay forwarding, and describe fallback by failure class and selected mode.

#### Scenario: Native coding-agent request
- **WHEN** a client uses the ordinary native inference surface
- **THEN** enabling a relay backend SHALL NOT be reported as proof that the request used Bifrost or preserved native features through Bifrost.

#### Scenario: Relay failure before or after output begins
- **WHEN** an evaluated relay backend encounters a transport error, an upstream HTTP error, or a partial-stream failure
- **THEN** evidence SHALL identify which cases return errors, permit fallback, or cannot be transparently replayed, without promising automatic retry for all failures.
