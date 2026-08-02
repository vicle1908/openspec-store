# OpenSpec: Temporal Workflow Architecture - Service Separation Analysis

## Purpose

Define the service-ownership and worker-lifecycle boundaries for Temporal workflows and activities.

## Requirements

### Requirement: Temporal behavior remains owned by its business service

Each service SHALL own and register its domain workflows and activities rather
than delegating them to a generic workflow service. The order service SHALL own
the fulfillment orchestration and invoke its versioned fulfillment activities;
payment, inventory, and shipping SHALL own their participant workflows and
activity implementations.

#### Scenario: Service-owned workflow registration

- **WHEN** a Temporal worker starts for order, payment, inventory, or shipping
- **THEN** it registers only the workflows and activities owned by that service on its documented task queue

#### Scenario: Fulfillment uses versioned activity contracts

- **WHEN** the order fulfillment workflow invokes payment, inventory, or shipping behavior
- **THEN** it uses the registered versioned activity names and the owning service adapters perform the remote domain calls

### Requirement: Worker construction and runtime lifecycle remain distinct

The order service SHALL keep Temporal worker construction and workflow/activity
registration in its Temporal adapter, while runtime lifecycle wiring SHALL
start and stop that worker through the service lifecycle interface.

#### Scenario: Runtime starts the registered worker

- **WHEN** the order worker process starts
- **THEN** runtime lifecycle hooks start the adapter-created worker without registering a duplicate workflow worker

## Background

## Metadata

- **id**: temporal-workflow-separation-analysis
- **status**: **completed**
- **created**: 2026-07-16
- **updated**: 2026-07-16
- **authors**: [architecture review]
- **reviewers**: [architects, platform team]
- **supersedes**: N/A
- **related**:
  - deployment-platform-strategy
  - platform-runtime

---

## Executive Summary

**Recommendation: DO NOT separate workflows into dedicated services.**

After validating the Temporal workflow architecture, the current implementation is **correct**. The initial research flagged a false positive regarding "duplicate workers" - the WorkerDriver pattern and runtime/worker.go serve different purposes and work together correctly.

---

## Validated Architecture (CORRECT ✓)

### Order-Service Temporal Structure

```
services/order-service/internal/
├── adapters/temporal/
│   ├── client.go              # Temporal workflow client
│   ├── worker.go             # WorkerDriver (creates worker, registers workflows/activities)
│   ├── workflow.go           # OrderFulfillmentWorkflow saga
│   ├── activities.go         # Activities struct (wraps domain interfaces)
│   ├── state.go              # Workflow state types
│   ├── constants.go          # Contract version constants
│   ├── validation.go          # Input validation
│   ├── contracts.go           # Request/response types
│   ├── registration.go       # Registration helpers
│   ├── interfaces.go         # OrderFulfillmentActivities interface
│   └── domain_interfaces.go  # Domain activity interfaces
└── runtime/
    └── worker.go              # Fx lifecycle hooks (uses TemporalWorkerLifecycle interface)
```

### Key Finding: NOT Duplicate Workers

| File | Purpose | Assessment |
|------|---------|------------|
| `internal/adapters/temporal/worker.go` | Creates Temporal worker, registers workflows/activities | ✅ Correct |
| `runtime/worker.go` | Fx lifecycle hooks, consumes `TemporalWorkerLifecycle` interface | ✅ Correct |

**These work together**: `WorkerDriver` implements `TemporalWorkerLifecycle`, and `runtime/worker.go` provides Fx hooks that start/stop the worker.

---

## Cross-Service Saga Pattern (CORRECT ✓)

| Service | Role | Workflows | Task Queue |
|---------|------|----------|------------|
| order-service | Orchestrator | OrderFulfillmentWorkflow | order-fulfillment.v1 |
| payment-service | Participant | PaymentCaptureWorkflow, PaymentRefundWorkflow | payment.capture.v1 |
| inventory-service | Participant | InventoryReservationWorkflow, etc. | inventory.reservation.v1 |
| shipping-service | Participant | ShippingDispatchWorkflow, etc. | shipping.dispatch.v1 |

### Saga Flow

1. Order created → `OrderFulfillmentWorkflow` starts in order-service
2. Workflow calls activities (by registered string name):
   - `ValidateInventoryActivityV1` → inventory-service
   - `ProcessPaymentActivityV1` → payment-service
   - `ReserveInventoryActivityV1` → inventory-service
   - `MarkOrderShippedActivityV1` → shipping-service
3. On failure → compensation workflows run in respective services

---

## Architecture Decision

### Option: Keep Current Architecture (RECOMMENDED)

**Pros:**
- ✅ Single ownership per service
- ✅ Co-located workflow and activities (no network hops)
- ✅ Domain models shared within service
- ✅ Standard Go/Fx patterns

**Cons:**
- None identified

### Option: Separate Workflow Services (REJECTED)

**Pros:**
- Independent scaling (minimal benefit - workflows are event-driven)

**Cons:**
- Network hop between workflow and activities
- Workflow becomes "dumb orchestrator" without domain context
- Team ownership split
- Distributed transaction complexity

**Verdict**: Not Recommended

---

## Identified Issues (Fixed)

### Issue 1: Activity Interface Clarity (RESOLVED)

**Before**: Activity method names were inconsistent with Temporal SDK patterns
**After**: 
- `Activities` struct wraps domain interfaces
- `OrderFulfillmentActivities` interface defines contract
- Domain interfaces (`InventoryActivities`, `PaymentActivities`, `ShippingActivities`) defined separately
- Backward-compatible aliases added for existing tests

### Issue 2: Import Cycle Prevention (RESOLVED)

**Before**: Risk of import cycle between adapters and domain
**After**: Clean interface hierarchy:
- `OrderFulfillmentActivities` interface in `interfaces.go`
- Domain interfaces in `domain_interfaces.go`
- `Activities` struct implements `OrderFulfillmentActivities`

---

## Verification

- [x] Build succeeds: `go build ./services/order-service/...`
- [x] Temporal tests pass: `go test ./internal/internal/adapters/temporal/...`
- [x] Activity interface properly separates domain from Temporal SDK
- [x] WorkerDriver pattern correctly implements TemporalWorkerLifecycle

---

## Conclusion

**No additional workflow-service split is required.**

The Temporal workflow architecture is correctly implemented:
1. Workflows stay with their owning service (domain ownership)
2. Activities are wrapped in a clean adapter layer
3. Saga pattern properly implemented with compensation workflows
4. Worker lifecycle correctly managed via Fx

The initial concern about "duplicate workers" was a false positive - the two files serve complementary purposes.

---

## Status

**Decision: REJECT separate workflow services**

**Rationale**: Current workflow-to-service mapping aligns with domain ownership.
Separating would introduce distributed transaction complexity without benefits.
Deployment readiness is governed separately by the deployment validation and
cloud delivery capabilities.
