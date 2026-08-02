## ADDED Requirements

### Requirement: Self-hosted Nexus calls are authenticated

Local Docker Compose SHALL explicitly label its no-op transport authorization
as insecure and local-only. Configuration validation SHALL reject any
non-local profile that lacks explicit TLS, ClaimMapper, Authorizer, and
secret-injection references. Deployment of those non-local components is
deferred and SHALL NOT be claimed by this change.

#### Scenario: Local callback succeeds

- **WHEN** the explicit local-only profile invokes an advertised Operation
- **THEN** the callback is accepted without a reusable credential
- **AND** readiness and evidence identify the insecure local-only mode

#### Scenario: Non-local identity configuration is absent

- **WHEN** validation selects staging or production without complete identity
  and TLS references
- **THEN** validation fails before endpoint reconciliation
- **AND** diagnostics contain no credential or private key

### Requirement: Endpoint access is authorized by policy

The local acceptance harness SHALL enforce a deterministic caller Namespace,
endpoint, and actor-reference policy before invoking the business handler.
This application-level harness is local evidence only and SHALL NOT be
represented as a deployed Temporal server Authorizer.

#### Scenario: Authorized local caller reaches an endpoint

- **WHEN** caller identity, Namespace, and endpoint match the configured policy
- **THEN** the Nexus request is admitted
- **AND** the decision records non-secret identity and policy metadata

#### Scenario: Unauthorized local caller is denied

- **WHEN** a caller is not permitted for an endpoint
- **THEN** the local acceptance policy denies it before Operation handling
- **AND** the caller receives a non-retryable authorization failure

### Requirement: No-op authorization is local-only

The default no-op Authorizer SHALL be allowed only in explicitly local
development. Staging and production startup and deployment validation SHALL
fail closed when an explicit ClaimMapper/Authorizer configuration is missing
or invalid.

#### Scenario: Production starts without an Authorizer

- **WHEN** a production Temporal deployment has no explicit authorization
  policy
- **THEN** startup or deployment validation fails
- **AND** no Nexus endpoint is advertised

#### Scenario: Local development uses the no-op policy

- **WHEN** the local Compose profile explicitly selects the no-op Authorizer
- **THEN** startup succeeds
- **AND** readiness identifies the insecure local-only mode

### Requirement: Business authorization is re-evaluated by the provider

Temporal transport and endpoint authorization SHALL NOT substitute for
provider-owned application authorization. When an Operation requires an actor
or tenant decision, the handler SHALL derive authorization context from
verified identity metadata or a validated actor reference and SHALL enforce the
provider's policy before aggregate mutation.

#### Scenario: Transport-authorized caller lacks business permission

- **WHEN** a caller can reach the endpoint but is not allowed to dispatch the
  requested Shipment
- **THEN** the application returns a typed non-retryable business authorization
  rejection
- **AND** no provider call, aggregate mutation, or outbox fact occurs

#### Scenario: Payload attempts to forge identity

- **WHEN** an untrusted request field claims a different authenticated subject
- **THEN** the handler ignores it as an authentication source
- **AND** authorization uses verified context and audited mappings

### Requirement: Local Nexus payload conversion is compatible

Local callers and handlers SHALL use the same explicitly named default
Temporal Data Converter profile. Local deployment validation SHALL reject a
profile mismatch before rollout and SHALL avoid logging opaque payloads.
Non-local encryption codecs, key rotation, and historical encrypted-payload
replay are deferred with the cloud identity and TLS deployment and SHALL NOT be
claimed from this local-only change.

#### Scenario: Caller and handler codecs differ

- **WHEN** a handler cannot decode the caller's protected payload version
- **THEN** deployment compatibility validation fails before rollout
- **AND** no opaque payload or key material is logged

#### Scenario: Local default converter is compatible

- **WHEN** the local caller and handler select the declared default profile
- **THEN** deployment compatibility validation succeeds
- **AND** the retained evidence identifies the profile without payload data
