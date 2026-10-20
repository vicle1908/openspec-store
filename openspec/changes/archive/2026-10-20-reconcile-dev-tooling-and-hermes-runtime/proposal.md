# Proposal: Reconcile Developer Tooling and Hermes Runtime

## Why

Auditing workstation developer toolchains across Hermes Agent, Node.js monorepo workspaces, and local service gateways revealed inline secret leakage in `~/.hermes/config.yaml`, cold-start latency from dynamic `npx` invocations during MCP tool discovery, workspace documentation drift on Node package managers (`pnpm`), and an interrupted Hermes source update leaving stale gateway locks and update warnings. Formalizing these remediations under OpenSpec restores single-source-of-truth credential safety, eliminates MCP startup overhead, aligns documentation with package manifests, and guarantees runtime release freshness.

## What Changes

- **Hermes Configuration & Credential Safety (`hermes-configuration-safety`)**:
  - Quarantine plaintext secret token `MCPR_TOKEN` in `~/.hermes/config.yaml` to `${MCPR_TOKEN}` with storage in `~/.hermes/.env`.
  - Replace ephemeral `npx -y @mcp_router/cli@latest connect` with deterministic local binary path `/Users/androidteam/.npm-global/bin/mcpr connect` for `mcp-router` tool discovery.
  - Finalize interrupted Hermes source update via `hermes update --check`, clearing stale update locks and updating bundled Node dependencies, TUI, Web UI, and model catalog to stable `v0.22.2`.
- **Workspace Toolchain Documentation Alignment (`workstation-toolchain-inventory`)**:
  - Reconcile `~/Developer/AGENTS.md` and `~/Developer/platform/mcp-router/AGENTS.md` to record `pnpm 12.14.0` (matching `platform/mcp-router/package.json` and host binary), eliminating stale `pnpm 10.22.0` references.
  - Upgrade GitHub Actions CI workflows in `platform/mcp-router` (`.github/workflows/typecheck.yml` and `make.yml`) from `pnpm/action-setup@v2` (`version: 10`) to `pnpm/action-setup@v4` (`version: 12.14.0`), establishing complete parity between local development and CI execution.
- **Service Deployment & Upstream Parity Verification**:
  - Verify OmniRoute AI gateway container digest against upstream Docker Hub index (`~/.omniroute/update-available: false`).
  - Verify SHB scheduler and PostgreSQL containers and Python 3.14 toolchain consistency.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `hermes-configuration-safety`: Add requirements for deterministic local MCP runner binary resolution and environment variable substitution for MCP credentials.

### Removed Capabilities
- None.

## Impact

- **Hermes Agent Runtime**: Faster MCP server initialization during startup; elimination of plaintext secret tokens in `~/.hermes/config.yaml`; clean CLI diagnostics without interrupted-update warnings.
- **Developers / Agents**: Clear and accurate package manager instructions in `AGENTS.md`.
- **Breaking Changes**: None. All changes are backward-compatible and preserve existing tool capabilities.
