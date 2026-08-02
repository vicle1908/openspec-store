# DDD Repository Cleanup - Proposal

## Why

The microservices monorepo has accumulated structural inconsistencies that violate Domain-Driven Design principles and create maintenance burden. Duplicated packages across `platform/` and service `internal/` directories, scattered deployment configurations, and unclear contract boundaries cause confusion for developers and risk architectural drift as new services are added.

## What Changes

1. **Migrate order-service to platform health package**
   - `order-service/internal/health/` uses a different API than `platform/health/`
   - This is a REWRITE, not just import change - the Probe types are incompatible
   - `order-service/internal/runtime/healthcheck.go` uses `map[string]health.Check` (functional)
   - `platform/health/probe.go` uses `Registry` with `Check` interface
   - Service must adopt platform's `Registry`-based design

2. **Document runtime package boundaries**
   - `platform/runtime/` contains shared Fx wiring (bootstrap, config, shutdown)
   - `order-service/internal/runtime/` contains service-specific orchestration
   - This separation is intentional - document it clearly

3. **Consolidate contract ownership**
   - Move `order-service/contracts/order/` → `services/order-service/contracts/order/`
   - Remove/deprecate `order-service/contracts/platform/` re-exports
   - Document contract ownership in README per service

4. **Clarify deploy structure**
   - `order-service/deploy/` contains standalone stack (postgres, kafka, temporal, app)
   - `deploy/` contains composable overlays (intended for `-f deploy/docker-compose.yaml -f deploy/docker-compose.order-service.yaml`)
   - Both are needed; clarify intended usage in README

5. **Clarify service directory structure**
   - `order-service/` - legacy location, Phase 1 MVP service
   - `services/*/` - Phase 2+ services following new structure
   - Document this is historical, not a bug
   - Consider whether order-service should migrate to `services/` for consistency (future decision)

## Capabilities

### New Capabilities

- `package-deduplication`: Standardized approach for identifying and resolving duplicate packages across platform and services
- `deploy-consolidation`: Clarified two-layer deployment structure (standalone vs composed)
- `contract-boundaries`: Clear ownership model for Protobuf/REST contracts across platform and domain layers
- `service-directory-structure`: Documented intentional inconsistency between Phase 1 (root) and Phase 2+ (`services/`) locations

### Modified Capabilities

- `platform-health`: **Clarification** - order-service currently uses incompatible `map[string]Check` API; migration to `Registry`-based design required
- `platform-runtime`: **Clarification** - service-specific runtime wiring (Fx modules) remains in services; shared patterns documented

## Impact

**Affected Code:**
- `order-service/internal/health/` → REWRITE to use `platform/health.Registry`
- `order-service/internal/runtime/` → update health check construction
- `order-service/contracts/` → move `order/` to `services/order-service/contracts/`
- `order-service/deploy/` → clarify this is standalone stack; document when to use vs root deploy

**Migration Effort:**
- **High risk for health**: Two incompatible APIs require careful migration of all call sites
- **Low risk for contracts**: Simple file moves with import rewrites
- **Low risk for deploy**: Documentation only - structure is already correct

**Rollback Approach:**
- Git revert of code changes
- Move contracts back to original location
- No database migrations required

## Open Questions Resolved

1. **Health packages are incompatible designs** - NOT simple duplication
   - Service uses: `map[string]Check` (functional style)
   - Platform uses: `Registry` with `Check` interface
   - Migration requires: rewrite all call sites in roles.go, runtime, worker, orchestrator

2. **Deploy structure is intentional** - NOT duplication
   - Service deploy: standalone complete stack for local dev
   - Root deploy: overlay system for composed environments
   - Resolution: document intended usage, not restructure

3. **Runtime separation is intentional** - NOT duplication
   - Platform: shared infrastructure wiring
   - Service: specific to order-service orchestration
   - Resolution: document boundaries, no code changes needed
