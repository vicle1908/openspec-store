# Design

## Context

See `proposal.md` — Why for problem statement and motivation, and `specs/bifrost-gateway/spec.md` + `specs/omniroute-agent-skills/spec.md` for normative requirements.

OmniRoute runs in Docker Compose (`omniroute-base`, container `omniroute`, image `diegosouzapw/omniroute:latest`) using `docker-compose.override.yml` to specify local environment variables, loopback port bindings, and named volume persistence (`omniroute-data`). On the host, `/Users/androidteam/.local/bin/omniroute` acts as an isolated Bun CLI bridge that wraps the upstream CLI (`/Users/androidteam/Omniroute/bin/omniroute.mjs`). To prevent mutating or reading from an unmounted local SQLite file while `/app/data/storage.sqlite` lives inside the container volume, the bridge sets `DATA_DIR` to an ephemeral temporary directory (`/tmp/omniroute-cli-bridge-*`). For operational queries, the bridge intercepts specific subcommands (`status`, `keys list`) and fetches live data from the container daemon via `fetchDaemonJson`.

## Goals / Non-Goals

**Goals:**
- Add `OMNIROUTE_MEMORY_MB=4096` to calibrate the standalone server launcher and child workers within the local Docker Desktop VM memory envelope.
- Add `OMNIROUTE_MAX_TOOLS_LIMIT=256` to raise the tool definition ceiling from the default of 128 for high-volume MCP toolchains.
- Add targeted stream resilience feature flags to `docker-compose.override.yml` (`STREAM_READINESS_STALL_RETRY=true`, `EMPTY_STREAM_SIBLING_RECOVERY_ENABLED=true`) while keeping `STREAM_RECOVERY_ENABLED=false` to avoid the 750 ms TTFT latency penalty.
- Add `providers list` / `providers` interception in `~/.local/bin/omniroute` to query `/api/providers?limit=5000` via `fetchDaemonJson`, rendering live connections in formatted table or `{ providers: [...] }` JSON output without secret leakage.
- Recreate the `omniroute-base` container under kernel lock (`~/.omniroute/update.lock`) and verify cold boot health.

**Non-Goals:**
- Enabling `STREAM_RECOVERY_ENABLED=true` (which introduces a 750 ms TTFT latency holdback on all streams).
- Modifying tracked files in the OmniRoute git repository.
- Re-encrypting or writing provider credentials.

## Decisions

### 1. Explicit Environment & Targeted Resilience in `docker-compose.override.yml`
- **Choice**: Add `OMNIROUTE_MEMORY_MB=4096`, `OMNIROUTE_MAX_TOOLS_LIMIT=256`, `STREAM_READINESS_STALL_RETRY=true`, and `EMPTY_STREAM_SIBLING_RECOVERY_ENABLED=true` alongside `NODE_OPTIONS=--max-old-space-size=4096`. Do not enable `STREAM_RECOVERY_ENABLED=true`.
- **Rationale**:
  - `DOCKER_GUIDE.md § Runtime defaults` documents that the Docker standalone launcher reads `OMNIROUTE_MEMORY_MB` to scale background worker heaps and memory thresholds. `4096` fits the local Docker Desktop VM RAM budget (whereas upstream's `8192` recommendation requires a ≥10 GiB VM allocation).
  - Upstream's default `MAX_TOOLS_LIMIT` is `128` (`open-sse/config/constants.ts`). Setting `256` provides headroom for MCP Router (84–134 tools).
  - `STREAM_RECOVERY_ENABLED` buffers up to 750 ms (`HOLDBACK_MS: 750`) on every stream. Keeping it off avoids TTFT latency degradation on interactive coding streams. `STREAM_READINESS_STALL_RETRY` retries stalled first bodies once, and `EMPTY_STREAM_SIBLING_RECOVERY_ENABLED` fails over empty stream terminals across eligible sibling combo targets without adding TTFT delay to healthy streams.

### 2. Bridge Interception for `omniroute providers list`
- **Choice**: In `~/.local/bin/omniroute`, add a `runRemoteProvidersList` handler. When the CLI command is `providers list` or `providers` (with optional `--output json` or `--json`), call `fetchDaemonJson("/api/providers?limit=5000", timeoutMs)`.
- **Rationale**: The daemon's `/api/providers` endpoint returns `{ connections: [...], total: N }`. The bridge must sanitize and project only public fields matching upstream CLI's `publicConnection()` (`id`, `provider`, `name`, `authType`, `isActive`, `testStatus`, `lastTested`, `lastError`, `defaultModel`) and emit `{ providers: [...] }` to preserve upstream CLI compatibility.
- **Alternatives Considered**: Directing users to `omniroute providers status`. While `providers status` is upstream's remote command, operators frequently run `omniroute providers list`. Intercepting it in the bridge maintains parity with `omniroute keys list` and prevents false "No providers configured." reports.

## Risks / Trade-offs

- **[Risk] Container restart causes transient ~5-10s downtime** → **Mitigation**: Recreate during scheduled maintenance window holding `/usr/bin/lockf` on `~/.omniroute/update.lock`.
- **[Risk] Upstream CLI JSON contract divergence** → **Mitigation**: Project daemon `{ connections: [...] }` to `{ providers: [...] }` with safe public fields only.
