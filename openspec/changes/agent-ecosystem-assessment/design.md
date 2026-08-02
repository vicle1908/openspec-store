## Assessment Methodology

All findings were validated by running actual tool output:
- `uv run pytest` with specific exclusions for environment-dependent tests
- `uv run ruff check src/` for code quality
- `uv run <cli> --help` for CLI availability
- `grep -rh 'from agent_core' src/` for cross-repo coupling
- `openspec validate --strict --all` for spec validation

## Validated Test Baseline

| Repo | Passed | Skipped | Notes |
|------|--------|---------|-------|
| agent-core | 608 | 1 | Scheduler manifest fixtures absent in isolated home |
| agent-docs-sync | 210 | 0 | 4 warnings (deprecation) |
| agent-harness | 323 | 0 | — |
| **Total** | **1,141** | **1** | Excludes env-dependent secret scanning tests |

The 6 excluded tests (`test_secret_scanning_policy.py`, `test_docker_local_dev.py`)
require `.github/workflows/ci.yml` which doesn't exist in these repos. This is
an environment gap, not a code bug.

## Module Coverage Assessment

Modules with test ratio below 0.40 are flagged:

| Module | src LOC | test LOC | ratio | Status |
|--------|---------|----------|-------|--------|
| llm_gateway | 559 | 153 | 0.27 | ⚠ Needs attention |
| foundation | 1,290 | 452 | 0.35 | ⚠ Needs attention |
| cli | 974 | 408 | 0.41 | Borderline |

The `llm_gateway` module is thin by design — it delegates to LiteLLM and the
real complexity lives in provider configuration and retry logic. The 153 test
lines cover the factory, gateway interface, and error propagation. The
`foundation` module includes settings, errors, logging, tracing, and migrations
— the lower ratio reflects that several sub-modules (logging, tracing) are
wiring-heavy with less branching logic.

## Cross-Repo Coupling

| Consumer | Unique import lines from core | Depth |
|----------|-------------------------------|-------|
| agent-docs-sync | 19 | Deep — uses SDK, memory, resilience, observability, tools, composition, agents |
| agent-harness | 7 | Clean — uses LLMGateway, ConsumerRuntimeProfile, lifecycle_identity, checkpointer |

agent-docs-sync's deep coupling is expected: it's a full agent built on
agent-core's BaseAgent, ToolRegistry, Memory, and WorkflowBuilder. The 19
imports span 7 distinct SDK groups.

agent-harness's clean boundary (7 imports, 3 SDK groups) reflects its design as
a planning workflow that uses agent-core primarily for identity resolution,
gateway access, and checkpointing.

## Spec Coverage Boundaries

Two agent-core docs lack dedicated specs:
- `agent-config.md`: Short usage guide for `load_agent_config()`. Covered by
  `agent-core-components` (SDK composition) and `agent-core-invocation-contract`.
- `agent-step-persistence.md`: Composition guide for step persistence. Covered
  by `agent-core-components` (SDK composition).

Both are reference docs describing how to use existing APIs, not normative
behavior contracts. No new specs needed.
