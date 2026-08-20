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

All 5 harness modules used by the workspace appear API-compatible between 0.11.0 and 0.23.0. **Compatibility verified via pre-upgrade smoke test** (task 2.1):

| Module | Classes Used | Import Path | Status |
|---|---|---|---|
| `step_persistence` | `StepPersistence`, `InMemoryStepStore`, `ContinuableSnapshot`, `SqliteStepStore`, `continue_run` | `pydantic_ai_harness.step_persistence` | ✅ Compatible |
| `memory` | `Memory`, `MemoryStore`, `MemoryFile`, `MemoryMutation`, `MemoryOperationConflictError`, `InMemoryStore`, `FileStore`, `SqliteMemoryStore` | `pydantic_ai_harness.memory` | ✅ Compatible |
| `guardrails` | `GuardResult`, `InputGuard`, `OutputGuard` | `pydantic_ai_harness.guardrails` | ✅ Compatible |
| `subagents` | `SubAgent`, `SubAgents` | `pydantic_ai_harness.subagents` | ✅ Compatible |
| `dynamic_workflow` | `DynamicWorkflow` (test-only) | `pydantic_ai_harness.dynamic_workflow` | ✅ Compatible (keeping for test) |

**Note:** The workspace uses `MemoryOperationConflictError` (not `MemoryConflictError`). Both names exist in the 0.23.0 API — `MemoryConflictError` is for path conflicts, `MemoryOperationConflictError` is for operation reuse. The workspace correctly uses the more specific variant.

### New Dependencies (transitive)

The upgrade introduces new transitive dependencies:
- `genai-prices>=0.0.71` — cost tracking
- `httpx2>=2.0` — HTTP client (replaces httpx internally; separate package, no conflict)
- `pydantic-graph==2.32.0` — graph execution engine
- `logfire-api>=3.14.1` — observability (opt-in telemetry, requires explicit configuration)

### Breaking Changes to Verify

1. **Capability naming convention rename** (0.13.0) — Capability class names were standardized (e.g., `StepPersistence` → consistent naming). The workspace uses class references (not string-based), so this is low risk. Verified via smoke test.
2. **Pydantic AI version compatibility** — 0.23.0 requires pydantic-ai 2.28+ (satisfied by current 2.32.0)

### Transitive Breakage Risk

agent-harness depends on agent-core (`agent-core>=0.2,<0.3`), which depends on the harness. If the harness upgrade changes a type signature that agent-core re-exports, agent-harness could break without directly importing the harness. **Mitigation:** Full test suite in agent-harness verifies transitive compatibility.

### Verification Strategy

Per-repo verification gates:
```bash
uv sync                              # Resolve updated lockfile
uv run pytest                        # Full test suite
uv run ruff check .                  # Full lint (not just I001)
uv run ruff check . --select I001    # Import ordering
uv run ruff format --check .         # Format check
uv run mypy src/ --strict            # Type checking
```

Cross-repo: agent-harness and agent-docs-sync import agent-core — verify import chain works.

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| API breaking change in used modules | Low | Medium | Pre-upgrade smoke test catches renames; full test suite verifies |
| New transitive dependency conflicts | Low | Low | `uv sync` handles resolution; revert if needed |
| httpx2 conflict with workspace httpx | Low | Medium | httpx2 is separate package; no conflict expected |
| Type errors from new harness | Low | High | Run mypy strict; fix any new errors |
| Transitive breakage through agent-core | Low | Medium | agent-harness full test suite verifies transitive compatibility |
| logfire-api silent telemetry | Low | Low | Opt-in only; requires explicit configuration |
| Rollback lockfile inconsistency | Low | Low | Revert both pyproject.toml and uv.lock together |
