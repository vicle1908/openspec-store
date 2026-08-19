## Why

During agent-docs-sync feature verification, three agent-core bugs were discovered that prevent correct LLM pipeline behavior:

1. **Token tracking reads wrong attributes**: `hooks.py` reads `prompt_tokens`/`completion_tokens` from pydantic-ai's `RunUsage`, but pydantic-ai v2.31 uses `input_tokens`/`output_tokens`. All LLM calls logged 0 tokens despite real usage.

2. **Logs go to stdout**: `logging.py` creates `StreamHandler(sys.stdout)`, routing all structlog output to stdout. This mixes log messages with `typer.echo` report output, making sync stdout unparseable.

3. **Missing deps_type**: `AgentRuntime` constructs pydantic-ai's `Agent` without `deps_type=AgentRuntimeDeps`, causing pydantic-ai to pass a string as `ctx` to tool functions (triggers `'str' object has no attribute 'deps'` in `grep_search` and other builtin tools).

Additionally, a defensive type guard for `ctx.deps` access was added, and the pydantic-ai version baseline was stale in tests (2.18.0 vs actual 2.31.0).

## What Changes

- **BREAKING** (log format unchanged, but internal attribute mapping corrected): `hooks.py` reads `input_tokens`/`output_tokens` from `RunUsage`, maps to `prompt_tokens`/`completion_tokens` in structured log output
- `logging.py`: `StreamHandler(sys.stdout)` → `StreamHandler(sys.stderr)`
- `agent.py`: `Agent` constructor gets `deps_type=AgentRuntimeDeps`; `hasattr(ctx, "deps")` type guard in `_prepare_tools`
- `tools.py`: `hasattr(ctx, "deps")` type guard in `_run_via_registry`
- `test_dependency_baseline.py`: pydantic-ai version 2.18.0 → 2.31.0

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `builtin-hooks`: Corrected token attribute names from `prompt_tokens`/`completion_tokens` to `input_tokens`/`output_tokens` (code reads pydantic-ai's actual fields); added log destination requirement (stderr, not stdout)
- `agent-core-model-resolution`: Added defensive type guard documentation for `ctx.deps` access and `deps_type=AgentRuntimeDeps` construction

## Impact

- **Code**: `agent_core/_ai/hooks.py` (5 lines), `agent_core/foundation/logging.py` (1 line), `agent_core/_ai/agent.py` (12 lines), `agent_core/_ai/tools.py` (7 lines), tests (2 lines)
- **Specs**: 2 modified capabilities
- **Tests**: All 644 agent-core tests pass (excluding pre-existing scheduler/docker failures)
