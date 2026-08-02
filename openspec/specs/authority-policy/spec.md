# authority-policy Specification

## Purpose
Defines explicit least-privilege authority and truthful bounded-execution semantics for tools that can affect the host, filesystem, or external systems.
## Requirements
### Requirement: Registration does not grant visibility

Registering a tool SHALL NOT make it visible or executable by a model unless the effective run policy separately grants its authority class.

#### Scenario: High-authority tool is registered

- **WHEN** shell, filesystem-write, network, external-search, runtime-authoring, or code-execution tooling is registered
- **THEN** it SHALL remain hidden and non-executable by default
- **AND** metadata SHALL identify its authority class and approval requirement

#### Scenario: Policy merge attempts escalation

- **WHEN** compatibility, consumer, and stage policies are combined
- **THEN** the effective policy SHALL preserve the narrowest grant unless an explicit reviewed escalation is supplied
- **AND** string aliases or duplicate registrations SHALL not widen authority

### Requirement: High-authority execution is explicitly approved

Each high-authority execution SHALL require an explicit least-privilege grant and, where policy requires human approval, an authenticated lifecycle subject and unconsumed single-use approval nonce bound to the exact normalized operation. Execution SHALL revalidate subject freshness, revocation, assurance, separation-of-duties policy, immutable policy digest, and operation identity immediately before invoking the host operation.

#### Scenario: Approved execution

- **WHEN** a run has a valid authority grant and matching authenticated operation-bound approval
- **THEN** execution SHALL enforce allowed roots, command or network scope, environment filtering, time/resource bounds, and audit correlation

#### Scenario: Missing or mismatched grant

- **WHEN** authority, approval, path, command, destination, or content identity is absent or mismatched
- **THEN** execution SHALL fail before invoking the host operation

#### Scenario: Indirect prompt injection reaches execution

- **WHEN** instructions from a document, retrieved evidence, tool output, or checkpoint attempt an invisible, denied, expired, mismatched, or unapproved high-authority invocation
- **THEN** the execution boundary SHALL reject it before host effects regardless of model behavior
- **AND** no caller-controlled content SHALL satisfy authenticated approval or widen the immutable policy

#### Scenario: Human approval is required

- **WHEN** policy requires a person to authorize a high-risk operation
- **THEN** approval SHALL use the `authenticated-lifecycle-actors` subject, freshness, nonce, replay, revocation, and separation-of-duties semantics
- **AND** caller-supplied actor text or model output SHALL never serve as approval authority

### Requirement: Bounded executor claims are truthful

A subprocess-based command tool SHALL describe itself as a bounded host executor unless it provides independently verified OS-level isolation.

#### Scenario: Bounded executor reports policy

- **WHEN** a consumer inspects or invokes the executor
- **THEN** the system SHALL expose its working-directory, environment, timeout, resource, and command restrictions
- **AND** it SHALL not claim sandbox isolation based only on regex blocklists

