# Tasks

## 1. Tooling Verification & Upgrades

- [x] 1.1 Verify GitNexus (1.6.12) and AgentMemory (0.9.29) binary and npm registry versions.
- [x] 1.2 Upgrade Graphify via `uv tool upgrade graphifyy` from `0.9.69` to `0.9.71` and verify `graphify --version`.

## 2. Wiki Knowledge Base Updates & Linting

- [x] 2.1 Update stale wiki files (`entities/gitnexus.md`, `entities/graphify.md`, `entities/tdt-observability.md`, `SCHEMA.md`, `references/developer-knowledge-refresh-2026-08-25.md`).
- [x] 2.2 Create `entities/shb.md` documenting the 12-repo SHB banking and agent ecosystem and link it in `index.md`.
- [x] 2.3 Verify wiki integrity via `python3 scripts/wiki-lint.py` and `pytest tests/test_wiki_lint.py`.

## 3. Knowledge Index & Graph Refresh

- [x] 3.1 Run Graphify incremental update (`graphify update .`) across STALE repositories (`shb/*`, `tdt/tdt-scheduler`, etc.).
- [x] 3.2 Refresh GitNexus code intelligence index for STALE repositories in the inventory.
- [x] 3.3 Execute AgentMemory diagnostics and memory consolidation checks via CLI/MCP.

## 4. Operational Verification & OpenSpec Validation

- [x] 4.1 Run `knowledge-status.sh --json` to verify updated freshness across inventoried repositories.
- [x] 4.2 Test live query responsiveness across GitNexus, Graphify, AgentMemory, and Wiki tools.
- [x] 4.3 Validate the OpenSpec change strictly via `openspec validate update-dev-toolings-and-refresh-knowledge --strict --store openspec-store`.
