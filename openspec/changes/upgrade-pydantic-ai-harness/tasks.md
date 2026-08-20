## 1. Capture Pre-Upgrade Baseline

- [x] 1.1 In agent-core: run `uv run pytest --co -q | tail -1` to count tests, `uv run ruff check . --select I001` for lint baseline
- [x] 1.2 In agent-harness: run `uv run pytest --co -q | tail -1` to count tests, `uv run ruff check . --select I001` for lint baseline
- [x] 1.3 In agent-docs-sync: run `uv run pytest --co -q | tail -1` to count tests, `uv run ruff check . --select I001` for lint baseline

## 2. Pre-Upgrade API Smoke Test

- [x] 2.1 Install harness 0.23.0 in temporary venv and verify all import paths resolve:
  ```bash
  uv run --with pydantic-ai-harness==0.23.0 python -c "
  from pydantic_ai_harness.step_persistence import StepPersistence, InMemoryStepStore, ContinuableSnapshot, SqliteStepStore, continue_run
  from pydantic_ai_harness.memory import Memory, MemoryStore, MemoryFile, MemoryMutation, MemoryConflictError, MemoryOperationConflictError, InMemoryStore, FileStore, SqliteMemoryStore
  from pydantic_ai_harness.guardrails import GuardrailResult, InputGuardrail, OutputGuardrail
  from pydantic_ai_harness.subagents import SubAgent, SubAgents
  from pydantic_ai_harness.dynamic_workflow import DynamicWorkflow
  print('All imports OK')
  "
  ```
- [x] 2.2 If smoke test fails, identify which class was renamed and update import paths before proceeding

## 3. Update Version Pins

- [x] 3.1 Update `agent-core/pyproject.toml`: change `pydantic-ai-harness[dynamic-workflow]==0.11.0` to `pydantic-ai-harness>=0.23.0,<0.24`
- [x] 3.2 Update `agent-harness/pyproject.toml`: change `pydantic-ai-harness[dynamic-workflow]==0.11.0` to `pydantic-ai-harness>=0.23.0,<0.24`
- [x] 3.3 Update `agent-docs-sync/pyproject.toml`: change `pydantic-ai-harness[dynamic-workflow]==0.11.0` to `pydantic-ai-harness>=0.23.0,<0.24`
- [x] 3.4 Run `uv sync` in agent-core to resolve updated lockfile
- [x] 3.5 Run `uv sync` in agent-harness to resolve updated lockfile
- [x] 3.6 Run `uv sync` in agent-docs-sync to resolve updated lockfile
- [x] 3.7 Review `uv.lock` diff in all 3 repos: verify no unexpected new packages (expect: genai-prices, httpx2, pydantic-graph, logfire-api)

## 4. Migrate Deprecated Guardrails API (Source Code)

- [x] 4.1 In `agent-docs-sync/src/agent_docs_sync/guardrails.py`: replace `GuardResult` → `GuardrailResult`
- [x] 4.2 In `agent-docs-sync/src/agent_docs_sync/guardrails.py`: replace `InputGuard` → `InputGuardrail`
- [x] 4.3 In `agent-docs-sync/src/agent_docs_sync/guardrails.py`: replace `OutputGuard` → `OutputGuardrail`
- [x] 4.4 In `agent-docs-sync/src/agent_docs_sync/guardrails.py`: update `GuardResult.block()` → `GuardrailResult.block()`
- [x] 4.5 In `agent-docs-sync/src/agent_docs_sync/guardrails.py`: update `GuardResult.allow()` → `GuardrailResult.allow()`
- [x] 4.6 In `agent-docs-sync/src/agent_docs_sync/guardrails.py`: update `InputGuard(guard=_guard)` → `InputGuardrail(guard=_guard)`
- [x] 4.7 In `agent-docs-sync/src/agent_docs_sync/guardrails.py`: update return type annotations
- [x] 4.8 In `agent-core/src/agent_core/_ai/config.py`: update docstring comment mentioning `InputGuard/OutputGuard`

## 5. Migrate Deprecated Guardrails API (Tests)

- [x] 5.1 In `agent-docs-sync/tests/test_guardrails_integration.py`: replace all deprecated imports
- [x] 5.2 In `agent-docs-sync/tests/test_tools/test_guardrails.py`: replace all deprecated imports
- [x] 5.3 Verify all tests pass after migration

## 6. Migrate Documentation (agent-core)

- [x] 6.1 In `agent-core/docs/harness-integration.md`: update `InputGuard` → `InputGuardrail` references
- [x] 6.2 In `agent-core/docs/harness-integration.md`: update `pydantic_ai_harness.context` → `pydantic_ai_harness.repo_context` references
- [x] 6.3 In `agent-core/docs/framework-integration.md`: update `pydantic-ai-harness==0.11.0` → `pydantic-ai-harness>=0.23.0,<0.24`
- [x] 6.4 In `agent-core/docs/research/feature-mapping.md`: update `InputGuard` → `InputGuardrail` references
- [x] 6.5 In `agent-core/docs/research/pydanticai-langgraph.md`: update `InputGuard` → `InputGuardrail` references
- [x] 6.6 In `agent-core/docs/research/upgrade-opportunities.md`: update harness version and `InputGuard` references

## 7. Migrate Documentation (agent-docs-sync)

