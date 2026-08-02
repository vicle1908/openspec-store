## Context

agent-core uses GitNexus for symbol-level code intelligence and Graphify for concept-level knowledge graphs. Both tools need updating.

**Current state:**
- GitNexus: v1.6.9, stale index (df84913 vs aa1aeac), 0 symbols/relationships
- Graphify: v0.7.15 (outdated), no graphify-out/ directory

## Goals / Non-Goals

**Goals:**
- Re-index GitNexus for accurate code intelligence
- Update Graphify to v0.9.14 (11 correctness fixes, better caching)
- Generate knowledge graph for concept-level exploration
- Update documentation with current tool usage

**Non-Goals:**
- Modify agent-core source code
- Change tool configurations
- Update other repositories

## Decisions

### Decision 1: Re-index GitNexus

**Choice:** Run `node .gitnexus/run.cjs analyze`

**Details:**
- Command takes ~2-5 minutes for 221 files
- Produces fresh symbol, relationship, and process data
- Enables impact analysis, call graphs, execution flows

### Decision 2: Update Graphify to v0.9.14

**Choice:** `pip install --upgrade graphifyy`

**Benefits of v0.9.14:**
- 11 correctness fixes
- Better extraction caching
- Cross-repo graph merging
- Improved git hooks

### Decision 3: Generate Knowledge Graph

**Choice:** `graphify analyze .`

**Output:**
- `graphify-out/graph.json` — queryable graph
- `graphify-out/graph.html` — interactive visualization
- `graphify-out/GRAPH_REPORT.md` — analysis report

### Decision 4: Register with Claude Code

**Choice:** `graphify install --platform claude`

**Result:** /graphify skill available in Claude Code sessions

## Risks / Trade-offs

**[Risk] Update breaking changes** → v0.9.x may have API changes. Mitigation: Test after update.
**[Risk] Large graph size** → agent-core has 221 files, manageable. Mitigation: Use --no-viz for CI.
