## Why

agent-core's code intelligence tools need updating:

**GitNexus:**
- Index is stale (indexed at df84913, current is aa1aeac)
- Symbol count: 0 (needs re-index)
- Relationship count: 0 (needs re-index)
- Process count: 170 (partial data)

**Graphify:**
- Version outdated: v0.7.15 installed, v0.9.14 latest
- No knowledge graph exists (no graphify-out/ directory)
- Missing concept-level exploration capabilities

**Impact:**
- Inaccurate impact analysis for code changes
- No path finding between modules
- Manual architecture exploration instead of tool-assisted

## What Changes

- **GitNexus**: Re-index to get fresh symbol/relationship/process data
- **Graphify**: Update to v0.9.14 and generate knowledge graph
- **Documentation**: Update AGENTS.md with tool usage patterns

## Capabilities

### New Capabilities
- `gitnexus-reindex`: Fresh symbol/relationship index
- `graphify-generate`: Knowledge graph for exploration

### Modified Capabilities
- `documentation`: Update AGENTS.md references

## Impact

- **Files modified**: .gitnexus/ (re-index), graphify-out/ (new), AGENTS.md (updated)
- **Dependencies**: graphifyy (updated to v0.9.14)
- **No breaking changes**: Tooling improvements only
