# package-deduplication Specification

## Purpose

Standardized approach for identifying and resolving duplicate packages across platform and services. Ensures DRY principles are maintained and architectural boundaries (DDD hexagonal architecture) are respected.

## ADDED Requirements

### Requirement: Platform vs Service package ownership

The monorepo SHALL maintain clear ownership boundaries between platform packages and service packages:

- **Platform packages** (`platform/*/`) MUST contain only infrastructure-agnostic, cross-service reusable code
- **Service packages** (`*/internal/*/`) MAY contain service-specific implementations
- **Domain packages** (`*/internal/domain/`) MUST NOT depend on infrastructure packages

#### Scenario: Platform package contains only shared code
- **WHEN** a package is placed in `platform/`
- **THEN** it SHALL be importable by any service without creating circular dependencies
- **AND** it SHALL NOT contain domain logic or service-specific types

#### Scenario: Service imports platform package
- **WHEN** a service needs infrastructure functionality
- **THEN** it SHOULD import from `platform/` rather than implementing locally
- **AND** it SHALL NOT duplicate platform functionality in its own `internal/`

### Requirement: Duplicate package detection

The monorepo SHALL have documented criteria for identifying duplicates:

A package is considered a duplicate when:
1. It provides the same interface/type as an existing `platform/` package
2. It has more than 70% similarity in exported symbols with an existing package
3. It exists at both `platform/<pkg>/` and `<service>/internal/<pkg>/`

#### Scenario: Duplicate detected by file comparison
- **WHEN** `order-service/internal/health/` exists alongside `platform/health/`
- **THEN** this SHALL be flagged as a duplicate
- **AND** the service-level package SHALL be migrated to use the platform package

### Requirement: Duplicate resolution process

When a duplicate is identified, the resolution SHALL follow this process:

1. **Audit**: Determine if service package has service-specific logic not in platform
2. **If no service-specific logic**: Remove service package, update imports
3. **If service-specific logic exists**: Extract shared logic to platform, keep service-specific wrapper
4. **Verify**: Ensure all services build and pass tests after migration

#### Scenario: No service-specific logic in duplicate
- **WHEN** `order-service/internal/health/health.go` only wraps `platform/health`
- **THEN** the file SHALL be removed
- **AND** all imports SHALL be updated to use `platform/health` directly

#### Scenario: Service-specific logic in duplicate
- **WHEN** `order-service/internal/runtime/` has service-specific orchestration
- **THEN** the platform-shared components SHALL be moved to `platform/runtime`
- **AND** service-specific components SHALL remain in `order-service/internal/runtime/`
- **AND** documentation SHALL clarify the boundary

### Requirement: Prevention of future duplicates

To prevent future duplicates:

1. New shared functionality SHALL first be evaluated for placement in `platform/`
2. Before creating a new package in a service's `internal/`, developers SHALL check if `platform/` has equivalent functionality
3. Architecture tests SHALL verify that domain packages do not import infrastructure packages

#### Scenario: New service checks platform before implementing
- **WHEN** a developer needs health check functionality for a new service
- **THEN** they SHALL first use `platform/health`
- **AND** they SHALL NOT create a new `*/internal/health/` package

#### Scenario: Architecture test catches domain-infrastructure coupling
- **WHEN** a test runs architecture verification
- **THEN** it SHALL fail if any package in `*/internal/domain/` imports `platform/kafka`, `platform/temporal`, or similar infrastructure