- [x] 7.1 In `agent-docs-sync/docs/configuration.md`: update harness version references
- [x] 7.2 In `agent-docs-sync/docs/framework-integration.md`: update `pydantic-ai-harness==0.11.0` → `pydantic-ai-harness>=0.23.0,<0.24`
- [x] 7.3 In `agent-docs-sync/docs/reference/discovery-api.md`: update `InputGuard` → `InputGuardrail` references

## 8. Migrate Documentation (wiki)

- [x] 8.1 In `~/Developer/wiki/references/agent-ecosystem-evaluation-2026-08.md`: update `pydantic-ai-harness==0.11.0` → `pydantic-ai-harness>=0.23.0,<0.24`

## 9. Migrate OpenSpec Specs

- [x] 9.1 In `openspec/specs/agent-framework-verification/spec.md`: update harness version references
- [x] 9.2 In `openspec/specs/configuration/spec.md`: update harness path references if needed
- [x] 9.3 In `openspec/specs/agent-guardrails/spec.md`: update `InputGuard` → `InputGuardrail`, `OutputGuard` → `OutputGuardrail`, `GuardResult` → `GuardrailResult`
- [x] 9.4 In `openspec/specs/_standalone/agent-docs-harness/spec.md`: update `InputGuard` → `InputGuardrail`
- [x] 9.5 In `openspec/specs/agent-docs-research/spec.md`: update `InputGuard` → `InputGuardrail`, `OutputGuard` → `OutputGuardrail`
- [x] 9.6 Verify all specs pass validation after migration

## 10. Verify Compatibility

- [x] 10.1 Run `uv run pytest` in agent-core — all tests pass, compare count to baseline
- [x] 10.2 Run `uv run pytest` in agent-harness — all tests pass, compare count to baseline
- [x] 10.3 Run `uv run pytest` in agent-docs-sync — all tests pass, compare count to baseline
- [x] 10.4 Run `uv run ruff check .` in all 3 repos — full lint pass (not just I001)
- [x] 10.5 Run `uv run ruff check . --select I001` in all 3 repos — import ordering clean
- [x] 10.6 Run `uv run ruff format --check .` in all 3 repos — format clean
- [x] 10.7 Run `uv run mypy src/ --strict` in all 3 repos — no type errors

## 11. Update Dependency Baseline Tests

- [x] 11.1 Update `agent-core/tests/test_dependency_baseline.py`: change harness version from `"0.11.0"` to `"0.23.0"`, remove `DynamicWorkflow` import line (line 9) AND assertion (line 20)
- [x] 11.2 Update `agent-harness/tests/test_dependency_baseline.py`: change `"0.11.0"` → `"0.23.0"` in version tuple
- [x] 11.3 Update `agent-docs-sync/tests/test_dependency_baseline.py`: change `"0.11.0"` → `"0.23.0"` in version tuple
- [x] 11.4 Re-run dependency baseline tests to verify they pass

## 12. Verify No Legacy Code Remains

- [x] 12.1 Run `grep -rn "GuardResult\|InputGuard\|OutputGuard" src/ tests/` in agent-docs-sync — should return 0 matches
- [x] 12.2 Run `grep -rn "from pydantic_ai_harness.guardrails import GuardResult" src/ tests/` in all repos — should return 0 matches
- [x] 12.3 Run `grep -rn "from pydantic_ai_harness.guardrails import InputGuard" src/ tests/` in all repos — should return 0 matches
- [x] 12.4 Run `grep -rn "from pydantic_ai_harness.guardrails import OutputGuard" src/ tests/` in all repos — should return 0 matches
- [x] 12.5 Run `grep -rn "GuardResult\|InputGuard\|OutputGuard" docs/` in all repos — should return 0 matches
- [x] 12.6 Run `grep -rn "pydantic-ai-harness==0.11.0" docs/` in all repos — should return 0 matches
- [x] 12.7 Run `grep -rn "InputGuard\|OutputGuard" openspec/specs/` — should return 0 matches
- [x] 12.8 Run `grep -rn "pydantic_ai_harness.context" src/ tests/` in all repos — should return 0 matches (use repo_context)
- [x] 12.9 Run `grep -rn "pydantic_ai_harness.cache_stability" src/ tests/` in all repos — should return 0 matches (use warn_on_cache_busts)

## 13. Fix Any Issues

- [x] 13.1 Fix any type errors from harness version upgrade (if any)
- [x] 13.2 Fix any test failures from harness version upgrade (if any)
- [x] 13.3 Fix any ruff/mypy findings introduced by version changes
- [x] 13.4 Re-run full verification suite until all gates pass

## 14. Commit and Archive

- [ ] 14.1 Commit agent-core changes: `git add -A && git commit`
- [ ] 14.2 Commit agent-harness changes: `git add pyproject.toml uv.lock tests/test_dependency_baseline.py && git commit`
- [ ] 14.3 Commit agent-docs-sync changes: `git add -A && git commit` (includes guardrails migration + docs)
- [ ] 14.4 Commit openspec-store changes: `git add -A && git commit` (specs + archive)
- [ ] 14.5 Archive the OpenSpec change: `openspec archive upgrade-pydantic-ai-harness --yes`
- [ ] 14.6 Commit openspec-store archive: `git add -A && git commit`
- [ ] 14.7 Run `openspec validate --all --strict` to confirm no regressions

## 15. Verify Rollback Works

- [ ] 15.1 In agent-core: `git stash && git checkout main -- pyproject.toml uv.lock && uv sync && uv run pytest -q && git stash pop`
- [ ] 15.2 Verify rollback restores previous harness version and all tests pass
