# Complete Migration No Legacy Proposal

## Why

The platform has accumulated legacy configurations and deprecated components that need to be removed and replaced with modern equivalents. This includes:

1. **PostgreSQL 17 → 18.4**: Migrate to latest stable with security fixes and new features
2. **Temporal auto-setup → server**: Migrate from deprecated `temporalio/auto-setup` to `temporalio/server`
3. **Remove legacy code**: Clean up deprecated configurations, old patterns, and outdated dependencies

This migration ensures the platform uses only current, supported, and secure versions with no legacy fallbacks.

## What Changes

### PostgreSQL Migration
- **BREAKING**: Migrate from PostgreSQL 17-alpine to 18.4-alpine
- Data migration from old format to new format
- Update all service configurations
- Remove PostgreSQL 17 compatibility code

### Temporal Migration
- **BREAKING**: Migrate from deprecated `temporalio/auto-setup` to `temporalio/server`
- Update docker-compose configuration
- Remove auto-setup specific configurations
- Use `temporalio/admin-tools` for setup/migration

### Legacy Code Removal
- Remove all `ClusterMode` backward compatibility code
- Remove single-node Redis fallback
- Remove deprecated configuration options
- Clean up old version references

### Dependency Updates
- Update all Go modules to latest versions
- Update all Docker images to latest versions
- Remove deprecated dependencies

## Capabilities

### New Capabilities

- `postgresql-18-migration`: Migrate PostgreSQL from 17 to 18.4 with data migration
- `temporal-server-migration`: Migrate from deprecated auto-setup to server
- `legacy-code-removal`: Remove all legacy code and configurations

### Modified Capabilities

- `platform-infrastructure`: Update all Docker images to latest versions
- `platform-cache`: Remove legacy Redis fallback code

## Impact

### Affected Code
- `deploy/tools.env` — Update all image versions
- `deploy/docker-compose.yaml` — Update Temporal configuration
- `services/*/go.mod` — Update Go dependencies
- `services/catalog-service/internal/adapters/redis/adapter.go` — Remove legacy code

### Affected Infrastructure
- PostgreSQL — Data migration from 17 to 18
- Temporal — Migration from auto-setup to server
- All services — Dependency updates

### Dependencies
- PostgreSQL 18.4-alpine (latest stable)
- Temporal server 1.31.2 (latest stable)
- All Go modules updated to latest

### Compatibility
- **BREAKING** — PostgreSQL data format change
- **BREAKING** — Temporal configuration change
- **BREAKING** — Legacy code removal

### Rollout
1. Backup all data
2. Migrate PostgreSQL data
3. Update Temporal configuration
4. Remove legacy code
5. Update dependencies
6. Deploy to staging
7. Deploy to production

### Rollback
- Restore PostgreSQL from backup
- Revert Temporal configuration
- Restore legacy code from git
