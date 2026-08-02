## Why

Local Temporal acceptance currently proves that versioned workflow and activity
pollers exist on all nine task queues, but it does not prove that each advertised
workflow and activity set is registered, dependency-complete, and executable.
The gap is material: catalog registers no workflow or activity, payment,
inventory, and shipping construct zero-value activity bundles and omit
activities their workflows call, retained "replay" tests do not use Temporal
Event Histories, and the operator termination helper returns success without
calling Temporal.

This change makes the local Temporal capability truthful and executable before
the separate cloud deployment and CI/CD readiness work proceeds.

## What Changes

- Implement the catalog price-rollback flow as a real deterministic Temporal
  Workflow with registered Activities, a concrete starter, and real application
  dependencies.
- Wire payment, inventory, and shipping workers with their real command
  handlers, repositories, unit-of-work implementations, and idempotency stores;
  register every Activity referenced by their Workflows.
- Add local execution acceptance for every advertised Workflow and owned task
  queue. Poller presence remains an infrastructure check, while successful
  Workflow execution becomes a separate readiness result.
- Replace same-input re-execution tests described as replay tests with Temporal
  `WorkflowReplayer` tests backed by newly generated Event History fixtures for
  the current implementation. These fixtures establish current-code
  determinism only; they are not a backward-compatibility contract.
- Reconcile the catalog price-rollback ADR with the canonical catalog
  long-running-operation capability, including multi-step semantics, ownership,
  and implementation status.
- Make canonical Activity type names, input/output contract versions, custom
  registration aliasing, and Workflow ID conflict/reuse policies explicit and
  executable. Old aliases, old payload versions, and old Workflow executions
  are outside the supported local cutover.
- Centralize validated Activity timeout, retry, and heartbeat conversion into
  SDK `workflow.ActivityOptions`; apply it consistently and require heartbeats
  only where Activities actually report progress.
- Implement the `temporal-workflow terminate` operator path with a real SDK
  call, typed Not Found handling, reason propagation, and local integration
  coverage.
- Integrate deterministic Workflow analysis into the local verification gates
  for all services that own Temporal Workflows.
- Align worker lifecycle and fatal-error propagation with the canonical runtime
  contract, and correct OpenSpec status annotations so poller convergence is not
  described as proof of executable registration.

Goals:

- Every locally advertised Workflow can be started and reaches its expected
  terminal state against the canonical Compose topology.
- Every worker registers a dependency-complete, internally consistent Workflow
  and Activity set.
- Current-code Workflow determinism is tested against clean-slate Event History
  fixtures generated after the cutover.
- Local readiness evidence distinguishes namespace, poller/routing, and
  execution results.

Non-goals:

- Cloud or managed Temporal deployment.
- Staging or production namespaces, retention, TLS, API keys, mTLS, secrets, or
  high availability.
- CI/CD image promotion, Argo CD rollout, Worker Controller adoption, or
  non-local rollback automation.
- Changing public REST, Protobuf, Kafka, or database ownership contracts.
- Retaining, replaying, draining, or migrating old local Workflow executions.
- Supporting legacy Activity aliases, legacy payload versions, or compatibility
  wrappers.

Clean-slate cutover:

- Existing task queues, Workflow type names, canonical dotted `.v1` Activity
- type names, and Worker Deployment names are the new-code baseline for this
  local cutover; they are not a promise to support prior implementations.
- Peer-service Workflows use only the canonical dotted `.v1` Activity names.
  Bare names and compatibility aliases are removed and rejected.
- The local Temporal namespace/project is required to be clean before the new
  workers start. Existing local executions and histories are not supported,
  exported, or replayed.
- Activity payloads must use the current contract version. Older payload
  versions are rejected before side effects.
- A new incompatible identity may be introduced when implementation requires
  it, but no old identity is retained solely for compatibility.

Rollout and rollback:

- Establish the clean local namespace reset and strict validation first, then
  repair workers service by service, generate current-code fixtures, and enable
  execution acceptance for the full local topology.
- Each service repair remains independently testable until the final local
  execution matrix is enabled. Rollback means reverting the uncommitted code
  change and recreating the disposable local project; it does not preserve
  legacy workers or histories.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `per-service-temporal-registration`: Require dependency-complete registration
  and successful local execution for every advertised Workflow instead of
  treating poller presence as sufficient proof.
- `platform-temporal-versioning`: Require true Event History replay,
  Workflow-specific versioning behavior, consistently converted Activity
  options, heartbeat correctness, canonical Activity identities, contract
  versioning, and a functional termination command.
- `platform-verification`: Separate Temporal infrastructure convergence from
  Workflow execution acceptance, retain machine-readable evidence for both,
  and fail closed when determinism or inventory discovery is incomplete.
- `architecture-test-expansion`: Make the Temporal-specific architecture
  categories applicable to all eight current worker owners, remove stale
  deferrals, and require each service gate to invoke the canonical inventory
  validator and upstream workflow checker.
- `platform-hexagonal-enforcement`: Clarify that direct-import boundaries,
  rather than a third-party SDK's transitive closure, determine whether
  application code imports infrastructure; admit Temporal APIs only inside the
  owned orchestration package while continuing to prohibit adapters and
  unrelated infrastructure frameworks.

## Impact

- **Services:** catalog, payment, inventory, shipping, notification, customer,
  reporting, and order worker registration, Workflow tests, Activity contract
  validation, and local fixtures.
- **Platform:** `platform/temporal`, Workflow determinism tooling, operator CLI,
  and architecture checks.
- **Local deployment:** Compose smoke/evidence scripts and possibly kind smoke
  consume the same execution matrix; task queues and deployment identities do
  not change.
- **OpenSpec and docs:** Temporal registration, versioning, verification,
  architecture-test coverage, hexagonal boundaries, runtime descriptions,
  catalog ADR/README, traceability manifests, and runbooks are corrected to
  match executable behavior.
- **Dependencies:** no new external runtime system is introduced. Temporal Go
  SDK APIs already present in the repository provide registration, Worker
  Versioning, Event History replay, retries, heartbeats, and termination.
