## MODIFIED Requirements

### Requirement: Self-hosted Nexus calls are authenticated

The `local-fast` Compose profile SHALL explicitly label its no-op transport
authorization as insecure and local-only. The `production-contract`, staging,
and production profiles SHALL require verified TLS identity, an explicit
ClaimMapper, an explicit Authorizer, and secret or trust injection references.
Configuration validation SHALL fail before endpoint reconciliation when any
required reference is absent or invalid.

#### Scenario: Non-local identity configuration is absent
- **WHEN** validation selects staging or production without complete identity and TLS references
- **THEN** validation fails before endpoint reconciliation
- **AND** diagnostics contain no credential or private key

#### Scenario: Local-fast callback succeeds
- **WHEN** the explicit local-fast profile invokes an advertised Operation
- **THEN** the callback may be accepted without a reusable credential
- **AND** readiness and evidence identify the insecure local-fast mode

#### Scenario: Production-contract callback is authenticated
- **WHEN** an authorized production-contract workload invokes an advertised Operation over verified transport
- **THEN** the ClaimMapper derives its caller identity and the Authorizer admits only the configured Namespace and endpoint
- **AND** the Operation reaches its expected durable provider state and evidence records non-secret identity, policy, Workflow/run, operation, outbox, and provider-effect metadata

#### Scenario: Wrong workload invokes the advertised Operation
- **WHEN** a valid workload identity without permission for the Namespace or endpoint invokes the same purposeful Operation
- **THEN** the Authorizer denies it before a handler Workflow, provider effect, or outbox fact is created
- **AND** the denial does not enter Activity retry or business compensation handling

#### Scenario: Required identity configuration is absent
- **WHEN** production-contract, staging, or production lacks complete identity, TLS, ClaimMapper, Authorizer, or trust references
- **THEN** validation fails before endpoint reconciliation
- **AND** diagnostics contain no credential or private key

### Requirement: No-op authorization is local-only

The default no-op Authorizer SHALL be allowed only when `local-fast` is
explicitly selected. Production-contract, staging, and production startup and
deployment validation SHALL fail closed when an explicit ClaimMapper or
Authorizer configuration is missing, invalid, or selects the no-op policy.

#### Scenario: Local development uses the no-op policy
- **WHEN** the local Compose profile explicitly selects the no-op Authorizer
- **THEN** startup succeeds
- **AND** readiness identifies the insecure local-only mode

#### Scenario: Production starts without an Authorizer
- **WHEN** a production Temporal deployment has no explicit authorization policy
- **THEN** startup or deployment validation fails
- **AND** no Nexus endpoint is advertised

#### Scenario: Production-contract selects no-op authorization
- **WHEN** the local production-contract profile selects the no-op Authorizer
- **THEN** startup fails before any handler becomes ready

#### Scenario: Local-fast uses the no-op policy
- **WHEN** the local-fast Compose profile explicitly selects the no-op Authorizer
- **THEN** startup may succeed
- **AND** all resulting evidence identifies the insecure local-fast mode
