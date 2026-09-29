# Design

## Context

The workspace relies on four interrelated tooling and knowledge systems:
1. **GitNexus** (`1.6.12`): Provides deep AST symbol mapping, call graph execution flows, and impact analysis for coding agents.
2. **Graphify** (`graphifyy` `0.9.69` -> `0.9.71`): Generates conceptual knowledge graphs, community clusters, and god node abstractions across workspace repositories.
3. **AgentMemory** (`0.9.29`): Persistent agent memory service running at `http://localhost:3111`, offering knowledge graph extraction, memory consolidation, and smart search.
4. **LLM Wiki** (`~/Developer/wiki`): Curated Karpathy-style markdown knowledge base indexed and queried via `wiki-mcp-server`.

## Technical Approach

### 1. Tooling Upgrade & Provider Panning

- Execute `uv tool upgrade graphifyy` to advance `graphifyy` from `0.9.69` to `0.9.71`.
- Verify executable availability and version output:
  - `gitnexus --version` -> `1.6.12`
  - `graphify --version` -> `graphify 0.9.71`
  - `agentmemory --help` -> `@agentmemory/agentmemory` `0.9.29`
- Update `specs/workspace-index-freshness/spec.md` delta specification to record `graphifyy` `0.9.71` and `gitnexus` `1.6.12` as the approved versions.

### 2. Knowledge Index & Graph Refresh Strategy

- Check `knowledge-status.sh --json` baseline before updates.
- Identify repositories with STALE Graphify and GitNexus indexes:
  - Graphify: run incremental `graphify update .` in target repositories (`shb-core`, `shb-browser-cli`, `shb-tools`, `shb-ai-harness-skills`, `shb-ai-review`, `shb-webhook-receiver`, `shb-jira-tools`, `shb-mcp-servers`, `shb-observability`, `tdt-scheduler`, etc.).
  - GitNexus: ensure `.gitnexus/` indexes reflect current HEAD revisions.
- Execute AgentMemory health diagnostics and memory consolidation checks via CLI/MCP.

### 3. Wiki Knowledge Base Updates

- Update stale files flagged by `python3 ~/Developer/wiki/scripts/wiki-lint.py`:
  - `entities/gitnexus.md`: Update version to 1.6.12, document MCP tools and current usage.
  - `entities/graphify.md`: Update version to 0.9.71, document incremental update behavior and CLI flags.
  - `entities/tdt-observability.md`: Update status and last-modified metadata.
  - `SCHEMA.md`: Refresh audit timestamp.
  - `references/developer-knowledge-refresh-2026-08-25.md`: Refresh audit metadata.
- Create `entities/shb.md`:
  - Document the newly established SHB banking ecosystem (12 repositories under `~/Developer/shb/`): `shb-core`, `shb-agent-core`, `shb-agent-harness`, `shb-ai-harness-skills`, `shb-agent-skills`, `shb-browser-cli`, `shb-ai-review`, `shb-webhook-receiver`, `shb-jira-tools`, `shb-mcp-servers`, `shb-observability`, `shb-tools`.
  - Add link from `index.md`.
- Verify wiki integrity:
  - Run `python3 ~/Developer/wiki/scripts/wiki-lint.py`.
  - Run `pytest ~/Developer/wiki/tests/test_wiki_lint.py`.

### 4. Verification & Validation

- Run `knowledge-status.sh --json` to corroborate updated freshness across target repositories.
- Test tool responsiveness:
  - Query GitNexus symbol analysis or context.
  - Query Graphify graph via `graphify query`.
  - Check AgentMemory status and session list.
  - Query Wiki via MCP or CLI.
