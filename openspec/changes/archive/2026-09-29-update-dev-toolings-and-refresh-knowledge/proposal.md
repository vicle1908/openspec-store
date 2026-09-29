# Proposal

## Why

Development toolings and knowledge indexing systems (`gitnexus`, `agentmemory`, `graphify`, `wiki`) are core infrastructure across the multi-repo workspace (`~/Developer/`). A scheduled health audit (`knowledge-status.sh --json`) and wiki linter audit revealed:
1. `graphifyy` is currently at `0.9.69`, while upstream PyPI has `0.9.71` available with bug fixes and incremental update improvements.
2. `gitnexus` (v1.6.12) and `agentmemory` (v0.9.29) binaries are at their latest upstream versions, but code repository changes across `tdt/`, `platform/`, and the newly created `shb/` ecosystem (12 repos) have left code intelligence and knowledge graph indexes in a `STALE` state relative to git HEAD revisions.
3. The LLM Wiki (`~/Developer/wiki`) has stale documentation entities (`entities/gitnexus.md`, `entities/graphify.md`, `entities/tdt-observability.md`, `SCHEMA.md`) and lacks documentation for the newly created `shb` banking and agent ecosystem.
4. AgentMemory daemon is running at `http://localhost:3111` with healthy provider bindings but requires memory diagnostics, schema verification, and graph consolidation check.

Bringing these toolchains up to date and synchronizing the underlying knowledge indices ensures coding agents and developers have reliable, high-precision code intelligence and architectural awareness.

## What Changes

1. **Tooling Upgrades & Verification**:
   - Upgrade `graphifyy` from `0.9.69` to `0.9.71` via `uv tool upgrade graphifyy`.
   - Verify `gitnexus` CLI (1.6.12) and `agentmemory` CLI (0.9.29) are active and functional.
   - Update `workspace-index-freshness` capability specification to pin `graphifyy` 0.9.71 and `gitnexus` 1.6.12.

2. **Wiki Knowledge Base Updates & Linting**:
   - Update stale wiki entity files (`entities/gitnexus.md`, `entities/graphify.md`, `entities/tdt-observability.md`, `SCHEMA.md`).
   - Create documentation for the newly created SHB ecosystem (`entities/shb.md`) covering its 12 repositories and architecture.
   - Update `index.md` and verify clean lint execution via `python3 scripts/wiki-lint.py` and `pytest tests/`.

3. **Knowledge Index & Graph Refresh**:
   - Refresh stale Graphify and GitNexus indexes across inventoried repositories via `refresh-knowledge-indexes.sh` and targeted repo updates.
   - Ensure the knowledge refresh approval digest (`knowledge-refresh-approval.sha256`) is synchronized.
   - Perform AgentMemory diagnostics and memory consolidation checks.

4. **System Understanding & Verification**:
   - Verify tool responsiveness via MCP Router and CLI commands (`gitnexus`, `graphify query`, `agentmemory status`, `wiki_search`).
   - Run `knowledge-status.sh --json` to verify updated freshness telemetry.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `workspace-index-freshness`: Update official provider version pin to GitNexus `1.6.12` and Graphify `0.9.71`.

## Impact

- **Affected Toolchains**: `graphifyy` (uv tool environment), `gitnexus` (CLI/MCP), `agentmemory` (daemon/MCP), `wiki` (markdown documentation).
- **Affected Repositories**: `~/Developer/scripts/knowledge-refresh/`, `~/Developer/wiki/`, `~/Developer/platform/openspec-store/`, and inventoried repos under `~/Developer/`.
- **Breaking Changes**: None. Graphify 0.9.71 and GitNexus 1.6.12 maintain backwards-compatible CLI flags and schema contracts.
