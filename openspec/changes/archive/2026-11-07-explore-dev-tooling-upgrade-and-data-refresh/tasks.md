# Tasks

## 1. Dev Tooling Audit & Upgrade Preparation

- [x] 1.1 Audit Homebrew formulae, casks, and Mac App Store packages (`Telegram 2 12.10 -> 13.1.0`).
- [x] 1.2 Audit Bun runtime (`1.4.4`) and npm-global packages (`gitnexus 1.6.12`, `@openai/codex 0.167.0`, `openspec 1.16.1`).
- [x] 1.3 Audit Python uv tools and identify upstream drift: `graphifyy` (installed `0.9.95`, upstream `0.9.103`).
- [x] 1.4 Audit coding agent CLIs (`claude`, `codex`, `opencode`, `auggie`, `qoder`, `pi`, `kimi`, `ntn`), verifying 8/8 aligned with stable releases.
- [x] 1.5 Apply `uv tool upgrade graphifyy` to advance `graphifyy` to `0.9.103` and verify CLI parity.

## 2. Data Refresh & Knowledge Base Synchronization

- [x] 2.1 Audit daily maintenance telemetry records in `~/Developer/data/updates/` (records current through `2026-11-06.json`).
- [x] 2.2 Audit knowledge index freshness via `knowledge-status.sh --json` (30 fresh, 3 stale: `jira-skill`, `mcp-router`, `openspec-store`).
- [x] 2.3 Audit LLM Wiki documentation freshness (`wiki-lint.py` identified 20 entities >30 days old).
- [x] 2.4 Execute `workstation-daily-update.sh` to record today's maintenance telemetry (`2026-11-07.json`).
- [x] 2.5 Refresh GitNexus indexes for STALE repositories (`jira-skill`, `mcp-router`, `openspec-store`).
- [x] 2.6 Synchronize documentation to Notion via `sync-notion-knowledge.sh --incremental`.

## 3. Operational Runtime & Determinism Verification

- [x] 3.1 Verify network interface DNS routing fail-closed behavior (`curl --interface en0` vs `en1`).
- [x] 3.2 Verify Bun runtime execution readiness (`bun -e`).
- [x] 3.3 Verify OmniRoute inference gateway models endpoint fetch (`1048` models verified via `/v1/models`).
- [x] 3.4 Verify Go microservices Temporal workflow determinism replay across 8 services bounded within 45s (completed in 22.88s).

## 4. OpenSpec Store Validation & Governance

- [x] 4.1 Create OpenSpec exploration change `explore-dev-tooling-upgrade-and-data-refresh`.
- [x] 4.2 Author proposal, design, and delta specification for `workspace-index-freshness`.
- [x] 4.3 Validate OpenSpec strict compliance via `openspec validate --changes explore-dev-tooling-upgrade-and-data-refresh --strict --store openspec-store`.
