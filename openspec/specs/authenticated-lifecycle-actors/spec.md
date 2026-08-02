# authenticated-lifecycle-actors Specification

## Purpose
Defines trusted actor resolution and auditable authorization for approval, denial, and resume actions that cross process boundaries.
## Requirements
### Requirement: Trusted actor resolution

Lifecycle actions SHALL resolve an authenticated subject from a configured, reviewed host-native identity boundary and SHALL NOT treat caller-supplied display text as authority. The provider-neutral resolver SHALL verify a short-lived assertion against an explicitly configured adapter identity, trust-root identifier, audience, nonce, and policy generation. When no production adapter or trust root is ratified, lifecycle actions SHALL fail closed; this change SHALL NOT invent a broker identity or substitute the OS username.

#### Scenario: Authenticated subject resolves

- **WHEN** a caller requests an approval, denial, or resume action
- **THEN** the resolver SHALL return a `tdt.subject.v1` normalized subject, issuer, adapter and normalization versions, assurance level, authentication time, expiry, revocation/policy generation, and evidence handle
- **AND** authorization SHALL evaluate that resolved result against the pending operation

#### Scenario: Caller supplies an actor string

- **WHEN** a caller supplies an arbitrary actor name or identifier
- **THEN** the value SHALL be non-authoritative diagnostic metadata only
- **AND** it SHALL not change the authenticated subject or policy decision

#### Scenario: Identity is missing or stale

- **WHEN** identity is missing, expired, revoked, too old for the operation, ambiguous, signed by an untrusted broker key, produced by an unavailable or unratified adapter, or cannot be verified
- **THEN** the lifecycle action SHALL fail before state mutation
- **AND** the audit record SHALL contain a redacted failure reason without credential values

#### Scenario: Production identity provider is unavailable

- **WHEN** no ratified host adapter, broker endpoint, trust-root identifier, revocation generation, or policy generation is configured
- **THEN** the resolver SHALL return a typed identity-unavailable result before authorization
- **AND** caller text, process ownership, environment values, or the current OS username SHALL not satisfy authentication

#### Scenario: Authentication becomes stale before mutation

- **WHEN** a previously valid assertion no longer satisfies freshness, revocation, assurance, or policy-generation requirements at the final mutation or resume boundary
- **THEN** the operation SHALL reauthenticate or fail closed before continuation
- **AND** no prior prepare-time decision SHALL bypass that final revalidation

### Requirement: Replay-bound authorization

An authorization decision SHALL bind the authenticated subject to the exact pending request, repository, operation, normalized path, content digest, expiry, policy version, and a cryptographically unpredictable single-use nonce issued for that operation.

#### Scenario: Valid continuation

- **WHEN** a separately started process presents the same pending identity and a valid authenticated subject
- **THEN** the final mutation boundary SHALL atomically consume the nonce, revalidate the subject/session and immutable operation digest, and record the action exactly once before continuation MAY proceed

#### Scenario: Replay or mismatch

- **WHEN** a request is expired, already terminal, has a used or mismatched nonce, or differs in repository, operation, path, digest, subject, assurance, or policy generation
- **THEN** continuation SHALL fail closed and no successful approval event SHALL be recorded

### Requirement: High-risk separation of duties

Policy SHALL designate high-risk lifecycle operations and SHALL require an authenticated approver distinct from the initiating subject unless a reviewed, operation-specific exception is recorded before the request is created.

#### Scenario: Initiator attempts high-risk self-approval

- **WHEN** the initiating subject attempts to approve a designated high-risk shell, code-execution, external mutation, or protected filesystem-write operation
- **THEN** authorization SHALL fail before the approval nonce is consumed
- **AND** audit evidence SHALL record only the redacted separation-of-duties reason and safe subject identifiers

