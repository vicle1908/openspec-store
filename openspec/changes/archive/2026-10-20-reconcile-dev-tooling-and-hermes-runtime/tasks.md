# Tasks: Reconcile Developer Tooling and Hermes Runtime

## 1. Hermes Security & MCP Optimization

- [x] 1.1 Quarantine plaintext secret token `MCPR_TOKEN` in `~/.hermes/config.yaml` to `${MCPR_TOKEN}` with backing secret in `~/.hermes/.env`
- [x] 1.2 Switch `mcp_servers.mcp-router` command from dynamic runner (`npx -y @mcp_router/cli@latest connect`) to deterministic local binary (`/Users/androidteam/.npm-global/bin/mcpr connect`)
- [x] 1.3 Resolve interrupted Hermes source update via `hermes update --check` and clean up orphaned update locks
- [x] 1.4 Validate Hermes configuration and MCP server runner with `hermes config get mcp_servers.mcp-router`

## 2. Toolchain Alignment & Workspace Documentation

- [x] 2.1 Reconcile Node.js package manager documentation in `~/Developer/AGENTS.md` to record `pnpm 12.14.0` matching `package.json` and host runtime
- [x] 2.2 Verify toolchain version consistency across Python (`uv 0.13.1`, Python 3.14.7, `ruff 0.17.1`) and Go (`1.27.2`)
- [x] 2.3 Verify test cache isolation (`-p no:cacheprovider`) and hatchling build standards across `tdt` and `shb` Python repos
- [x] 2.4 Reconcile nested `platform/mcp-router/AGENTS.md` to record pinned `pnpm 12.14.0` toolchain
- [x] 2.5 Upgrade GitHub Actions workflows in `platform/mcp-router` (`typecheck.yml`, `make.yml`) to `pnpm/action-setup@v4` (`version: 12.14.0`)

## 3. Service Deployment & Upstream Parity Checks

- [x] 3.1 Verify OmniRoute AI gateway container health and check upstream Docker Hub image index digest (`update-available: false`)
- [x] 3.2 Verify SHB scheduler and database container deployment health (`shb-schedule-scheduler-1`, `shb-schedule-db-1`)
- [x] 3.3 Verify git working trees across core development repositories (`~/Developer/platform/mcp-router`, `~/Omniroute`)

## 4. OpenSpec Specification & Progress Tracking

- [x] 4.1 Author OpenSpec change proposal, delta specs, design, and tracked task artifacts under `platform/openspec-store`
- [x] 4.2 Validate change artifacts strictly against OpenSpec schema (`openspec validate --change reconcile-dev-tooling-and-hermes-runtime --store openspec-store`)
