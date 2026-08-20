## Why

The agent ecosystem dependency pins are blocking access to latest stable features and creating coordination overhead:

1. **Pydantic AI version cap** — All three agent repos pin `pydantic-ai>=2.31.0,<2.32`, blocking v2.32.0 which ships the capability primitives system (`Thinking()`, `CodeMode()`, `WebSearch()`, `ToolSearch()`), the core/harness split, and native MCP support through capabilities.

2. **pydantic-ai-harness exact pin** — `==0.11.0` exact pin across 3 repos creates tight coupling. Any security fix or bug fix requires coordinated bump across all repos. Investigating and upgrading to latest stable reduces this friction.

3. **OpenTelemetry SDK ceiling** — Pinned `<1.45.0` may block access to newer instrumentation features.

This change is needed now because:
- The capability primitives in Pydantic AI v2.32.0 are the recommended pattern for agent composition
- The exact harness pin prevents independent repo upgrades
- Version drift between pinned and latest grows daily, increasing migration risk

## What Changes

- **MODIFIED**: Update `pydantic-ai` upper bound from `<2.32` to `<2.33` in agent-core, agent-harness, and agent-docs-sync
- **MODIFIED**: Investigate and update `pydantic-ai-harness[dynamic-workflow]` from `==0.11.0` to latest stable across all 3 repos
- **MODIFIED**: Update `pydantic-evals` upper bound from `<3` if needed for compatibility with new pydantic-ai
- Run full test suites in all 3 repos to verify compatibility
- Resolve updated lockfiles via `uv sync`

## Non-goals

- No MCP SDK v2 migration (still beta — deferred to future change)
- No `@anthropic-ai/dxt` → `@anthropic-ai/mcpb` migration (mcp-router scope, separate change)
- No model tier differentiation (config change, not dependency upgrade)
- No new features or schema changes
- No changes to tdt-core, ai-review, ai-harness-skills, or other repos

## Capabilities

### Modified Capabilities

- `agent-core-runtime`: Updated dependency bounds allow access to Pydantic AI v2.32.0 capability primitives and latest harness features
- `agent-harness-workflow`: Updated dependency bounds align with agent-core for consistent workspace behavior

## Impact

- **Runtime:** No runtime behavior changes — dependency bounds are widened, not contract changes
- **Testing:** Full test suite verification required in all 3 repos (agent-core: 69 tests, agent-harness: 33 tests, agent-docs-sync: 38 tests)
- **Lockfiles:** `uv.lock` files will be regenerated in all 3 repos
- **Blast radius:** LOW — changes are additive version bound widening with full test verification
- **Rollback:** Git revert per repo; OpenSpec change preserved in archive
