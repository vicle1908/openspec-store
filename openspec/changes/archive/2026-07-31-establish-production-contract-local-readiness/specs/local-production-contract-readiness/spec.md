## Purpose

Define authoritative local readiness as production application-contract parity
with explicit laptop-scale reductions, retained security and failure evidence,
and no implication of cloud control-plane or high-availability proof.

## ADDED Requirements

### Requirement: A normalized runtime contract is the parity source of truth

The repository SHALL maintain one versioned runtime-contract inventory for all
eight services and shared dependencies. It MUST identify every deployed role,
image/build source, command, health contract, non-secret configuration class,
secret class, workload identity, dependency protocol, owned data boundary,
Kafka topics and groups, Temporal namespace and task queue, provider mode,
container policy, and required evidence. Validation SHALL compare normalized
merged Compose and rendered local kind models to this inventory and SHALL fail
on missing, extra, contradictory, or insecure required fields.

#### Scenario: Compose and kind satisfy the contract
- **WHEN** the production-contract Compose model and local kind manifests are normalized
- **THEN** every required runtime invariant matches the versioned contract inventory
- **AND** technology-specific topology fields may differ only through declared reductions

#### Scenario: A deployed role is omitted
- **WHEN** a Compose service or kind workload has no matching runtime-contract role
- **THEN** validation fails and identifies the unowned role

#### Scenario: Current production overlay differs
- **WHEN** a current staging or production render has not yet adopted the contract
- **THEN** local readiness reports it as deferred downstream drift
- **AND** it does not weaken the canonical contract or cause local evidence to claim cloud readiness

### Requirement: Production-contract and local-fast profiles are unambiguous

The canonical local Compose lifecycle SHALL use the production-contract profile.
The repository MAY expose local-fast only through separately named commands and
models that label themselves insecure and non-evidentiary. A merged model MUST
contain exactly one compatible security profile and MUST fail before container
creation when secure required inputs are unresolved or an insecure override is
mixed into production-contract.

#### Scenario: Canonical startup renders production-contract
- **WHEN** a developer invokes the canonical local startup command
- **THEN** the merged model selects production-contract and contains no local-fast override

#### Scenario: Developer explicitly selects local-fast
- **WHEN** a developer invokes the separately named fast command
- **THEN** the stack may use the supported convenience behavior
- **AND** all artifacts are labeled insecure and ineligible for readiness

#### Scenario: Profiles are mixed
- **WHEN** merged configuration contains both production-contract and local-fast security inputs
- **THEN** validation fails before any container is created

### Requirement: Local credentials and PKI are ephemeral and run-scoped

Production-contract startup SHALL generate or provision unique per-run secrets,
trust roots, server identities, client identities, and dependency credentials
outside tracked source files. Secret values SHALL be mounted through secret
files, SHALL be scoped to the owned Compose project or kind run, and MUST be
redacted from rendered configuration, diagnostics, process arguments, and
evidence. Cleanup SHALL remove owned ephemeral secret material after retaining
non-secret identity and cleanup results.

#### Scenario: Two runs generate independent identities
- **WHEN** two production-contract readiness runs execute concurrently
- **THEN** they use different trust roots, credentials, project identities, and secret directories

#### Scenario: Rendered configuration is inspected
- **WHEN** production-contract Compose and kind inputs are rendered for evidence
- **THEN** they contain secret references but no reusable credential, token, private key, or complete credential-bearing DSN

#### Scenario: Cleanup fails to remove secret material
- **WHEN** owned ephemeral secret cleanup returns non-zero
- **THEN** readiness fails closed and retains a redacted cleanup diagnostic

### Requirement: Containers preserve production hardening and health behavior

Application containers in production-contract SHALL use the same canonical
image build, binary, role command, user, and health behavior intended for
non-local deployment. They SHALL run as non-root with a read-only root
filesystem, no privilege escalation, all capabilities dropped, no-new-privileges,
and bounded writable volumes or tmpfs only where declared. Infrastructure-image
exceptions MUST be explicit, minimal, and validated. Every selected image MUST
support linux/arm64 or have an approved, evidenced fallback.

#### Scenario: Hardened service role starts
- **WHEN** a production-contract API or Worker starts
- **THEN** it becomes healthy with the declared non-root and read-only policy
- **AND** its role-aware healthcheck uses an executable present in the canonical image

#### Scenario: Container requests an undeclared writable root
- **WHEN** a production-contract role requires a writable path not present in its declared volume or tmpfs set
- **THEN** startup or its health gate fails instead of disabling read-only root

