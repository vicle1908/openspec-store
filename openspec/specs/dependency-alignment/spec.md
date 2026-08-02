# dependency-alignment

## Purpose

Align pgx versions across all services to v5.10.0 to ensure consistency and compatibility.

## Current State

- catalog-service: pgx v5.9.2
- order-service: pgx v5.10.0
- notification-service: pgx v5.10.0
- payment-service: pgx v5.10.0
- shipping-service: pgx v5.10.0

## Dependencies

- pgx v5.10.0 (Go module)

## Requirements

### Requirement: DA-001: pgx Version Alignment

All services SHALL use pgx v5.10.0. The catalog-service SHALL be upgraded from v5.9.2 to v5.10.0.

#### Scenario: Version Alignment
Given catalog-service at pgx v5.9.2
When the dependency is updated to v5.10.0
Then all services shall use the same pgx version
And no compatibility issues shall occur

#### Scenario: Backward Compatibility
Given catalog-service code using pgx v5.9.2 APIs
When upgraded to v5.10.0
Then all existing code shall continue to work
And no breaking changes shall be introduced

### Requirement: DA-002: go.mod Update

The `services/catalog-service/go.mod` file SHALL be updated to reference pgx v5.10.0.

#### Scenario: go.mod Update
Given `services/catalog-service/go.mod` with pgx v5.9.2
When the dependency is updated to v5.10.0
Then `go.mod` shall reference v5.10.0
And `go.sum` shall be updated accordingly

### Requirement: DA-003: Dependency Consistency

All services SHALL use the same version of shared dependencies to prevent compatibility issues.

#### Scenario: Dependency Matrix
Given multiple services with shared dependencies
When dependencies are aligned
Then all services shall use the same version of:
- pgx v5.10.0
- temporal/sdk v1.46.0
- go-redis/v9 v9.21.0
- franz-go v1.21.5

### Requirement: DA-004: Validation

The alignment SHALL be validated through:
1. `go mod tidy` completing successfully
2. Unit tests passing
3. Integration tests passing
4. No dependency conflicts

#### Scenario: Validation
Given updated go.mod files
When `go mod tidy` is run
Then it shall complete without errors
And no dependency conflicts shall be detected

### Requirement: DA-005: Rollback Capability

The alignment SHALL be reversible by reverting go.mod changes.

#### Scenario: Rollback
Given aligned dependencies
When go.mod is reverted to previous versions
Then all services shall continue to work
And no data loss shall occur
