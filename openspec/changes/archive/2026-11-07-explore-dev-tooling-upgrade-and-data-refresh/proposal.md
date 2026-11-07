# Proposal: Explore Workspace Dev Tooling Upgrade and Data Refresh (Nov 2026)

## Why

Developer tooling and data assets across the multi-repo workspace (`~/Developer/`) require continuous synchronization and proactive lifecycle governance. An empirical workspace-wide audit conducted on 2026-11-07 established the following status:

1. **Toolchain Drift**: `graphifyy` is currently installed at `0.9.95` (`uv tool`), while upstream PyPI has released `0.9.103` (an 8-version advance providing AST cache isolation under `graphify-out/cache/ast/`, faster incremental graph updates, and improved edge indexing).
2. **Mac App Store**: `mas outdated` detects `Telegram 2` (`12.10` -> `13.1.0`), which requires non-disruptive lifecycle upgrade.
3. **Knowledge Index Stale State**: A health audit via `knowledge-status.sh --json` identified 3 STALE GitNexus repositories (`jira-skill`, `mcp-router`, `openspec-store`) relative to HEAD commits, while all 33 inventoried repositories are commit-equal in Graphify but contain generated graph cache artifacts.
4. **Documentation & Wiki Staleness**: `wiki-lint.py` identified 20 entities and concepts in `~/Developer/wiki/` exceeding the 30-day freshness threshold, while the automated Notion sync pipeline (`sync-notion-knowledge.sh`) is ready for incremental publication via `ntn`.
5. **Workspace Telemetry**: Telemetry records in `~/Developer/data/updates/` are recorded through `2026-11-06.json`; today's scheduled update cycle (`2026-11-07.json`) needs execution and archival.
6. **Live Operational Verification**: Foundational infrastructure—including OmniRoute's `/v1/models` endpoint (1,048 models), Bun 1.4.4 runtime eval, network interface DNS binding (`curl --interface en0` inactive physical fail-closed, `en1` active), and Go microservices Temporal workflow replay across 8 services—must be continuously verified within a strict 45-second execution boundary.

## What Changes

1. **Dev Tooling Modernization**:
   - Upgrade `graphifyy` from `0.9.95` to `0.9.103` via `uv tool upgrade graphifyy`.
   - Update `workspace-index-freshness` capability specification to pin Graphify `0.9.103`.
   - Audit coding agent CLIs (`claude 2.1.319`, `codex 0.167.0`, `opencode 1.19.5`, `auggie 0.37.0`, `qoder 1.1.84`, `pi 1.5.0`, `kimi 2.5.2`, `ntn 0.23.28`), confirming all 8 tools are aligned with current stable releases.
2. **Data & Knowledge Freshness**:
   - Refresh GitNexus code intelligence indexes for `jira-skill`, `mcp-router`, and `openspec-store`.
   - Execute workstation daily maintenance runner (`workstation-daily-update.sh`) to produce `~/Developer/data/updates/2026-11-07.json`.
   - Sync ecosystem architectural documentation to Notion via `sync-notion-knowledge.sh --incremental`.
3. **Operational Verification**:
   - Re-verify live endpoints: WiFi DNS binding, Bun runtime eval, Python models endpoint fetch (`/v1/models`), and Temporal replay tests within the 45-second boundary.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `workspace-index-freshness`: Upgrade Graphify provider version requirement to `0.9.103`.

## Impact

- **Affected Toolchains**: `graphifyy` (`uv tool`), `gitnexus` (CLI/MCP), `wiki` (documentation), `ntn` (Notion CLI).
- **Affected Repositories**: `platform/openspec-store/`, `tdt/jira-skill/`, `platform/mcp-router/`, and inventoried repos under `~/Developer/`.
- **Breaking Changes**: None. Graphify 0.9.103 maintains strict backwards compatibility with existing CLI arguments (`graphify update .`, `graphify extract .`) and schema contracts (`graph.json`).
