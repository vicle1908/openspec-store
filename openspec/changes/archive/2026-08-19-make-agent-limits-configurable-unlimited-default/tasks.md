## 1. ConsumerRuntimeProfile changes (agent-core)

- [x] 1.1 Change `max_iterations: int = Field(default=15, ge=1, le=100)` to `max_iterations: int | None = Field(default=None)` in `sdk/config.py`
- [x] 1.2 Change `timeout_seconds: float = Field(default=180.0, gt=0)` to `timeout_seconds: float | None = Field(default=None)` in `sdk/config.py`
- [x] 1.3 Verify `ConsumerRuntimeProfile()` defaults to `None` for both fields

## 2. AgentRuntime enforcement (agent-core)

- [x] 2.1 Update `AgentRuntime.__init__` to accept `total_tokens_limit: int | None = None` parameter
- [x] 2.2 Update `UsageLimits` calls in `AgentRuntime.run()` (3 sites) to pass `total_tokens_limit=None` when no limit is set
- [x] 2.3 Update type annotations: `max_iterations: int | None` in `AgentRuntime.__init__` and `set_max_iterations`
- [x] 2.4 Verify `UsageLimits(request_limit=None, total_tokens_limit=None)` means no cap (pydantic-ai test)
- [x] 2.5 Verify `asyncio.wait_for(..., timeout=None)` means no timeout (Python stdlib)

## 3. BaseAgent enforcement (agent-core)

- [x] 3.1 Update `effective_max_iterations` return type to `int | None`
- [x] 3.2 Update `effective_timeout` return type to `float | None`
- [x] 3.3 Update `BaseAgent.__init__` type annotations: `max_iterations: int | None`, `timeout_seconds: float | None`
- [x] 3.4 Verify `MAX_ITERATIONS` is not raised when max_iterations is `None`
- [x] 3.5 Verify `AGENT_TIMEOUT` is not raised when timeout is `None`

## 4. Flavor defaults (agent-core)

- [x] 4.1 Confirm `FlavorDefaults` already accepts `None` for all fields (no change needed)
- [x] 4.2 Keep flavor-level numeric defaults as-is (per-role safety rails)
- [x] 4.3 Verify flavor merge logic handles `None` correctly

## 5. Config loading (agent-core)

- [x] 5.1 Verify `~/.tdt/config.yaml` `agent.max_iterations: null` loads as `None`
- [x] 5.2 Verify `~/.tdt/config.yaml` `agent.budget_usd: null` loads correctly (unlimited)
- [x] 5.3 Verify unset fields default to `None` (unlimited)

## 6. agent-docs-sync consumer alignment

- [x] 6.1 Update `EffectiveRuntimeControls.max_iterations` to `int | None` and `timeout_seconds` to `float | None` in `operation_context.py`
- [x] 6.2 Update `NormalizedResult.effective_max_iterations` and `effective_timeout_seconds` to `int | None` / `float | None`; serialize `None` as `"unlimited"` in `to_report_dict()`
- [x] 6.3 Update `RuntimeConfigLike.timeout_seconds` return type to `float | None` in `config.py`
- [x] 6.4 Add sentinel mapping in `_apply_environment`: `"none"` (case-insensitive) → `None` for max_iterations, timeout_seconds, total_tokens_limit
- [x] 6.5 Update spec text `agent-docs-sync-tdt-runtime/spec.md` to remove hardcoded `max_iterations=20, timeout=300s` and reflect unlimited default possibility

## 7. Validation and testing

- [x] 7.1 Run agent-core test suite
- [x] 7.2 Run agent-docs-sync test suite
- [x] 7.3 Update any tests that assert specific iteration counts
- [x] 7.4 Add new tests: ConsumerRuntimeProfile with None propagates through EffectiveRuntimeControls
- [x] 7.5 Add new test: `DOCS_SYNC_MAX_ITERATIONS=none` resolves to None
- [x] 7.6 Run live sync pipeline to verify unlimited iterations work
- [x] 7.7 Verify budget_usd cap still enforced when set
