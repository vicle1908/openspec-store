## 1. Capture Pre-Upgrade Baseline

- [ ] 1.1 In agent-core: run `uv run pytest --co -q | tail -1` to count tests, `uv run ruff check . --select I001` for lint baseline
- [ ] 1.2 In agent-harness: run `uv run pytest --co -q | tail -1` to count tests, `uv run ruff check . --select I001` for lint baseline
- [ ] 1.3 In agent-docs-sync: run `uv run pytest --co -q | tail -1` to count tests, `uv run ruff check . --select I001` for lint baseline

## 2. Pre-Upgrade API Smoke Test

- [ ] 2.1 Install harness 0.23.0 in temporary venv and verify all import paths resolve:
  ```bash
  uv run --with pydantic-ai-harness==0.23.0 python -c "
  from pydantic_ai_harness.step_persistence import StepPersistence, InMemoryStepStore, ContinuableSnapshot, SqliteStepStore, continue_run
  from pydantic_ai_harness.memory import Memory, MemoryStore, MemoryFile, MemoryMutation, MemoryOperationConflictError, InMemoryStore, FileStore, SqliteMemoryStore
  from pydantic_ai_harness.guardrails import GuardResult, InputGuard, OutputGuard
  from pydantic_ai_harness.subagents import SubAgent, SubAgents
  from pydantic_ai_harness.dynamic_workflow import DynamicWorkflow
  print('All imports OK')
  "
  ```
- [ ] 2.2 If smoke test fails, identify which class was renamed and update import paths before proceeding

## 3. Update Version Pins

- [ ] 3.1 Update `agent-core/pyproject.toml`: change `pydantic-ai-harness[dynamic-workflow]==0.11.0` to `pydantic-ai-harness>=0.23.0,<0.24`
- [ ] 3.2 Update `agent-harness/pyproject.toml`: change `pydantic-ai-harness[dynamic-workflow]==0.11.0` to `pydantic-ai-harness>=0.23.0,<0.24`
- [ ] 3.3 Update `agent-docs-sync/pyproject.toml`: change `pydantic-ai-harness[dynamic-workflow]==0.11.0` to `pydantic-ai-harness>=0.23.0,<0.24`
- [ ] 3.4 Run `uv sync` in agent-core to resolve updated lockfile
- [ ] 3.5 Run `uv sync` in agent-harness to resolve updated lockfile
- [ ] 3.6 Run `uv sync` in agent-docs-sync to resolve updated lockfile
- [ ] 3.7 Review `uv.lock` diff in all 3 repos: verify no unexpected new packages (expect: genai-prices, httpx2, pydantic-graph, logfire-api)

## 4. Verify Compatibility

- [ ] 4.1 Run `uv run pytest` in agent-core — all tests pass, compare count to baseline
- [ ] 4.2 Run `uv run pytest` in agent-harness — all tests pass, compare count to baseline
- [ ] 4.3 Run `uv run pytest` in agent-docs-sync — all tests pass, compare count to baseline
- [ ] 4.4 Run `uv run ruff check .` in all 3 repos — full lint pass (not just I001)
- [ ] 4.5 Run `uv run ruff check . --select I001` in all 3 repos — import ordering clean
- [ ] 4.6 Run `uv run ruff format --check .` in all 3 repos — format clean
- [ ] 4.7 Run `uv run mypy src/ --strict` in all 3 repos — no type errors

## 5. Update Dependency Baseline Tests

- [ ] 5.1 Update `agent-core/tests/test_dependency_baseline.py`: change harness version from `"0.11.0"` to `"0.23.0"` and remove `DynamicWorkflow` import assertion if present
- [ ] 5.2 Create `agent-harness/tests/test_dependency_baseline.py` if it doesn't exist: add harness version assertion for `"0.23.0"`
- [ ] 5.3 Create `agent-docs-sync/tests/test_dependency_baseline.py` if it doesn't exist: add harness version assertion for `"0.23.0"`
- [ ] 5.4 Re-run dependency baseline tests to verify they pass

## 6. Fix Any Issues

- [ ] 6.1 Fix any type errors from harness version upgrade (if any)
- [ ] 6.2 Fix any test failures from harness version upgrade (if any)
- [ ] 6.3 Fix any ruff/mypy findings introduced by version changes
- [ ] 6.4 Re-run full verification suite until all gates pass

## 7. Commit and Archive

- [ ] 7.1 Commit agent-core changes: `git add pyproject.toml uv.lock tests/test_dependency_baseline.py && git commit`
- [ ] 7.2 Commit agent-harness changes: `git add pyproject.toml uv.lock tests/test_dependency_baseline.py && git commit`
- [ ] 7.3 Commit agent-docs-sync changes: `git add pyproject.toml uv.lock tests/test_dependency_baseline.py && git commit`
- [ ] 7.4 Archive the OpenSpec change: `openspec archive upgrade-pydantic-ai-harness --yes`
- [ ] 7.5 Commit openspec-store archive: `git add -A && git commit`
- [ ] 7.6 Run `openspec validate --all --strict` to confirm no regressions

## 8. Verify Rollback Works

- [ ] 8.1 In agent-core: `git stash && git checkout main -- pyproject.toml uv.lock && uv sync && uv run pytest -q && git stash pop`
- [ ] 8.2 Verify rollback restores previous harness version and all tests pass
