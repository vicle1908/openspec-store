# Design — Upgrade OmniRoute to v3.8.51

## Context

OmniRoute is deployed on macOS as a local containerized AI gateway serving loopback ports 20128 (dashboard), 20129 (API bridge), and 20132 (LiveWS). The runtime runs under Docker Compose (`--profile base`) against the official Hub image `diegosouzapw/omniroute:latest`. 

The update-tracking LaunchAgent (`com.omniroute.update-check`) discovered v3.8.51 and recorded the target index digest `sha256:8bd462c9f60d8eda79329cfbb6ea7ea723505fe7721beb944f3d43835409e218` in `~/.omniroute/update-available`.

See `proposal.md` for problem statement and motivation.

## Goals / Non-Goals

**Goals:**
- Execute a deterministic, fail-closed upgrade of `omniroute` from v3.8.50 to v3.8.51 via `~/Omniroute/scripts/update.sh 3.8.51`.
- Verify all 10 update gates (0 through 9) pass completely before clearing `~/.omniroute/update-available`.
- Guarantee SQLite database integrity and preserve active API keys and provider connections.
- Ensure all 5 standard service endpoints respond with expected HTTP statuses.
- Update `platform/openspec-store/openspec/config.yaml` with the upgraded version, date, and index digest.

**Non-Goals:**
- No Redis major version bump (`redis:7-alpine` is retained; Redis container is untouched).
- No git pull or tracking changes in `~/Omniroute` (the local checkout carries untracked overrides).
- No `.env` modifications (all 64 active keys are verified compatible).
- No addition of optional Compose profiles (`web`, `cli`, `bifrost`, `memory`, `codex-app-server`).

## Decisions

### D1: Re-use Existing Hardened Linear Gate Chain in `update.sh`

The deployment updater `~/Omniroute/scripts/update.sh` was hardened in `2026-08-28-upgrade-omniroute-to-v3-8-50` with fail-closed semantics (`set -euo pipefail` plus an `ERR` trap and gate check functions). It accepts the target version as an argument:
```bash
~/Omniroute/scripts/update.sh 3.8.51
```

The gate sequence executes in strict linear order:

| Gate | Name | Verification & Safety Action |
|---|---|---|
| **0** | Flag Check | Verifies `~/.omniroute/update-available` exists and contains target digest `sha256:8bd462c9...`. |
| **P** | Preflight | Checks Docker daemon, host sqlite3 CLI, compose config rendering, and existing container presence. |
| **Pre** | Pre-state Snapshot | Captures pre-upgrade version (`3.8.50`), running image ID, image digest, and baseline counts (`api_keys=1`, `provider_connections=19`). Tags rollback image `omniroute:rollback-3.8.50-<timestamp>`. |
| **1** | SQLite Snapshot & Integrity | Verifies live SQLite `integrity_check=ok`, performs non-blocking `db.backup('/tmp/...')` via `better-sqlite3`, copies to host `~/.omniroute/snapshots/`, runs host `sqlite3 PRAGMA integrity_check`, and truncates WAL sidecars into a single durable artifact. |
| **2** | Service-Targeted Pull | Runs `docker compose --profile base pull omniroute-base` (Redis is untouched). |
| **3** | Target Digest Match | Validates that pulled image RepoDigest matches `TARGET_DIGEST` from the flag file. |
| **4** | Container Recreation | Recreates service via `docker compose --profile base up -d --no-build --pull never --no-deps --force-recreate omniroute-base`. |
| **5** | Health Check | Polls `docker inspect --format='{{.State.Health.Status}}' omniroute` until `healthy` (up to 5 min, start period 120s). |
| **6** | In-Image Version | Inspects `/app/package.json` inside the running container to confirm `version === "3.8.51"`. |
| **7** | Image ID Match | Verifies running container image ID equals the newly pulled image ID. |
| **8** | Endpoint Verification | Asserts `/healthz` returns `ok`, dashboard root returns HTTP 200 or 307, `/api/monitoring/health` returns `status: "healthy"` and `setupComplete: true`, `HEAD /v1/models` returns 200, and authenticated in-container `GET /v1/models` returns 200 with non-empty catalog data. |
| **9** | Post-Deploy Data Check | Confirms post-deploy SQLite `integrity_check=ok`, and verifies active `api_keys >= 1` and `provider_connections >= 19`. |

Only when Gate 9 passes does the script clear `~/.omniroute/update-available` and log completion.

### D2: SQLite Transaction Boundaries & Persistence Integrity

To ensure zero risk of database corruption on macOS:
- Persistence uses the named Docker volume `omniroute-data` mounted at `/app/data`. Bind mounts are forbidden because Docker Desktop virtiofs causes SQLite WAL corruption.
- Transaction boundary for snapshot: The backup executes inside the container via SQLite's online backup API (`better-sqlite3` `db.backup()`), which acquires a shared read lock without stalling concurrent reads. On the host copy, `PRAGMA wal_checkpoint(TRUNCATE)` integrates pending WAL frames into the main database file and removes `-wal` and `-shm` sidecars, producing a self-contained, restorable snapshot.

### D3: Defer Redis Major Upgrade

Upstream compose includes `redis:8.6.5-alpine`. Local deployment deliberately stays on `redis:7-alpine`. The Redis container service is excluded from pull and recreation (`pull omniroute-base` and `up --no-deps omniroute-base`). Any Redis upgrade requires separate data directory validation and schema compatibility review.

### D4: Runtime Memory Setting Maintenance

Upstream v3.8.51 continues to recommend 2048 MB memory ceiling for Next.js and the Node router under heavy model catalog caching. The untracked `docker-compose.override.yml` already specifies:
```yaml
environment:
  - NODE_OPTIONS=--max-old-space-size=2048
```
This is preserved without alteration.

## Risks / Trade-offs

| Risk | Consequence | Mitigation |
|---|---|---|
| Registry digest mismatch or corrupted pull | Broken runtime or partial image | Gate 3 verifies pulled RepoDigest equals flagged target `sha256:8bd462c9...` before recreation. |
| Startup migration failure | Container crash loop | Gate 5 enforces a 5-minute health deadline with 120s start period. If unhealthy, the script fails closed and preserves pre-state evidence. |
| Data loss during upgrade | Lost credentials or routes | Pre-state backup in `~/.omniroute/snapshots/` verified with host `sqlite3`. Pre-state image tagged as `omniroute:rollback-3.8.50-<timestamp>`. Post-deploy Gate 9 verifies `api_keys >= baseline` and `provider_connections >= baseline`. |
| Transient service interruption | 30–60s unavailability during recreation | Run during operator session; subagents and CLI tools tolerate brief HTTP 502/503 during container restart. |

### Rollback Plan

If any gate fails or post-deploy anomalies occur:
1. Re-tag or redeploy the pre-state image:
   ```bash
   docker tag omniroute:rollback-3.8.50-<timestamp> diegosouzapw/omniroute:latest
   docker compose --profile base up -d --no-build --pull never --no-deps --force-recreate omniroute-base
   ```
2. If SQLite migrations altered tables in an incompatible way:
   ```bash
   docker compose --profile base stop omniroute-base
   docker cp ~/.omniroute/snapshots/pre-update-<timestamp>.sqlite omniroute:/app/data/storage.sqlite
   docker compose --profile base start omniroute-base
   ```
