# Proposal: Refresh Knowledge Tooling and Wiki Integrity

## Why

Routine weekly cron monitoring identified several maintenance issues across workspace tooling, documentation, and knowledge indexes:

1. **Tooling Version Drift**: Installed CLI tools were behind latest upstream releases: `gitnexus` was at `1.6.10` (latest `1.6.12`), and `graphify` was at `0.9.64` (latest `graphifyy` `0.9.65`). Graphify agent platform skills were also on `0.9.64`.
2. **Wiki Staleness and Orphan Link Warnings**: `weekly-wiki-lint` reported 10 stale documentation pages with `updated` timestamps older than 30 days, an orphan reference (`references/developer-knowledge-refresh-2026-08-25.md`) with zero inbound links from `index.md`, and transient `.pytest_cache/` residue.
3. **Knowledge Index Stale Commit Mismatches**: `weekly-graphify-freshness` flagged index staleness on clean repositories (`mcp-router`, `tdt-core`, `tdt-scheduler`) due to past application commits that had not triggered an index refresh, as well as a stale index lock in `tdt-core`.

## What Changes

1. **Tooling Upgrades & Skill Synchronization**:
   - Upgrade `gitnexus` globally to `1.6.12` via npm.
   - Upgrade `graphifyy` to `0.9.65` via `uv tool upgrade`.
   - Synchronize Graphify platform skills across `hermes`, `agents`, `claude`, and `codex`.

2. **Wiki Integrity & Staleness Resolution**:
   - Remove transient `.pytest_cache/` from `~/Developer/wiki`.
   - Link `references/developer-knowledge-refresh-2026-08-25.md` in `wiki/index.md` and bump total page count to 26.
   - Review and refresh `updated: 2026-09-21` across all 10 flagged pages.
   - Commit changes to `wiki` repo (`c26dea4`).
   - Verify deterministic `wiki-lint.py` validator produces zero-byte output and exit 0.

3. **Knowledge Index Freshness & Cron Acceptance**:
   - Refresh GitNexus and Graphify indexes for clean repositories `mcp-router`, `tdt-core`, and `tdt-scheduler`.
   - Remove stale `analyze.lock` in `tdt-core`.
   - Preserve dirty worktrees (`go-microservices` and 18 other active repositories) without premature mutation, strictly following the Knowledge Refresh Contract.
   - Verify live execution of `weekly-wiki-lint` (`589262cf00d4`) and `weekly-graphify-freshness` (`13ca08f6f0fd`).

## Scope Boundaries

- **Out of Scope**: Blind commits or automated cleaning in dirty workspace repositories (`go-microservices`, `agent-core`, `ai-review`, etc.). Uncommitted work in progress must be preserved until owner review.
- **Out of Scope**: Reopening historical archived changes (e.g. `2026-08-25-repair-hermes-cron-run-reliability`).
