## Why

pydantic-ai-harness is pinned to `==0.11.0` (released Jul 25, 2026) across 3 repos. The latest stable is **0.23.0** (Aug 19, 2026) — 12 minor releases in 25 days with significant new capabilities, bug fixes, and security improvements.

The exact `==0.11.0` pin creates coordination overhead: any security fix or bug fix requires coordinated bump across all repos. The workspace is also missing 12 releases worth of improvements to the 5 modules actually used (step_persistence, memory, guardrails, subagents, dynamic_workflow).

Additionally, the `[dynamic-workflow]` extra is installed but **not used in production** — only imported in `test_dependency_baseline.py` as a version pin check. Removing it reduces install footprint.

This change is needed now because:
- Security patches and bug fixes in 0.12.0–0.23.0 are not being applied
- The harness is evolving rapidly (12 releases in 25 days) and the workspace should track stable releases
- The exact pin prevents independent repo upgrades
- Documentation references deprecated APIs that will be removed

## What Changes

- **MODIFIED**: Update `pydantic-ai-harness` pin from `==0.11.0` to `>=0.23.0,<0.24` in agent-core, agent-harness, and agent-docs-sync
- **MODIFIED**: Remove `[dynamic-workflow]` extra from all 3 repos (not used in production)
- **MODIFIED**: Create/update dependency baseline tests to reflect new harness version
- **MODIFIED**: Migrate deprecated Guardrails API (GuardResult → GuardrailResult, InputGuard → InputGuardrail, OutputGuard → OutputGuardrail)
- **MODIFIED**: Update all documentation referencing deprecated APIs
- **MODIFIED**: Update OpenSpec specs referencing harness version or deprecated APIs
- Run full test suites in all 3 repos to verify API compatibility
- Resolve updated lockfiles via `uv sync`

## Non-goals

- No new feature adoption (separate change: `integrate-harness-features`)
- No changes to tdt-core, ai-review, ai-harness-skills, or other repos
- No MCP SDK v2 migration (still beta)

## Capabilities

### Modified Capabilities

- `agent-core-runtime`: Updated harness dependency allows access to latest step_persistence, memory, guardrails, and subagent improvements
- `agent-harness-workflow`: Updated dependency bounds align with agent-core

## Impact

- **Runtime:** No runtime behavior changes — dependency bounds are widened, not contract changes
- **Testing:** Full test suite verification required in agent-core (79 tests), agent-harness (38 tests), agent-docs-sync (285 test cases across 41 test files)
- **Lockfiles:** `uv.lock` files will be regenerated in all 3 repos with new harness version and its dependencies (genai-prices, httpx2, pydantic-graph, logfire-api)
- **Documentation:** Multiple doc files reference deprecated APIs that will be migrated
- **Specs:** OpenSpec specs reference harness version and deprecated APIs
- **Blast radius:** LOW — changes are additive version bound widening with full test verification
- **Rollback:** Git revert per repo (both pyproject.toml and uv.lock together); OpenSpec change preserved in archive
