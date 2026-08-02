## ADDED Requirements

### Requirement: Temporal namespace bootstrap precedes workers

Every self-hosted Temporal deployment SHALL register each configured application namespace idempotently after the Temporal frontend becomes ready and before any service worker starts. Schema creation alone MUST NOT satisfy this readiness condition.

#### Scenario: Missing default namespace is created

- **WHEN** the Temporal database schemas and frontend are ready but the configured `default` namespace is absent
- **THEN** the namespace initializer creates `default` with the configured retention period and exits zero only after it can describe the namespace

#### Scenario: Existing namespace is preserved

- **WHEN** the configured namespace already exists with valid settings
- **THEN** the namespace initializer exits zero without deleting the namespace or changing workflow history

#### Scenario: Namespace bootstrap failure blocks workers

- **WHEN** the namespace cannot be described or created within the bounded retry period
- **THEN** the initializer exits non-zero, Temporal-dependent workers do not start, and diagnostics include the Temporal address, namespace, and final error

### Requirement: Worker convergence is part of deployment readiness

A deployment SHALL be considered Temporal-ready only when every required service worker has connected to its configured namespace, registered its workflow and activity set, and reported readiness on its owned task queue.

#### Scenario: All service workers converge

- **WHEN** the full eight-service deployment completes startup
- **THEN** all required task queues are observable and every required worker readiness endpoint returns success within the deployment timeout

#### Scenario: Polling errors fail readiness

- **WHEN** a worker repeatedly receives namespace, task-queue, or server polling errors
- **THEN** that worker remains unready, the deployment readiness command exits non-zero, and the polling error is retained in evidence

### Requirement: Worker deployment identity is valid and independent from task queues

Every versioned worker SHALL retain its existing task-queue and workflow registration names while using a service-specific Worker Deployment name that contains no SDK-reserved `.` separator. Every worker SHALL set an explicit default versioning behavior supported by the pinned Temporal Go SDK.

#### Scenario: Stable queue uses a valid deployment identity

- **WHEN** the notification worker polls task queue `notification.dispatch.v1`
- **THEN** its Worker Deployment name is `notification-dispatch-v1`, its task-queue name remains unchanged, and workflow plus activity pollers register successfully

#### Scenario: Invalid deployment identity fails readiness

- **WHEN** a worker is configured with a Worker Deployment name containing `.` or omits its default versioning behavior
- **THEN** startup or registration fails, the worker remains unready, and diagnostics identify the invalid deployment option
