## 1. ConsumerRuntimeProfile changes

- [ ] 1.1 Change `max_iterations: int = Field(default=15)` to `max_iterations: int | None = Field(default=None)` in `sdk/config.py`
- [ ] 1.2 Change `timeout_seconds: float = Field(default=180.0)` to `timeout_seconds: float | None = Field(default=None)` in `sdk/config.py`
- [ ] 1.3 Verify `ConsumerRuntimeProfile()` defaults to `None` for both fields

## 2. AgentRuntime enforcement

- [ ] 2.1 Update `AgentRuntime.__init__` to accept `total_tokens_limit: int | None = None` parameter
- [ ] 2.2 Update `UsageLimits` calls in `AgentRuntime.run()` (3 sites) to pass `total_tokens_limit=None` when no limit is set
- [ ] 2.3 Verify `UsageLimits(request_limit=None, total_tokens_limit=None)` means no cap (pydantic-ai test)
- [ ] 2.4 Verify `asyncio.wait_for(..., timeout=None)` means no timeout (Python stdlib)

## 3. BaseAgent enforcement

- [ ] 3.1 Update `effective_max_iterations` to return `None` when flavor/limits are `None`
- [ ] 3.2 Update `effective_timeout` to return `None` when flavor/limits are `None`
- [ ] 3.3 Verify `MAX_ITERATIONS` is not raised when max_iterations is `None`
- [ ] 3.4 Verify `AGENT_TIMEOUT` is not raised when timeout is `None`

## 4. Flavor defaults

- [ ] 4.1 Change `FlavorDefaults.budget_usd` default from `None` to `None` (already unlimited)
- [ ] 4.2 Update flavor definitions in `flavors.py` to use `None` for unlimited modes
- [ ] 4.3 Verify flavor merge logic handles `None` correctly

## 5. Config loading

- [ ] 5.1 Verify `~/.tdt/config.yaml` `agent.max_iterations: null` loads as `None`
- [ ] 5.2 Verify `~/.tdt/config.yaml` `agent.budget_usd: null` loads correctly (unlimited)
- [ ] 5.3 Verify unset fields default to `None` (unlimited)

## 6. Validation and testing

- [ ] 6.1 Run agent-core test suite
- [ ] 6.2 Run agent-docs-sync test suite
- [ ] 6.3 Update any tests that assert specific iteration counts
- [ ] 6.4 Run live sync pipeline to verify unlimited iterations work
- [ ] 6.5 Verify budget_usd cap still enforced when set
