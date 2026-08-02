## Why

Comprehensive research from official sources (PyPI, GitHub repos, pydantic.dev docs) reveals several inaccuracies and gaps in the agent-core research docs:

1. **Durable execution not documented** — 4 official solutions (Temporal, DBOS, Prefect, Restate) with built-in capabilities exist but aren't mentioned
2. **Streaming v3 not documented** — LangGraph v1.2.0+ introduced content-block-centric streaming with SubgraphTransformer
3. **Harness capability matrix outdated** — Several capabilities are now stable that were listed as "Not implemented"
4. **Version references inconsistent** — Some docs reference v0.7.0 (old GitHub releases) while installed version is v0.10.0
5. **Missing capabilities** — On-demand capabilities, RuntimeAuthoring, ExaSearch not documented

## What Changes

- Update `framework-comparison.md` with latest version numbers and new features
- Update `upgrade-opportunities.md` with accurate harness capability statuses
- Update `feature-mapping.md` with new capabilities and accurate status
- Update `pydanticai-langgraph.md` with streaming v3 and durable execution
- Update `validation-report.md` with latest research findings

## Capabilities

### Modified Capabilities

- `agent-docs-research`: Update research documentation with latest findings from official sources

## Impact

- **Files modified**: 5 research docs in `agent-core/docs/research/`
- **Dependencies**: None
- **Breaking changes**: None — docs only
