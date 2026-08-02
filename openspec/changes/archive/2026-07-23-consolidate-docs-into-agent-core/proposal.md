## Why

agent-core documentation is scattered across 3 locations with no single source of truth:

```
agent-core/docs/              (13 implementation guides)
tdt-meta/docs/agent-core/     (6 additional docs — evaluation, mcp, streaming, etc.)
ai-agents-comparison/         (8 research docs — framework comparison, feature mapping)
```

This fragmentation makes docs hard to find, maintain, and keep in sync. Developers must check 3 directories to get the full picture.

## What Changes

### Move from tdt-meta/docs/agent-core/ → agent-core/docs/
- `evaluation.md` — evaluation framework guide
- `mcp-integration.md` — MCP integration guide
- `skill-profiles.md` — skill profile configuration
- `streaming.md` — streaming API guide
- `vector-memory.md` — vector memory guide
- `integration-contract.md` — keep in tdt-meta (cross-cutting contract), update references

### Move from ai-agents-comparison/ → agent-core/docs/research/
- 7 research files (framework comparison, feature mapping, best practices, etc.)
- Absorb typed-state-summary into orchestration.md

### Create new files
- `agent-core/docs/README.md` — overview + index

### Update references
- CLAUDE.md, AGENTS.md, tdt-meta/docs/ integration-contract.md

### Delete
- `ai-agents-comparison/` directory entirely

## Capabilities

### New Capabilities

- `agent-docs-research`: Research and analysis documentation (framework comparisons, feature mapping, upgrade opportunities)

### Modified Capabilities

- `agent-core-orchestration`: Absorb typed-state summary into orchestration docs

## Impact

- **Files moved**: 12 files (6 from tdt-meta, 7 from ai-agents-comparison, minus 1 absorbed)
- **Files created**: 1 (`agent-core/docs/README.md`)
- **Files deleted**: 8 (`ai-agents-comparison/` directory)
- **Files updated**: 2-3 (CLAUDE.md, AGENTS.md, integration-contract.md)
- **Dependencies**: None
- **Breaking changes**: None — docs reorganization only

## Non-Goals

- Rewriting content of any docs (only moving + minor sync)
- Changing implementation docs (`agent-core/docs/*.md` existing content)
- Changing agent-core code
