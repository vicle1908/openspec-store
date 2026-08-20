## 1. Capture Pre-Upgrade Baseline

- [ ] 1.1 In agent-core: run `uv run pytest --co -q | tail -1` to count tests, `uv run ruff check . --select I001` for lint baseline
- [ ] 1.2 In agent-harness: run `uv run pytest --co -q | tail -1` to count tests, `uv run ruff check . --select I001` for lint baseline
- [ ] 1.3 In agent-docs-sync: run `uv run pytest --co -q | tail -1` to count tests, `uv run ruff check . --select I001` for lint baseline

## 2. Update Version Pins

- [ ] 2.1 Update `agent-core/pyproject.toml`: change `pydantic-ai-harness[dynamic-workflow]==0.11.0` to `pydantic-ai-harness>=0.23.0,<0.24`
- [ ] 2.2 Update `agent-harness/pyproject.toml`: change `pydantic-ai-harness[dynamic-workflow]==0.11.0` to `pydantic-ai-harness>=0.23.0,<0.24`
- [ ] 2.3 Update `agent-docs-sync/pyproject.toml`: change `pydantic-ai-harness[dynamic-workflow]==0.11.0` to `pydantic-ai-harness>=0.23.0,<0.24`
- [ ] 2.4 Run `uv sync` in agent-core to resolve updated lockfile
- [ ] 2.5 Run `uv sync` in agent-harness to resolve updated lockfile
- [ ] 2.6 Run `uv sync` in agent-docs-sync to resolve updated lockfile

## 3. Verify Compatibility

- [ ] 3.1 Run `uv run pytest` in agent-core — all tests pass, compare count to baseline
- [ ] 3.2 Run `uv run pytest` in agent-harness — all tests pass, compare count to baseline
- [ ] 3.3 Run `uv run pytest` in agent-docs-sync — all tests pass, compare count to baseline
- [ ] 3.4 Run `uv run ruff check . --select I001` in all 3 repos — no new findings
- [ ] 3.5 Run `uv run ruff format --check .` in all 3 repos — format clean
- [ ] 3.6 Run `uv run mypy src/ --strict` in all 3 repos — no type errors

## 4. Update Dependency Baseline Tests

- [ ] 4.1 Update `agent-core/tests/test_dependency_baseline.py`: change harness version from `"0.11.0"` to `"0.23.0"` and remove `DynamicWorkflow` import assertion if present
- [ ] 4.2 Update `agent-harness/tests/test_dependency_baseline.py`: change harness version from `"0.11.0"` to `"0.23.0"`
- [ ] 4.3 Update `agent-docs-sync/tests/test_dependency_baseline.py`: change harness version from `"0.11.0"` to `"0.23.0"` and remove `DynamicWorkflow` import assertion if present
- [ ] 4.4 Re-run dependency baseline tests to verify they pass

## 5. Fix Any Issues

- [ ] 5.1 Fix any type errors from harness version upgrade (if any)
- [ ] 5.2 Fix any test failures from harness version upgrade (if any)
- [ ] 5.3 Fix any ruff/mypy findings introduced by version changes
- [ ] 5.4 Re-run full verification suite until all gates pass

## 6. Commit and Archive

- [ ] 6.1 Commit agent-core changes: `git add pyproject.toml uv.lock tests/test_dependency_baseline.py && git commit`
- [ ] 6.2 Commit agent-harness changes: `git add pyproject.toml uv.lock tests/test_dependency_baseline.py && git commit`
- [ ] 6.3 Commit agent-docs-sync changes: `git add pyproject.toml uv.lock tests/test_dependency_baseline.py && git commit`
- [ ] 6.4 Archive the OpenSpec change: `openspec archive upgrade-pydantic-ai-harness --yes`
- [ ] 6.5 Commit openspec-store archive: `git add -A && git commit`
- [ ] 6.6 Run `openspec validate --all --strict` to confirm no regressions
