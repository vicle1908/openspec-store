# Design: Reclaim Workstation Disk Storage

## Context

See `proposal.md` for problem background and motivation. The workstation primary APFS volume (`/System/Volumes/Data`) currently operates at 95% capacity with 21.9 GiB free space, below the 30 GiB minimum threshold required by `workstation-storage-hygiene`.

Five active Docker containers (`omniroute`, `omniroute-redis`, `omniroute-qdrant`, `shb-schedule-db-1`, `shb-schedule-scheduler-1`) are currently running and must remain undisturbed. Named Docker volumes (`omniroute-data`, `postgres-data`) store production/persistent state and must not be unlinked. Rebuilding and caching dependencies across Go, Python (uv), Node.js (npm/pnpm), and Homebrew are safe and fast, while deleting unreferenced simulator devices and stale system crash logs clears system-level bloat.

## Goals / Non-Goals

**Goals:**
- Reclaim >30 GiB of disk space to safely surpass the 30 GiB minimum threshold and head towards the 120 GiB high-water mark.
- Follow the tiered safety progression defined in the `workstation-storage-reclamation` skill and `workstation-storage-hygiene` spec.
- Protect all active running containers, named database volumes, source code worktrees, and user photos.
- Measure and record storage deltas on `/System/Volumes/Data` before and after each tier.

**Non-Goals:**
- Deleting named Docker volumes or stopping running containers.
- Touching active project worktrees, virtual environments, or git branches in `~/Developer/`.
- Deleting local Ollama LLM model weights or active IDE configuration profiles.
- Modifying mounted cryptex disk images or active Simulator runtimes while in use.

## Decisions

### Decision 1: Strict Tiered Progression (Tier 1 → Tier 2 → Tier 3)
- **Rationale**: Evacuating zero-risk ephemeral download caches first immediately relieves disk pressure before touching container layers or simulator runtimes.
- **Alternatives Considered**: Bulk execution via a single shell script. Rejected because staged execution isolates any tool errors and enables measuring incremental deltas per subsystem.

### Decision 2: Owning Tool Commands Over Unguided Filesystem Deletion
- **Rationale**: Using `brew cleanup`, `npm cache clean`, `pnpm store prune`, `uv cache prune`, `go clean -cache`, and `docker prune` ensures internal package index databases stay synchronized and consistent.
- **Alternatives Considered**: Raw `rm -rf ~/.cache/* ~/.npm/*`. Rejected because unguided deletion corrupts package manager index databases and leaves lock files or stale references.

### Decision 3: Strict Named-Volume Preservation in Docker Pruning
- **Rationale**: `docker volume prune -f` only targets anonymous unreferenced volumes. Named volumes (`omniroute-data`, `shb-schedule-db-data`, `postgres-data`) are excluded by Docker engine semantics.
- **Alternatives Considered**: `docker system prune --volumes -f`. Rejected because `--volumes` would delete unattached named volumes, risking data loss for stopped services.

### Decision 4: APFS Data-Volume Boundary Measurement
- **Rationale**: APFS root `/` is a read-only sealed snapshot (~13 GiB). All developer caches and container layers reside on `/System/Volumes/Data`.
- **Alternatives Considered**: `df -h /`. Rejected because root volume reporting is misleading on modern macOS.

## Risks / Trade-offs

- **[Risk] Docker base images deleted forcing re-download** → Mitigation: Use `--filter "until=168h"` to prune only images older than 7 days, retaining current working images.
- **[Risk] `uv cache prune` lock contention with background Python agents** → Mitigation: Run `uv cache prune` with a standard timeout; if locked, safely skip.
- **[Risk] APFS local snapshot retention pinning deleted blocks** → Mitigation: Check `tmutil listlocalsnapshots /` before and after. If snapshots pin blocks, document snapshot dates.
- **[Risk] Re-download overhead on next build** → Trade-off: Package caches will re-download when new packages are fetched, which is the expected behavior for ephemeral caches.

## Migration / Rollback Plan

- Rebuildable caches regenerate automatically on the next invocation of `brew install`, `npm install`, `pnpm install`, `uv run`, `go build`, or `docker build`.
- No rollback script is necessary since deleted objects are ephemeral caches, unreferenced layers, and stale logs.
