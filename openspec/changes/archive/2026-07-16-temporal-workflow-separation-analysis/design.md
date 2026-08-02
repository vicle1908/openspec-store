# Design: Temporal Workflow Architecture Standardization

## Overview

This design document specifies the structural changes required to standardize the Temporal workflow architecture across all microservices.

---

## Current State Analysis

### Service Structure Comparison

| Service | Workflow Location | Worker Location | Activity Pattern | Task Queue Pattern |
|---------|------------------|-----------------|-----------------|-------------------|
| order-service | internal/adapters/temporal/ | DUPLICATE (2 files) | `order.fulfillment.X.v1` | `order-fulfillment.v1` |
| payment-service | internal/application/orchestration/ | internal/runtime/ | `payment.X.activity.v1` | `payment.capture.v1` |
| inventory-service | internal/application/orchestration/ | internal/runtime/ | `inventory.X.activity.v1` | `inventory.reservation.v1` |
| shipping-service | internal/application/orchestration/ | internal/runtime/ | `shipping.X.activity.v1` | `shipping.dispatch.v1` |

---

## Target Architecture

### Standard Directory Structure

```
services/{service}/
└── internal/
    ├── adapters/
    │   └── temporal/
    │       └── client.go          # Workflow client (optional)
    ├── application/
    │   └── orchestration/
    │       ├── workflow.go       # Workflow definitions
    │       └── activities.go     # Activity implementations
    ├── runtime/
    │   └── worker.go            # Single worker definition
    └── domain/
```

### Standard Naming Conventions

#### Activity Naming
Pattern: `{service}.{operation}.vN`

| Before | After |
|--------|-------|
| `payment.capture.activity.v1` | `payment.capture.v1` |
| `inventory.reserve.activity.v1` | `inventory.reservation.v1` |
| `shipping.dispatch.activity.v1` | `shipping.dispatch.v1` |

#### Task Queue Naming
Pattern: `{service}-worker.vN`

| Before | After |
|--------|-------|
| `order-fulfillment.v1` | `order-worker.v1` |
| `payment.capture.v1` | `payment-worker.v1` |
| `inventory.reservation.v1` | `inventory-worker.v1` |
| `shipping.dispatch.v1` | `shipping-worker.v1` |

---

## Implementation Details

### 1. Remove Duplicate Worker

**File to Delete**: `services/order-service/internal/adapters/temporal/worker.go`

**Rationale**: The Fx-based worker in `internal/runtime/worker.go` is the standard pattern. Having two workers polling the same queue causes race conditions.

### 2. Move Workflow Files

**Files to Move**:
- `internal/adapters/temporal/workflow.go` → `internal/application/orchestration/workflow.go`
- `internal/adapters/temporal/activities.go` → `internal/application/orchestration/activities.go`

**Import Updates Required**:
- Update package imports in moved files
- Update any external references to these files

### 3. Standardize Naming

Update all services to use:
- Activity names: `{service}.{operation}.vN`
- Task queues: `{service}-worker.vN`

---

## Rollback Plan

If issues arise:

1. `git checkout` to revert changes
2. Verify Temporal server is running
3. Restart affected services

---

## Dependencies

- Temporal server must be running
- All services must have go.mod properly configured
