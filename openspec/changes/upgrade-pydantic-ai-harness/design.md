## Design: pydantic-ai-harness Upgrade

### Version Constraint Changes

| Repo | Current | Target | Rationale |
|---|---|---|---|
| agent-core | `pydantic-ai-harness[dynamic-workflow]==0.11.0` | `pydantic-ai-harness>=0.23.0,<0.24` | Unlock 12 releases of improvements |
| agent-harness | `pydantic-ai-harness[dynamic-workflow]==0.11.0` | `pydantic-ai-harness>=0.23.0,<0.24` | Align with agent-core |
| agent-docs-sync | `pydantic-ai-harness[dynamic-workflow]==0.11.0` | `pydantic-ai-harness>=0.23.0,<0.24` | Align with agent-core |

### Extra Removal

The `[dynamic-workflow]` extra is removed because:
- `DynamicWorkflow` is only imported in `tests/test_dependency_baseline.py` as a version pin check
- No production code references `DynamicWorkflow`
- Removing the extra reduces install footprint (removes dynamic-workflow-specific dependencies)

### API Compatibility Analysis

All 5 harness modules used by the workspace appear API-compatible between 0.11.0 and 0.23.0:

| Module | Classes Used | Status |
|---|---|---|
| `step_persistence` | `StepPersistence`, `InMemoryStepStore`, `ContinuableSnapshot`, `SqliteStepStore`, `continue_run` | ✅ Compatible |
| `memory` | `Memory`, `MemoryStore`, `MemoryFile`, `MemoryMutation`, `MemoryConflictError`, `InMemoryStore`, `FileStore`, `SqliteMemoryStore` | ✅ Compatible |
| `guardrails` | `GuardResult`, `InputGuard`, `OutputGuard` | ✅ Compatible |
| `subagents` | `SubAgent`, `SubAgents` | ✅ Compatible |
| `dynamic_workflow` | `DynamicWorkflow` (test-only) | ✅ Compatible (keeping for test) |

### New Dependencies (transitive)

The upgrade introduces new transitive dependencies:
- `genai-prices>=0.0.71` — cost tracking
- `httpx2>=2.0` — HTTP client (replaces httpx internally)
- `pydantic-graph==2.32.0` — graph execution engine
- `logfire-api>=3.14.1` — observability

### Breaking Changes to Verify

1. **Capability naming convention rename** (0.13.0) — verify no string-based capability references
2. **Pydantic AI version compatibility** — 0.23.0 requires pydantic-ai 2.28+ (satisfied by 2.32.0)

### Verification Strategy

Per-repo verification gates:
```bash
uv sync                              # Resolve updated lockfile
uv run pytest                        # Full test suite
uv run ruff check . --select I001    # Import ordering
uv run ruff format --check .         # Format check
uv run mypy src/ --strict            # Type checking
```

Cross-repo: agent-harness and agent-docs-sync import agent-core — verify import chain works.

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| API breaking change in used modules | Low | Medium | All 5 modules appear stable; run full tests |
| New transitive dependency conflicts | Low | Low | `uv sync` handles resolution; revert if needed |
| httpx2 conflict with workspace httpx | Low | Medium | httpx2 is separate package; no conflict expected |
| Type errors from new harness | Low | High | Run mypy strict; fix any new errors |