#### Scenario: Image lacks required architecture
- **WHEN** a selected image lacks native linux/arm64 support and no approved fallback evidence exists
- **THEN** profile validation fails before startup

### Requirement: Local networks express least reachability

Production-contract Compose SHALL separate edge, service, data, messaging,
workflow, observability, and provider-egress traffic. Each role SHALL attach
only to the networks required by its runtime contract, host ports SHALL be
limited to declared developer entry points, and application-layer identity
SHALL remain mandatory because network membership alone is not authorization.

#### Scenario: API reaches an owned dependency
- **WHEN** a role is attached to a network required by its contract and presents an authorized identity
- **THEN** the dependency connection may succeed

#### Scenario: Unrelated role reaches a protected dependency
- **WHEN** a role lacks the required network or workload authorization
- **THEN** the connection or operation is denied before protected work executes

#### Scenario: Internal dependency is exposed on the host
- **WHEN** the normalized model publishes an undeclared PostgreSQL, Kafka, Temporal, Redis, OTLP, or internal service port
- **THEN** validation fails and identifies the exposure

### Requirement: Production-contract exercises real dependency security

The production-contract stack SHALL use the secure behavior defined by
`service-runtime-security-contract`: PostgreSQL TLS and per-service roles,
Kafka TLS/SASL and ACLs, Temporal/Nexus verified identity and authorization,
mutual-TLS internal HTTP, Redis TLS/ACLs, and verified OTLP. Bootstrap and
one-shot initialization SHALL be idempotent and MUST complete before dependent
roles become ready.

#### Scenario: Full secure dependency startup succeeds
- **WHEN** all identities, grants, ACLs, trust roots, endpoints, and policies are valid
- **THEN** every required role and initializer converges and secure operations succeed

#### Scenario: Wrong identity is supplied
- **WHEN** a role receives another role's database, Kafka, HTTP, Temporal, Redis, or OTLP identity
- **THEN** the protected operation is denied and aggregate readiness remains failed

#### Scenario: Startup is repeated for the same project
- **WHEN** secure bootstrap and service startup run again with the same owned project inputs
- **THEN** they converge without duplicating roles, grants, topics, connectors, namespaces, endpoints, or business effects

### Requirement: Provider readiness uses a networked sandbox

Production-contract Shipping readiness SHALL invoke a protocol-faithful
networked sandbox through the same provider adapter, authentication, timeout,
idempotency, unknown-outcome reconciliation, and redaction paths intended for a
real carrier. The in-process deterministic stub MUST NOT satisfy this gate.

#### Scenario: Sandbox dispatch succeeds
- **WHEN** Shipping dispatches through the configured networked sandbox
- **THEN** the provider adapter performs a network call and records one logical shipment and one outbox fact

#### Scenario: Provider response is lost after effect
- **WHEN** the sandbox applies a dispatch but the response becomes unknown to Shipping
- **THEN** retry performs provider lookup with the stable idempotency identity
- **AND** no second logical dispatch or outbox fact is created

#### Scenario: In-process stub is selected
- **WHEN** production-contract resolves the in-process stub provider
- **THEN** startup or readiness fails and identifies the invalid provider mode

### Requirement: Readiness is proven by causal business operations

The production-contract gate SHALL execute representative operations through
the same owning API, authenticated peer, Temporal/Nexus, consumer, persistence,
and provider adapters used by the deployed stack. It SHALL include a successful
fulfillment cohort, a post-payment or post-reservation compensation cohort, an
idempotent replay cohort, an unauthorized-operation cohort, and a bounded
recovery cohort. Every cohort SHALL retain a causal ledger containing its run,
project, source, contract, request, correlation, idempotency, domain aggregate,
Workflow/run/activity, outbox event, Kafka topic/partition/offset, processed
receipt, projection, provider effect, notification, trace, and before/after
durable-state identities when applicable. Missing links MUST be explicit and
MUST fail a cohort whose contract requires them.

Canonical readiness MUST NOT originate domain evidence through direct table
mutation or direct Kafka injection. Service-scoped read-only database and Kafka
inspection MAY verify durable results after an owned operation, while synthetic
probes MAY remain supplemental connector diagnostics.

#### Scenario: Fulfillment operation completes
- **WHEN** the cohort creates a customer, product and price, seeds inventory, and creates an order through owning APIs
- **THEN** Payment is captured, Inventory is reserved and confirmed, Shipping records one sandbox dispatch, Order reaches its expected terminal state, the exact notification is delivered, and Reporting contains the expected projected fields
- **AND** the causal ledger links every required effect to the originating order operation

