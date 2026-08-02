## ADDED Requirements

### Requirement: Nexus advertisement and handler registration are explicit

A service SHALL declare every Nexus endpoint, Service, Operation, contract
version, handler Workflow, Task Queue, and owning context it advertises. Its
owned Temporal adapter SHALL register each declared handler on the expected
Worker. A service without a Nexus declaration SHALL NOT register an implicit
handler or endpoint.

#### Scenario: Shipping handler is registered

- **WHEN** the Shipping Worker starts with `shipping.commands.v1` enabled
- **THEN** every declared Operation and handler Workflow is registered on the
  owned Task Queue
- **AND** startup evidence matches the context map and generated contract
  inventory

#### Scenario: Declaration and Worker differ

- **WHEN** an advertised Operation has no canonical handler registration or is
  registered under a different durable name
- **THEN** startup fails before readiness
- **AND** diagnostics identify the declaration and observed registration

#### Scenario: Unadvertised service starts

- **WHEN** a service has no Nexus declaration
- **THEN** its existing Workflow and Activity Worker starts normally
- **AND** no empty or implicit Nexus endpoint is created

### Requirement: Local Nexus registration controls handler readiness

Handler readiness SHALL remain false until all declared local handlers,
pollers, Worker build identity, and callback-routing prerequisites converge.
A fatal registration or callback error SHALL make the handler role unready and
stop it within the configured shutdown budget.

#### Scenario: Local poller is absent

- **WHEN** the advertised handler is registered but no local poller serves its
  Task Queue
- **THEN** the handler role returns `503`
- **AND** diagnostics identify the endpoint, Service, Operation, and Task Queue

#### Scenario: Nexus Worker stops

- **WHEN** the Worker stops or reports a fatal error after convergence
- **THEN** handler readiness returns `503`
- **AND** the runtime emits a structured shutdown or fatal-error record

#### Scenario: Remote provider is unavailable to a caller

- **WHEN** a caller Worker remains locally registered but a remote endpoint is
  unavailable
- **THEN** caller Worker readiness is based on its local ability to accept and
  durably process work
- **AND** remote availability is reported through dependency and circuit state

### Requirement: Legacy Temporal placement is inventoried and frozen

Every Temporal-using service SHALL identify whether its Workflow/Activity
wrappers live in the canonical Temporal adapter or in an approved legacy
`internal/application/orchestration` exception. A legacy exception SHALL list
its packages and SHALL NOT add Nexus imports or expand transport-facing
responsibilities.

#### Scenario: Pilot touches a legacy Shipping package

- **WHEN** the Shipping pilot modifies a Workflow, Activity wrapper, or
  registration
- **THEN** the touched code moves to or is implemented in the canonical
  Temporal adapter
- **AND** application commands remain executable through in-memory ports

#### Scenario: Unlisted legacy package imports Temporal

- **WHEN** a non-adapter package outside the approved legacy inventory imports
  a Temporal SDK subpackage
- **THEN** registration/architecture validation fails
