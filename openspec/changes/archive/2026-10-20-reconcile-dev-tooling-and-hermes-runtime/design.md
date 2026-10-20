# Design: Reconcile Developer Tooling and Hermes Runtime

## Context

An architectural audit of developer tooling across the multi-repo workspace (`~/Developer/`) and Hermes Agent runtime (`~/.hermes/`) revealed configuration, security, and documentation drift:
1. `~/.hermes/config.yaml` contained an unmasked `MCPR_TOKEN` within the `mcp_servers.mcp-router` configuration.
2. The MCP server runner used `npx -y @mcp_router/cli@latest connect`, causing dynamic registry checks on each agent startup and increasing discovery latency.
3. `~/Developer/AGENTS.md` listed `pnpm 10.22.0` while `platform/mcp-router/package.json` and host toolchains use `pnpm 12.14.0`.
4. An interrupted source update left stale lock files in `~/.hermes/` and surfaced persistent warnings on CLI invocations.

## Goals / Non-Goals

### Goals
- Enforce secret quarantine by referencing `${MCPR_TOKEN}` in `config.yaml` while reading values from `~/.hermes/.env`.
- Establish deterministic local binary execution for `mcpr` (`/Users/androidteam/.npm-global/bin/mcpr connect`).
- Ensure `AGENTS.md` accurately documents the canonical `pnpm 12.14.0` toolchain.
- Complete interrupted updates and verify clean runtime state across Docker and language toolchains.

### Non-Goals
- Modifying upstream Hermes core code or altering core approval policies beyond documented profile requirements.
- Upgrading unrelated monorepo dependencies or altering service logic.

## Technical Decisions

### Decision 1: Environment Variable Interpolation for MCP Tokens
Hermes natively supports `${VAR}` substitution in `config.yaml`. Moving secrets to `~/.hermes/.env` (mode 0600) and referencing them via `${MCPR_TOKEN}` complies with OpenSpec `hermes-configuration-safety` requirement: *"Credentials SHALL remain outside tracked planning artifacts and non-secret configuration files."*

### Decision 2: Deterministic Local MCP Binary Invocation
Replacing `npx -y @mcp_router/cli@latest connect` with `/Users/androidteam/.npm-global/bin/mcpr connect` removes dependency on network reachability, npm registry response times, and npm package resolution during agent startup.

### Decision 3: Finalizing Interrupted Updates via CLI
Running `hermes update --check` triggers Hermes's native recovery handler, which builds required node dependencies, updates desktop and web assets, refreshes the model catalog, and deletes stale `.hermes-update-in-progress.lock` markers.

## Risks & Mitigations

- **Risk**: Missing environment variable causes MCP server authentication failure.
  - *Mitigation*: Confirmed `MCPR_TOKEN` is present in `~/.hermes/.env` prior to switching `config.yaml`.
- **Risk**: Global npm binary out of sync with workspace.
  - *Mitigation*: Confirmed `/Users/androidteam/.npm-global/bin/mcpr` links directly to `@mcp_router/cli` distribution.
