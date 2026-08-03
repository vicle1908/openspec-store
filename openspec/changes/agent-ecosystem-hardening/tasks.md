## 1. P1 — Fix Secret Scanning Test Failures

- [ ] 1.1 Create `.github/workflows/ci.yml` in agent-core with gitleaks config matching test assertions
  - Verify: `uv run pytest tests/test_secret_scanning_policy.py -v` passes
- [ ] 1.2 Create `.github/workflows/ci.yml` in agent-docs-sync (same workflow)
  - Verify: `uv run pytest tests/test_secret_scanning_policy.py -v` passes
- [ ] 1.3 Create `.github/workflows/ci.yml` in agent-harness (same workflow)
  - Verify: `uv run pytest tests/test_secret_scanning_policy.py -v` passes

## 2. P1 — Fix Harness lifecycle_auth Docstring

- [ ] 2.1 Update `agent_harness/lifecycle_auth.py` docstring to reflect actual wiring state
  - Verify: `grep -n 'not wired' src/agent_harness/lifecycle_auth.py` returns 0 matches

## 3. P2 — Expand llm_gateway Tests

- [ ] 3.1 Add BifrostGateway tests: message routing, API key validation, error handling
  - Verify: `uv run pytest tests/llm_gateway/ -v` includes new BifrostGateway tests
- [ ] 3.2 Add ResilientGateway tests: retry on failure, circuit breaker open/close, timeout
  - Verify: `uv run pytest tests/llm_gateway/ -v` includes new ResilientGateway tests
- [ ] 3.3 Add create_gateway edge cases: invalid provider, missing config fields
  - Verify: `uv run pytest tests/llm_gateway/ -v` passes all
- [ ] 3.4 Verify ratio improved: `wc -l` comparison, target ≥0.50

## 4. P2 — Expand foundation Tests

- [ ] 4.1 Add migrations_eval tests: eval migration paths, error handling
  - Verify: `uv run pytest tests/foundation/test_migrations.py -v` includes eval tests
- [ ] 4.2 Add migrations_vector tests: vector migration paths, schema validation
  - Verify: `uv run pytest tests/foundation/test_migrations.py -v` includes vector tests
- [ ] 4.3 Add foundation edge cases: settings validation, workspace resolution errors
  - Verify: `uv run pytest tests/foundation/ -v` passes all
- [ ] 4.4 Verify ratio improved: target ≥0.50

## 5. P3 — Expand cli Tests

- [ ] 5.1 Add review command tests: file review, URL review, mock agent
  - Verify: `uv run pytest tests/cli/test_cli.py -v` includes review tests
- [ ] 5.2 Add propose command tests: change proposal, mock agent
  - Verify: `uv run pytest tests/cli/test_cli.py -v` includes propose tests
- [ ] 5.3 Add explore command tests: codebase exploration, mock agent
  - Verify: `uv run pytest tests/cli/test_cli.py -v` passes all

## 6. P3 — Reduce docs-sync SDK Coupling

- [ ] 6.1 Add `Settings` re-export to `agent_core.sdk.__init__.py`
  - Verify: `python -c "from agent_core.sdk import Settings; print('ok')"` succeeds
- [ ] 6.2 Add `SubjectResolutionRequest`, `SubjectResolutionResult` re-exports to SDK
  - Verify: `python -c "from agent_core.sdk import SubjectResolutionRequest; print('ok')"` succeeds
- [ ] 6.3 Update docs-sync imports to use SDK facade only
  - Verify: `grep -rn 'from agent_core.agent_base\|from agent_core.foundation\|from agent_core.lifecycle_identity' src/ --include='*.py'` returns 0 matches
- [ ] 6.4 Run full test suite across agent-core and agent-docs-sync
  - Verify: all tests pass, ruff clean

## 7. Final Validation

- [ ] 7.1 Run `uv run ruff check src/` in all 3 repos — 0 violations
- [ ] 7.2 Run `uv run pytest tests/` in all 3 repos — all pass
- [ ] 7.3 Run `openspec validate --strict --all` — 350+ pass
- [ ] 7.4 Update SPEC_INDEX.md test metrics in affected repos
- [ ] 7.5 Commit all changes with descriptive messages
