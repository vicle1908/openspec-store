## Why

agent-docs-sync is a Python agent (25 source files, 4 sub-packages) that documents other TDT repos, yet it lacks the code intelligence tooling that17 other repos already have. Without gitnexus indexing, we can't analyze symbol impact before modifying its tools or pipeline. Without graphify, we can't trace how the doc-sync pipeline connects to agent-core, tdt-core, or the LLM gateway. The repo also has 13 uncommitted files and no CLAUDE.md/AGENTS.md — it's the least "workspace-standard" Python repo in the ecosystem.

## What Changes

- **Index agent-docs-sync with gitnexus** — symbol-level code intelligence (impact analysis, blast radius, execution flows)
- **Generate graphify graph for agent-docs-sync** — architecture-level knowledge graph (component relationships, pipeline flow)
- **Install post-commit hook** — use graphify's built-in `hook install` + append gitnexus refresh (incremental, non-blocking)
- **Add CLAUDE.md** — project-specific instructions for AI assistants
- **Add AGENTS.md** — agent orchestration guidance
- **Commit uncommitted files** — 13 modified files brought to a clean state
- **Use gitnexus/graphify to analyze agent-docs-sync** — trace the pipeline architecture, identify hotspots, verify tool dependencies

## Capabilities

### New Capabilities

- `agent-docs-sync-code-intelligence`: GitNexus indexing, graphify graph generation, and post-commit hook for automatic index refresh
- `agent-docs-sync-project-scaffold`: CLAUDE.md, AGENTS.md, and clean git state to bring the repo to workspace standards

### Modified Capabilities

- `agent-docs-sync`: No spec requirements change — this is tooling and project hygiene, not feature work

## Impact

- **Code affected**: None — this is tooling setup and project metadata
- **New files**: `.gitnexus/`, `graphify-out/`, `CLAUDE.md`, `AGENTS.md`, `.git/hooks/post-commit`
- **Git changes**: Commit 13 existing modified files
- **Dependencies**: None new — gitnexus (npx) and graphify CLI already installed
- **Systems**: Agent-docs-sync becomes queryable via gitnexus MCP tools and graphify CLI; indexes auto-refresh after each commit
- **Precedent**: First repo in workspace with post-commit hook for gitnexus/graphify refresh
