# Proposal

## Why

The local OmniRoute Docker deployment currently omits explicit `OMNIROUTE_MEMORY_MB` and `OMNIROUTE_MAX_TOOLS_LIMIT` environment overrides in `docker-compose.override.yml`, leaves streaming readiness and stall recovery flags at inactive definition defaults, and the host CLI bridge (`~/.local/bin/omniroute`) falls through to an empty ephemeral SQLite database for `omniroute providers list` rather than querying live daemon truth from `/api/providers`.

Specifically, while official upstream documentation (`docs/guides/DOCKER_GUIDE.md § Runtime RAM for coding agents`) recommends `8192` for heavy multi-agent workloads, local workstation Docker Desktop VM constraints require calibrating `OMNIROUTE_MEMORY_MB=4096` to match the existing 4 GiB V8 heap limit. Furthermore, while the upstream default tool ceiling is `128` (`open-sse/config/constants.ts`), rich toolchains like MCP Router (84–134 tools) benefit from raising `OMNIROUTE_MAX_TOOLS_LIMIT=256` to prevent tool schema truncation. In addition, enabling targeted streaming resilience flags (`STREAM_READINESS_STALL_RETRY=true` and `EMPTY_STREAM_SIBLING_RECOVERY_ENABLED=true`) allows bounded recovery on stalled connections and empty-terminal streams without enabling `STREAM_RECOVERY_ENABLED=true` (which would impose a mandatory 750 ms time-to-first-token holdback latency penalty on interactive streams). Finally, while `~/.local/bin/omniroute` intercepts `omniroute status` and `omniroute keys list` to query `/api/monitoring/health` and `/api/providers`, it does not intercept `omniroute providers list`, causing host invocations of `omniroute providers list` to report `No providers configured.` despite 33 active provider connections operating in the live container.

## What Changes

- **Explicit Coding-Agent Runtime Limits & Targeted Resilience (`~/Omniroute/docker-compose.override.yml`)**:
  - Add `OMNIROUTE_MEMORY_MB=4096` to `omniroute-base` in `~/Omniroute/docker-compose.override.yml`, calibrating the standalone server launcher and child workers within the local Docker Desktop VM memory envelope.
  - Add `OMNIROUTE_MAX_TOOLS_LIMIT=256` to `omniroute-base` in `~/Omniroute/docker-compose.override.yml`, raising the gateway tool definition ceiling from the default of 128 to 256 for rich MCP workflows.
  - Add `STREAM_READINESS_STALL_RETRY=true` and `EMPTY_STREAM_SIBLING_RECOVERY_ENABLED=true` to `omniroute-base` in `~/Omniroute/docker-compose.override.yml` to enable bounded stall and empty-terminal failover while keeping `STREAM_RECOVERY_ENABLED=false` to avoid the 750 ms TTFT latency penalty.
- **Remote-Truth `omniroute providers list` Interception (`~/.local/bin/omniroute`)**:
  - Intercept `omniroute providers list` and `omniroute providers` in the host Bun bridge (`~/.local/bin/omniroute`) to query `/api/providers?limit=5000` on `127.0.0.1:20128` over HTTP using `fetchDaemonJson` and active key resolution (via `OMNIROUTE_API_KEY` or `~/.claude/helpers/omniroute-key.sh`).
  - Render live configured provider connections in both human-readable table format (`<short-id>  <provider>  <name>  <status>`) and `--output json` / `--json` format matching upstream's `{ providers: [...] }` schema (and projecting only safe public fields), eliminating the false "No providers configured." result.
- **Automated Behavioral Regression Testing**:
  - Extend `/Users/androidteam/Developer/platform/openspec-store/tests/test_omniroute_cli_bridge.py` to assert that `omniroute providers list` queries `/api/providers` and formats live connections in table and JSON formats without reading from local SQLite.

## Non-Goals

- Modifying upstream git-tracked files in `/Users/androidteam/Omniroute` (`docker-compose.override.yml` is an untracked local deployment file).
- Enabling `STREAM_RECOVERY_ENABLED=true` (which introduces a 750 ms time-to-first-token holdback latency penalty on all streams).
- Altering published port mappings, volume mounts, or Redis configuration.
- Re-encrypting or mutating provider credentials or combo definitions in `/app/data/storage.sqlite`.

## Affected Ownership Boundaries

- **OmniRoute Deployment Root**: `/Users/androidteam/Omniroute/docker-compose.override.yml` (runtime environment limits and resilience flags).
- **Host CLI Bridge**: `/Users/androidteam/.local/bin/omniroute` (remote-truth CLI interception).
- **OpenSpec Store & Test Suite**: `/Users/androidteam/Developer/platform/openspec-store` (`specs/bifrost-gateway/spec.md`, `specs/omniroute-agent-skills/spec.md`, `tests/test_omniroute_cli_bridge.py`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `bifrost-gateway`: Add requirements for coding-agent memory calibration (`OMNIROUTE_MEMORY_MB=4096`), tool count limits (`OMNIROUTE_MAX_TOOLS_LIMIT=256`), and targeted stream recovery flags (`STREAM_READINESS_STALL_RETRY=true`, `EMPTY_STREAM_SIBLING_RECOVERY_ENABLED=true`) in the container environment.
- `omniroute-agent-skills`: Add requirement for host CLI bridge to query remote daemon truth for `omniroute providers list` rather than falling through to local ephemeral SQLite storage.

## Impact

- **Gateway Robustness & Latency Safety**: Calibrates internal Node memory management to 4 GiB, avoids tool truncation for large MCP toolchains, and provides stall recovery without imposing universal TTFT latency holdbacks.
- **Operator Experience**: Resolves the discrepancy where `omniroute status` reports 33 configured providers but `omniroute providers list` falsely claims zero providers configured.
