## MODIFIED Requirements

### Requirement: Worker Versioning v2 adoption is required for all nine workers [DEFERRED]

Every Temporal worker in every service SHALL register with `UseVersioning: true`, a non-empty `BuildID`, an explicit default versioning behavior, and a service-specific Worker Deployment name. The deployment name is an operational identity independent from the stable task queue, MUST NOT contain the SDK-reserved `.` separator, and SHALL use this mapping:

- `order-service`: `order-fulfillment-v1`
- `payment-service`: `payment-capture-v1`
- `inventory-service`: `inventory-reservation-v1`
- `shipping-service`: `shipping-dispatch-v1`
- `notification-service`: `notification-dispatch-v1`
- `customer-service`: `customer-workflows-v1`
- `reporting-service`: `reporting`
- `catalog-service`: `catalog-admin-v1`

The `BuildID` SHALL be supplied by `platformtemporal.DeploymentVersion()`, which reads `PLATFORM_DEPLOYMENT_VERSION`, then `GIT_SHA`, then the local `dev` fallback. Stable task queues and workflow registration names SHALL NOT be renamed as part of this migration.

#### Scenario: All workers register valid versioned deployments

- **WHEN** the architecture and runtime checks inspect every service worker
- **THEN** each worker uses the mapped deployment name, a non-empty build ID, `UseVersioning: true`, and an explicit supported default versioning behavior
- **AND** both workflow and activity pollers are observable on every owned task queue

#### Scenario: Stable task queues are preserved

- **WHEN** deployment identities migrate from dotted values to the mapped dash-delimited values
- **THEN** existing task queues such as `payment.capture.v1`, `notification.dispatch.v1`, and `customer.purge.v1` remain unchanged

#### Scenario: Invalid deployment name fails before readiness

- **WHEN** a Worker Deployment name contains `.` or another character rejected by the pinned SDK and server
- **THEN** the worker remains unready, startup evidence records the registration error, and deployment acceptance fails

#### Scenario: Local build identity remains deterministic

- **WHEN** neither `PLATFORM_DEPLOYMENT_VERSION` nor `GIT_SHA` is set in an explicitly local development profile
- **THEN** the worker uses `BuildID: "dev"` and continues with versioning enabled
