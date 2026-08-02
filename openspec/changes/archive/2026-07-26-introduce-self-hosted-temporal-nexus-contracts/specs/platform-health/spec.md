## ADDED Requirements

### Requirement: Nexus health separates local readiness from remote dependency state

The platform health registry SHALL classify Nexus checks as local role
readiness, remote dependency health, or deployment convergence. Only a local
condition that prevents the process from serving its advertised role SHALL
make its Kubernetes readiness probe fail.

#### Scenario: Handler is locally ready

- **WHEN** the handler registration, poller, owned Task Queue, and callback
  route are operational
- **THEN** the handler role reports ready
- **AND** evidence identifies its endpoint, Service, Operation, Task Queue, and
  build without secrets

#### Scenario: Handler registration is missing

- **WHEN** a service advertises an Operation but its local handler or poller is
  absent
- **THEN** that handler role returns `503`
- **AND** the response identifies the missing local component

#### Scenario: Caller remote endpoint is unavailable

- **WHEN** an otherwise healthy caller cannot reach a remote Nexus endpoint
- **THEN** its dependency status becomes degraded and circuit/retry state is
  observable
- **AND** its readiness remains healthy when it can still accept work and
  apply its durable retry or configured fallback policy

### Requirement: Nexus deployment convergence is validated separately

Endpoint existence, declared target, authorization policy, registry drift, and
callback routability SHALL be checked by deployment validation and retained as
evidence. A failed convergence check SHALL block rollout but SHALL NOT be
misrepresented as process liveness.

#### Scenario: Endpoint target drifts

- **WHEN** the live endpoint target differs from the declared Namespace or Task
  Queue
- **THEN** deployment convergence fails with the exact drift
- **AND** running service liveness is unchanged

#### Scenario: Non-local authorization is missing

- **WHEN** staging or production lacks the declared Authorizer policy
- **THEN** deployment validation fails before the endpoint is advertised
- **AND** evidence contains no credential or token

### Requirement: Health checks are bounded and non-mutating

Every Nexus health check SHALL use a bounded timeout, redact credentials and
payloads, and SHALL NOT execute a mutating business Operation. End-to-end
non-production validation SHALL use an isolated non-mutating canary or
disposable test Operation.

#### Scenario: Routine readiness runs

- **WHEN** Kubernetes invokes a readiness endpoint
- **THEN** the check inspects local registration and bounded control-plane
  state
- **AND** it creates no Shipment, carrier dispatch, aggregate mutation, or
  outbox fact

#### Scenario: Canary fails

- **WHEN** the non-production canary cannot complete through callback routing
- **THEN** deployment acceptance fails with a redacted diagnostic
- **AND** no production business Operation was invoked
