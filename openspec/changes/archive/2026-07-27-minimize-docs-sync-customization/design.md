## Context

`agent-docs-sync` is the first production consumer of `agent-core` SDK. After the previous change (`standardize-consumer-framework-patterns`) fixed `build_toolkit` and `build_agent`, the consumer still has patterns that bypass SDK helpers. This change addresses remaining gaps to minimize customization.

**Current state (validated via GitNexus + code review):**
- 9 imports bypass `agent_core.sdk` (import from internal modules)
- 19 manual `ToolRegistry.register()` calls (could use `build_toolkit`)
- 3 tools making external calls without `@resilient_tool` (no retry/circuit breaker)
- `build_agent()` unused by `agent.py` (most complex agent builder)
- `AgentRequest` typed input unused (tasks passed as strings)
- `on_tool_error` hook manually retries `check_links` and `git_diff` (redundant with `@resilient_tool`)

**Research validation:**
- `resilient_tool` has 0 upstream callers (GitNexus impact: LOW) — safe to adopt
- `build_toolkit` has 0 upstream callers (GitNexus impact: LOW) — safe to adopt
- `BaseAgent.run()` already accepts `AgentRequest` (tested in `agent_base/test_agent.py`)
- `code_reviewer` example demonstrates `AgentRequest` usage pattern
- `resilient_tool` tests confirm decorator works on class-level `execute()` method

## Goals / Non-Goals

**Goals:**
- Fix all non-SDK imports to use `agent_core.sdk` re-exports
- Adopt `build_toolkit()` for tool registration in all agent builders
- Add `@resilient_tool` to external-call tools for retry + circuit breaker
- Extend `build_agent()` with optional `flavors` parameter (backwards-compatible)
- Refactor `agent.py` to use `build_agent()` with pre-built hooks and flavors
- Adopt `AgentRequest` for typed task passing
- Remove redundant `on_tool_error` retry hook (replaced by `@resilient_tool`)

**Non-Goals:**
- Migrating pipelines to `WorkflowEngine` (deferred — not worth refactoring effort now)
- Using `FallbackChain` for tool redundancy (deferred — limited applicability)
- Using `WorkflowResult` as return type (deferred — dict-based works fine)
- Changing tool implementations (all 15 tools already follow `BaseTool[T]`)

## Decisions

### Decision 1: Fix non-SDK imports (9 occurrences)

All 9 imports have verified SDK re-exports. Simple find-and-replace:

| File | Current Import | SDK Import |
|------|---------------|------------|
| `agent.py` | `agent_core.agent_base.hooks` | `agent_core.sdk` |
| `agent.py` | `agent_core.llm_gateway` | `agent_core.sdk` |
| `discovery.py` | `agent_core.agent_base` | `agent_core.sdk` |
| `discovery.py` | `agent_core.llm_gateway` | `agent_core.sdk` |
| `generation.py` | `agent_core.agent_base` | `agent_core.sdk` |
| `generation.py` | `agent_core.agent_base.hooks` | `agent_core.sdk` |
| `generation.py` | `agent_core.llm_gateway` | `agent_core.sdk` |
| `validation.py` | `agent_core.agent_base` | `agent_core.sdk` |
| `validation.py` | `agent_core.llm_gateway` | `agent_core.sdk` |

### Decision 2: Adopt `build_toolkit()` in 4 agent builders

Replace manual `ToolRegistry()` + `.register()` with `build_toolkit()`:

```python
# Before (agent.py):
registry = ToolRegistry()
registry.register(GitDiffTool())
registry.register(ReadDocTool())
# ... 6 more

# After:
from agent_core.sdk import build_toolkit
registry = build_toolkit(tools=[
    GitDiffTool(), ReadDocTool(), WriteDocTool(),
    CheckLinksTool(), ParseSourceTool(), SyncSpecTool(),
])
```

**Impact:** 4 files, ~40 lines reduced, consistent with SDK pattern.

### Decision 3: Add `@resilient_tool` to 3 external-call tools

Apply `@resilient_tool()` decorator to tools making external calls:

| Tool | External Call | Retry Config | Rationale |
|------|-------------|--------------|-----------|
| `CheckLinksTool` | httpx HTTP HEAD | max_retries=2, failure_threshold=3 | HTTP timeouts are transient, lower threshold for faster circuit opening |
| `GitDiffTool` | subprocess git | max_retries=1, failure_threshold=5 | Subprocess failures less frequent, higher threshold |
| `StateTool` | subprocess git + file I/O | max_retries=1, failure_threshold=5 | Same as GitDiffTool |

**Why these 3:** They make network/subprocess calls that can fail transiently. Other tools (read_doc, write_doc, scanner, classifier, enforcer) are pure file I/O or logic — no external calls.

**Impact:** 3 files, ~6 lines added (decorator), `on_tool_error` hook simplified.

### Decision 4: Extend `build_agent()` with `flavors` parameter

Add backwards-compatible `flavors` parameter to `build_agent()`:

```python
def build_agent(
    config: ConsumerConfig | None = None,  # Now optional
    gateway: LLMGateway | None = None,
    tools: list[Any] | None = None,
    name: str | None = None,
    instructions: str = "",
    memory: Any = None,
    hooks: HookRegistry | None = None,
    harness_config: dict[str, Any] | None = None,
    flavors: list[Flavor] | None = None,  # NEW
) -> BaseAgent:
```

**When `flavors` is provided:** Use it instead of creating Flavor from config.
**When `flavors` is None:** Create Flavor from config (existing behavior).
**When both `config` and `flavors` are None:** Raise ValueError.

### Decision 5: Refactor `agent.py` to use `build_agent()`

agent.py keeps its domain-specific logic (hook packs with params, domain hooks, mode-based flavor selection) but delegates BaseAgent construction to `build_agent()`:

```python
def build_doc_sync_agent(gateway, *, mode="full_sync", ...):
    registry = build_toolkit(tools=[...])
    hook_registry = HookRegistry()
    register_pack(hook_registry, "otel_metrics")
    # ... more hook packs with params
    hook_registry.register(...)  # domain hooks
    
    flavor_map = {"check": doc_checker, "generate": doc_generator, "full_sync": doc_full_sync}
    
    return build_agent(
        gateway=gateway,
        name="doc-syncer",
        model="gpt-4o-mini",
        tools=registry,
        hooks=hook_registry,
        flavors=[flavor_map[mode]],  # pre-built flavor
    )
```

### Decision 6: Adopt `AgentRequest` for typed task passing

Replace string tasks with `AgentRequest` in 3 call sites, following the `code_reviewer` example pattern:

```python
# Before (full_pipeline.py):
result = await agent.run(f"Create docs for {file_path}...")

# After:
from agent_core.sdk import AgentRequest
result = await agent.run(AgentRequest(
    task=f"Create docs for {file_path}...",
    context={"repo_root": repo_root, "quadrant": quadrant},
    correlation_id=run_id,
))
```

### Decision 7: Remove redundant `on_tool_error` hook

The `on_tool_error` hook in `agent.py` manually retries `check_links` and `git_diff` on `ConnectionError`/`TimeoutError`/`OSError`. With `@resilient_tool` on these tools, this hook becomes redundant.

**Action:** Remove `on_tool_error` from `agent.py` hook registration. Keep the function in `hooks.py` for backward compatibility but don't register it.

## Risks / Trade-offs

- **[Risk] `@resilient_tool` changes class behavior** → Mitigated by decorator pattern (wraps execute, doesn't modify class). Test with existing test suite.
- **[Risk] `flavors` parameter changes `build_agent` signature** → Mitigated by making it optional with default None. Existing callers unaffected.
- **[Risk] `AgentRequest` changes agent.run() contract** → Mitigated by `BaseAgent.run()` already accepting `AgentRequest` (tested in `agent_base/test_agent.py`).
- **[Trade-off] Skip `WorkflowResult` and `FallbackChain`** → Not worth refactoring effort for minimal value. Revisit if pipelines grow complex.
