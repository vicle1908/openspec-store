# Design: Complete Migration No Legacy

## Context

The platform has legacy configurations and deprecated components that need to be removed and replaced with modern equivalents. This migration uses a fresh start approach — deleting all old data and starting clean with modern versions.

### Current State
- PostgreSQL 17-alpine (running with old data)
- Temporal auto-setup (deprecated, no longer maintained)
- Legacy Redis fallback code
- Old dependency versions

### Target State
- PostgreSQL 18.4-alpine (latest stable, fresh start)
- Temporal server (latest stable, fresh start)
- No legacy code or configurations
- All dependencies at latest versions

## Goals / Non-Goals

**Goals:**
- Fresh start with PostgreSQL 18.4 (delete old data)
- Fresh start with temporalio/server (delete old workflows)
- Remove all legacy code and configurations
- Update all dependencies to latest versions

**Non-Goals:**
- Migrate data from PostgreSQL 17 to 18
- Migrate workflows from auto-setup to server
- Maintain backward compatibility with old versions
- Keep deprecated components

## Decisions

### Decision 1: PostgreSQL Fresh Start
**Chosen:** Delete old data, start fresh with PostgreSQL 18.4
**Rationale:** Simpler than migration, no data corruption risk, clean slate
**Alternatives considered:** pg_dump/pg_restore (migration), pg_upgrade (complex)

### Decision 2: Temporal Fresh Start
**Chosen:** Delete old workflows, use temporalio/admin-tools for schema setup, start fresh with temporalio/server
**Rationale:** No need to preserve old workflows, clean slate for new features, official migration path
**Alternatives considered:** Migrate data (complex), keep auto-setup (deprecated)

### Decision 2b: Admin Tools for Schema Setup
**Chosen:** Use temporalio/admin-tools to set up database schema before starting temporalio/server
**Rationale:** Official tool for database initialization, handles schema creation and migrations
**Alternatives considered:** Manual schema setup (error-prone), auto-setup (deprecated)

### Decision 3: Legacy Code Removal
**Chosen:** Remove all legacy code and configurations
**Rationale:** Clean codebase, no maintenance burden, modern patterns only
**Alternatives considered:** Keep for backward compatibility (rejected - adds complexity)

## Risks / Trade-offs

**Risk:** Data loss (intentional)
**Mitigation:** This is intentional - fresh start with no legacy data

**Risk:** Workflow loss (intentional)
**Mitigation:** This is intentional - fresh start with no legacy workflows

**Risk:** Legacy code removal breaks existing functionality
**Mitigation:** Test all services after removal, verify no dependencies

## Migration Plan

### Phase 1: PostgreSQL Fresh Start
1. Stop PostgreSQL 17 container
2. Delete old data volumes
3. Start PostgreSQL 18.4 container
4. Initialize fresh database
5. Verify all services connect

### Phase 2: Temporal Fresh Start
1. Stop temporalio/auto-setup container
2. Delete old workflow data
3. Start temporalio/server container
4. Initialize fresh workflow environment
5. Verify all workflows work

### Phase 3: Legacy Code Removal
1. Remove ClusterMode backward compatibility
2. Remove single-node Redis fallback
3. Remove deprecated configurations
4. Clean up old version references

### Phase 4: Dependency Updates
1. Update all Go modules
2. Update all Docker images
3. Remove deprecated dependencies
4. Verify all services work

## Rollback Strategy

### PostgreSQL Rollback
1. Stop PostgreSQL 18 container
2. Restore PostgreSQL 17 container
3. Restore from backup if available
4. Verify all services connect

### Temporal Rollback
1. Stop temporalio/server container
2. Restore temporalio/auto-setup container
3. Restore from backup if available
4. Verify all workflows work

### Legacy Code Rollback
1. Revert code changes from git
2. Restore deprecated configurations
3. Verify all services work
