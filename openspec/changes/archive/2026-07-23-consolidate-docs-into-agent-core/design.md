## Context

agent-core documentation is fragmented across 3 locations:
- `agent-core/docs/` — 13 implementation guides (the main docs)
- `tdt-meta/docs/agent-core/` — 6 additional docs (evaluation, mcp, streaming, etc.)
- `ai-agents-comparison/` — 8 research docs (framework comparison, feature mapping)

After consolidation, agent-core will have a single `docs/` directory with all documentation.

## Goals / Non-Goals

**Goals:**
- Single source of truth in `agent-core/docs/`
- Self-contained documentation for the agent-core package
- README as entry point with overview + index

**Non-Goals:**
- Rewriting content (only moving + minor sync)
- Changing implementation docs
- Changing agent-core code

## Decisions

### Decision 1: All agent-core docs move into agent-core/docs/

All agent-core-specific documentation belongs in the agent-core package. No docs in tdt-meta/docs/agent-core/ after consolidation.

### Decision 2: integration-contract.md stays in tdt-meta

`integration-contract.md` is a workspace-level contract (how sibling repos consume agent-core). It stays in `tdt-meta/docs/` but gets updated with new paths.

### Decision 3: research/ subdirectory for analysis docs

Research docs (framework comparison, feature mapping, etc.) go in `agent-core/docs/research/` — keeps them organized without polluting main docs.

### Decision 4: Typed-state absorbed into orchestration.md

The typed-state summary is a correction note — its content is already in orchestration.md. Absorb and drop standalone.

### Decision 5: evaluation.md is agent-core-specific

The evaluation framework is built into agent-core (`_ai/evaluation/`). It belongs in `agent-core/docs/`.

## Final Structure

```
agent-core/docs/
├── README.md                    (NEW)
├── architecture.md
├── building-agents.md
├── builtin-tools.md
├── cli.md
├── configuration.md
├── distribution.md
├── evaluation.md                (MOVED from tdt-meta)
├── extending.md
├── llm-gateway.md
├── memory.md
├── mcp-integration.md           (MOVED from tdt-meta)
├── observability.md
├── orchestration.md             (+ typed-state absorbed)
├── resilience.md
├── scheduling.md
├── skill-profiles.md            (MOVED from tdt-meta)
├── streaming.md                 (MOVED from tdt-meta)
├── vector-memory.md             (MOVED from tdt-meta)
└── research/
    ├── architecture-analysis.md
    ├── best-practices.md
    ├── feature-mapping.md
    ├── framework-comparison.md
    ├── pydanticai-langgraph.md
    ├── upgrade-opportunities.md
    └── validation-report.md
```

## Risks / Trade-offs

- **Risk**: Broken links in other repos → **Mitigation**: Update CLAUDE.md, AGENTS.md, integration-contract.md
- **Trade-off**: Lose tdt-meta/docs/agent-core/ directory → **Benefit**: Single source of truth
