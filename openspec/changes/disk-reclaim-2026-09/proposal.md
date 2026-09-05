# Proposal: disk-reclaim-2026-09

## Why

The machine's data volume hit 99.97% full (125 MiB free of 460 GiB) during routine
dependency upgrades, blocking installs. Emergency cleanup on 2026-09-05 (brew, go
build cache, JetBrains cache, pnpm store, Docker builder cache) recovered ~40 GiB
(49 GiB free now), but large reclaimable resources remain: ~14.6 GiB of unused
Docker images, ~2.9 GiB of orphaned Docker volumes, ~4.4 GiB of stale build cache,
and a 1.2 GiB Go module cache. The machine runs near capacity again unless the
remaining stale resources are reclaimed deliberately, with data-preserving rules
rather than blind prunes.

## What Changes

- Remove 50 orphaned **anonymous** Docker volumes (hash-named, no compose labels,
  created 2026-08-23/24 during a torn-down tdt experiment run). Anonymous-only
  prune keeps all named volumes (omniroute + tdt-local-full experiment data).
- Remove **21 explicitly listed unused Docker images** (no containers reference
  them): 4 locally-built team artifacts that are rebuildable from source
  (tdt-scheduler, agent-core, tdt-observability x2), 14 registry images that are
  re-pullable on next `docker compose up` (langfuse/lgtm/clickhouse/mlflow/
  postgres/redis/alpine/buf/minio/gitleaks/otel stacks), and 2 stale CI images
  unused for 2 years (registry:2, testcontainers/ryuk), plus 1 dangling
  untagged omniroute leftover.
- Prune stale Docker **build cache** (default prune: the 4.37 GiB reclaimable
  portion only; keeps cache in use).
- Clear the Go **module cache** (`go clean -modcache`, 1.2 GiB — re-downloads on
  demand).
- No spec impact: operational/tooling cleanup (skip_specs: true).

### Explicitly preserved (decided, not removed)

- `omniroute_omniroute-data` + `omniroute-redis-data` volumes and the 3 running
  containers (omniroute, omniroute-redis, provider-adapter) — active services.
- `omniroute:rollback-3.8.49-20260828-075010` (1.97 GiB) — the documented rollback
  image per ~/Omniroute/scripts/update.sh convention; keep the single latest.
- All 8 named `tdt-local-full_*` volumes (~2.9 GiB of experiment data: langfuse
  traces, mlflow artifacts, agent-core/mlflow postgres, lgtm, minio) — team data;
  re-deploying the stack re-pulls images but data survives only in these volumes.
- `~/jenkins_home` (1.8 GiB, untouched since Oct 2025) and
  `/Library/Developer/CoreSimulator` (11 GiB iOS simulator runtimes) — reported
  for owner decision, NOT removed by this change (user data / shared toolchain).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. (skip_specs: true — operational cleanup with no externally observable
system behavior change; services remain healthy and data volumes intact.)

## Impact

- Affected repos: none (workspace machine state only; OpenSpec store records the
  change).
- Risk: low — all removals are rebuildable/re-pullable or ephemeral state; active
  services and named data volumes are untouched; verification gates re-check
  service health and free space.
- Expected recovery: ~20 GiB (≈12.7 GiB images + ~2.9 GiB anonymous volumes +
  ~4.4 GiB build cache + 1.2 GiB go modcache).
