## Why

Graphify + GitNexus codebase audit (2026-07-31) identified dead legacy config,
unused exported functions, and a missing tooling pin. These are hygiene issues
that increase maintenance surface, confuse contributors, and cause unnecessary
rebuilds.

- **ClusterMode in catalog-service**: The `2026-07-22-complete-migration-no-legacy`
  change (LCR-001) marked "Remove ClusterMode backward compatibility" as complete,
  but the config field, default, env var, and single-node `Address` field remain.
  The Redis adapter is cluster-only and never reads these fields. Dead config
  leaks into config dumps and documentation.
- **RedactValue / HashFingerprint in order-service**: Build-tag-switched
  implementations exist in `observability.go` and `observability_platform.go`
  but have zero production callers (only test assertions). The propagation
  helpers are used; the redaction functions are orphaned scaffolding from the
  platform observability migration.
- **Missing .gitnexusrc**: No `.gitnexusrc` file exists, so GitNexus rebuilds
  detect a pdg-mode mismatch every run and force a full reindex (~12 min).

## What Changes

- Remove the dead `Redis.ClusterMode` field, its default, its env var binding,
  and the legacy single-node `Redis.Address` field from catalog-service config.
- Remove `RedactValue` and `HashFingerprint` from both build-tag variants in
  order-service observability, along with their test file.
- Pin `pdg: false` in `.gitnexusrc` to prevent unnecessary full rebuilds.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. This change removes dead code and pins tooling defaults; no externally
observable behavior changes.

## Affected Boundaries

- `services/catalog-service/internal/config/` — config struct, defaults, bindings
- `services/order-service/internal/observability/` — legacy observability functions
- `.gitnexusrc` (new file) — tooling config

## Compatibility

- Backward compatible. Removed config fields have zero consumers. Removed
  functions have zero production callers. Environment variables `CATALOG_REDIS_CLUSTER_MODE`
  and `CATALOG_REDIS_ADDRESS` become no-ops (viper ignores unknown keys).

## Rollout

- Immediate. No migration needed. Config consumers that set the removed env vars
  will see no effect (viper silently ignores them).

## Rollback

- Re-add the config fields and function definitions. No data or state changes
  are involved.
