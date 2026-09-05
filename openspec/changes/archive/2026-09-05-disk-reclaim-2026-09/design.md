# Design: disk-reclaim-2026-09

## Context

Machine: shared dev box (8 users, ~/Developer multi-repo workspace, OmniRoute
gateway in Docker Desktop, tdt observability experiments). Data volume 380 GiB
used / 49 GiB free after the 2026-09-05 emergency cleanup. Docker Desktop
recovered from a wedged daemon the same day; 3 containers run healthy (omniroute,
omniroute-redis, claude-code-provider-adapter).

Current Docker state (measured 2026-09-05, `docker system df`):
images 25 total / 3 active, 20.09 GiB size, 14.65 GiB reclaimable; build cache
231 entries / 10.7 GiB, 4.365 GiB reclaimable; volumes 60 total / 2 active,
3.354 GiB, 2.955 GiB reclaimable. Of the 60 volumes, 50 are anonymous
(hash-named, `com.docker.volume.anonymous` label, created 2026-08-23/24) and 10
are named (2 active omniroute + 8 tdt-local-full_* experiment data).

## Goals / Non-Goals

**Goals:**

- Reclaim ~20 GiB of rebuildable/re-pullable or ephemeral resources with a
  surgical, explicit-list approach (no blind `prune -a` / volume pruning).
- Preserve rollback capability, named data volumes, and running services.
- Record the exact removal list and verification gates for auditability.

**Non-Goals:**

- Deleting or archiving `~/jenkins_home` (1.8 GiB, stale CI home) — owner decision.
- Removing `/Library/Developer/CoreSimulator` (11 GiB iOS simulators) — owner decision.
- Deleting tdt-local-full_* named volumes (team experiment data).
- Docker.raw resize (sparse 704 GiB max is fine; actual usage shrinks post-prune).
- Any repo code changes.

## Decisions

1. **Anonymous-only volume prune** (`docker volume prune -f`): removes only
   anonymous unused volumes; all named volumes survive regardless of usage.
   The 50 orphans are 2-week-old ephemeral state from a torn-down experiment;
   the experiment's meaningful data lives in the named tdt-local-full_* volumes.
   Alternative rejected: `docker volume prune --all` — would destroy the tdt
   experiment data.

2. **Explicit image removal list, not `image prune -a`**: `prune -a` removes every
   unused image including `omniroute:rollback-3.8.49-*`. The update.sh convention
   (~/Omniroute/scripts/update.sh: "old image is tagged omniroute:rollback-<ver>-<ts>
   before deploy") makes the rollback image an intentional safety artifact — keep
   the single latest. The dangling `<none>` omniroutine image (1.97 GiB, same era)
   is a process leftover and IS removed.

3. **Default builder prune, not `--all`**: reclaims the 4.365 GiB stale portion
   while keeping cache that is in use; `--all` would also reset build cache that
   recent image builds (provider-adapter, 8 days) still reference.

4. **Registry images removed are re-pullable on demand**: the tdt-observability
   compose stack (langfuse, lgtm, clickhouse, mlflow, postgres, redis, minio,
   otel) re-pulls on next `up`; local builds (tdt-scheduler:main-c6a0fd4,
   agent-core:local-dev, tdt-observability:local-*) rebuild from their repos.
   Cost: minutes of re-pull/rebuild time, no data loss (volumes preserved).

5. **Go module cache cleared** (`go clean -modcache`): pure download cache;
   go-microservices builds re-fetch on demand.

6. **Verification gates after cleanup**: (a) all 3 containers healthy;
   (b) OmniRoute `/v1/models` returns 401 (documented healthy state, keyless
   loopback); (c) free space delta ≥ 15 GiB; (d) `docker volume ls` retains all
   10 named volumes; (e) rollback image still present.

## Risks / Trade-offs

- Re-deploying the tdt stack later requires re-pulling ~9 GiB of images (bandwidth
  - minutes). Accepted: 11-day-old images with no containers are stale; disk
  pressure outweighs re-pull cost.
- `go clean -modcache` slows the next go build by re-download time. Accepted.
- If the team wants to ROLL BACK OmniRoute to 3.8.49, the image is preserved; if
  they want to return to a tdt experiment state, data volumes are preserved.
- No risk to active services: removals are container-unreferenced by definition
  (`docker system df` active set), verified again before each removal command.
