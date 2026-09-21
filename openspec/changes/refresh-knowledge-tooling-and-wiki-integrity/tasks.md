# Tasks: Refresh Knowledge Tooling and Wiki Integrity

## Track 1: Tooling Upgrades & Skill Synchronization

- [x] 1.1 Upgrade `gitnexus` globally to `1.6.12` via npm and verify `gitnexus --version`
- [x] 1.2 Upgrade `graphifyy` to `0.9.65` via `uv tool upgrade` and verify `graphify --version`
- [x] 1.3 Synchronize Graphify platform skills across `hermes`, `agents`, `claude`, and `codex` runtimes

## Track 2: Wiki Staleness & Orphan Reference Resolution

- [x] 2.1 Clean up transient `.pytest_cache/` directory from `~/Developer/wiki`
- [x] 2.2 Link `references/developer-knowledge-refresh-2026-08-25.md` in `wiki/index.md` under `## References` and bump page count
- [x] 2.3 Refresh `updated: 2026-09-21` frontmatter on 10 stale wiki pages
- [x] 2.4 Commit wiki updates in `wiki` repository (`c26dea4`)
- [x] 2.5 Verify `python3 scripts/wiki-lint.py` exits 0 with zero-byte stdout

## Track 3: Knowledge Index Reconciliation & Cron Acceptance

- [x] 3.1 Refresh GitNexus and Graphify indexes on clean `mcp-router` repository (`dfed7d4`)
- [x] 3.2 Clear stale `analyze.lock` and refresh GitNexus on `tdt-core` (`7d0b090`)
- [x] 3.3 Refresh GitNexus on `tdt-scheduler` (`308422d`)
- [x] 3.4 Preserve dirty worktrees (`go-microservices` and others) per Knowledge Refresh Contract
- [x] 3.5 Verify live cron execution for `weekly-wiki-lint` (`589262cf00d4`)
- [x] 3.6 Verify live cron execution for `weekly-graphify-freshness` (`13ca08f6f0fd`)

## Closure

- [x] 4.1 Strict OpenSpec validation of change artifacts
- [x] 4.2 Review change artifacts and commit store change
- [x] 4.3 Archive change to `openspec/changes/archive/`