#### Scenario: Fulfillment compensates after Shipping failure
- **WHEN** the networked sandbox induces the selected failure after Payment capture and Inventory reservation
- **THEN** Payment is refunded, Inventory is released, Order records the compensated outcome, required compensation events are delivered, and no Shipping logical effect is retained

#### Scenario: Delivery is repeated
- **WHEN** the same API idempotency key, Workflow operation identity, or admitted event is delivered again
- **THEN** the ledger records the repeated attempt and proves one logical domain, provider, notification, and projection effect

#### Scenario: Purposeful operation uses the wrong identity
- **WHEN** the same business operation is attempted with a valid but unauthorized workload identity
- **THEN** it is denied before domain mutation, outbox creation, retry or DLQ publication, Workflow effect, or provider call

#### Scenario: Operation recovers from an injected fault
- **WHEN** a required dependency restarts, a credential rotates, or the provider response becomes unknown during an in-flight operation
- **THEN** the operation either recovers within its bound with one logical effect or fails with an evidenced recoverable state
- **AND** its original correlation and idempotency identities are preserved

### Requirement: Failure and recovery behavior is part of readiness

The production-contract gate SHALL exercise bounded dependency restart,
credential or certificate replacement with process restart, invalid trust,
unauthorized operations, graceful application termination, message redelivery,
Workflow replay, and provider unknown-outcome recovery. Each recovery SHALL
preserve operation, event, offset, Workflow, and provider idempotency identities
and SHALL retain before/after evidence.

#### Scenario: Dependency restarts during an operation
- **WHEN** a required local dependency is restarted within the declared fault cohort
- **THEN** clients reconnect within the bound or readiness fails with diagnostics
- **AND** no duplicate logical business effect is reported

#### Scenario: Credential is replaced
- **WHEN** a run replaces a dependency credential and restarts the affected role
- **THEN** the old credential is denied, the new credential is admitted, and state remains consistent

#### Scenario: Application terminates gracefully
- **WHEN** an API, Worker, orchestrator, or consumer receives the supported termination signal
- **THEN** it stops accepting new work, drains or safely abandons owned work within its bound, and becomes unready before exit

### Requirement: Local reductions and excluded claims are explicit

Local production-contract MAY reduce replica count, broker count, replication
factor, failure-domain count, storage class, resource size, secret provider, and
certificate issuer only when each reduction is versioned in the runtime
contract and recorded in evidence. Local evidence MUST NOT claim cloud IAM,
managed-control-plane, autoscaling, multi-zone, multi-region, GitOps convergence,
production load, backup restoration, or production rollback readiness.

#### Scenario: Declared single-broker reduction is used
- **WHEN** local Kafka runs one broker with replication factor one
- **THEN** evidence records the reduction and still requires client security, ACL, ordering, and idempotency contracts

#### Scenario: Undeclared reduction appears
- **WHEN** a normalized model weakens a production contract without a declared local reduction
- **THEN** validation fails before readiness

#### Scenario: Local evidence is submitted as cloud proof
- **WHEN** an operator attempts to promote local evidence as staging, production, HA, or GitOps readiness
- **THEN** validation rejects the claim and identifies the missing external evidence class

### Requirement: Production-contract evidence is exact, redacted, and scoped

The readiness manifest SHALL bind the source revision, runtime-contract version,
run ID, project or cluster identity, merged model digest, image identities,
security mode, non-secret workload identities, declared reductions, health and
initializer results, positive and negative operations, fault/recovery outcomes,
provider results, diagnostics, and cleanup status. Any missing, stale,
mismatched, secret-bearing, local-fast, or cross-run artifact MUST fail the
aggregate gate. The manifest SHALL include the causal ledger for each required
operation cohort and SHALL reject a terminal status, projection row, message,
or telemetry sample that cannot be linked to that cohort's originating
operation.

#### Scenario: Aggregate gate passes
- **WHEN** every required parity, security, operation, fault, recovery, redaction, and cleanup result passes for one exact run
- **THEN** the manifest records `local-production-contract` readiness and exits zero

#### Scenario: Evidence contains a secret pattern
- **WHEN** retained evidence contains a credential, token, private key, or complete secret-bearing DSN
- **THEN** redaction validation fails the run and identifies only the artifact and secret category

#### Scenario: Fault evidence belongs to another run
- **WHEN** a recovery artifact has a different run, project, contract version, or source revision
- **THEN** aggregate validation rejects it before evaluating its outcome
