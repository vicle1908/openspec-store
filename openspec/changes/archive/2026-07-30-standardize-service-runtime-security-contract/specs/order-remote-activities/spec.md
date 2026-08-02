## MODIFIED Requirements

### Requirement: Peer URLs are configurable via env vars

The Order peer configuration SHALL provide Payment, Inventory, and Shipping
service URLs and per-peer timeouts. Production-contract and strict modes SHALL
require secure URLs plus complete caller identity and peer-trust references,
and SHALL fail before Worker polling when any required input is absent. Only
local-fast MAY warn and select the preserved in-process fallback when a peer URL
is empty. Peer security configuration MUST NOT change activity inputs,
idempotency keys, compensation order, or trace propagation.

#### Scenario: Worker starts with authenticated peers
- **WHEN** the order-worker starts in production-contract mode with complete Payment, Inventory, and Shipping peer security inputs
- **THEN** it constructs remote clients and begins polling only after configuration validation passes

#### Scenario: Authenticated fulfillment operation crosses peers
- **WHEN** an Order fulfillment Workflow invokes Payment capture, Inventory reserve or confirm, and Shipping dispatch through authenticated remote activities
- **THEN** each provider authorizes the Order Worker identity and records its exact durable state, outbox fact, and correlation or operation identity
- **AND** the resulting fulfillment evidence is linked to the originating Order

#### Scenario: Wrong peer caller invokes fulfillment command
- **WHEN** a valid but unauthorized workload identity invokes the same Payment, Inventory, or Shipping command
- **THEN** the provider denies it before aggregate mutation, outbox creation, business retry, or external provider effect

#### Scenario: Worker lacks a production peer URL
- **WHEN** the order-worker starts in production-contract or strict mode with an empty required peer URL
- **THEN** it exits non-zero before polling or executing an Activity

#### Scenario: Worker lacks peer trust
- **WHEN** a secure peer URL is configured without its required trust or caller identity reference
- **THEN** configuration validation fails before an HTTP request is attempted

#### Scenario: Worker fails fast on missing peer URL in production
- **WHEN** the `order-worker` container starts with `DEPLOYMENT_ENV=prod` and `ORDER_PAYMENT_URL=` (empty)
- **THEN** the worker exits with a non-zero status and prints `FAIL: missing ORDER_PAYMENT_URL in production`

#### Scenario: Worker falls back to in-process stub in local dev
- **WHEN** the `order-worker` container starts with `DEPLOYMENT_ENV=local` and `ORDER_PAYMENT_URL=` (empty)
- **THEN** the worker prints a warning and continues with the `localFulfillmentActivities` adapter

#### Scenario: Worker falls back only in local-fast
- **WHEN** the order-worker starts in local-fast with an empty peer URL
- **THEN** it emits an insecure local-fast warning and may select `localFulfillmentActivities`
- **AND** its evidence cannot satisfy production-contract readiness

### Requirement: The localFulfillmentActivities adapter is preserved as a fallback

The preserved `localFulfillmentActivities` adapter SHALL remain a deprecated
soft-rollback path selectable only in local-fast. Production-contract, staging,
and production MUST use the authenticated remote adapter and MUST fail closed
instead of selecting the in-process fallback. Selecting the fallback SHALL not
alter recorded Workflow history or public activity contracts.

#### Scenario: Soft rollback is selected in local-fast
- **WHEN** an operator explicitly selects local-fast and omits all three peer URLs
- **THEN** the order-worker uses `localFulfillmentActivities`
- **AND** the saga compensation graph runs in-process without readiness claims

#### Scenario: Soft rollback via env var
- **WHEN** the operator sets empty peer URLs in the compose overlay
- **THEN** the `order-worker` uses `localFulfillmentActivities` instead of `remoteFulfillmentActivities`

#### Scenario: Fallback is requested in production-contract
- **WHEN** production-contract configuration would select `localFulfillmentActivities`
- **THEN** startup fails before the Worker polls its task queue
