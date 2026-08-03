## 1. P1 — Fix Secret Scanning Test Failures

- [x] 1.1 Pre-scan: run `gitleaks detect --source . --log-opts="--all"` in each repo to identify any findings. For any deterministic false positives (e.g., metadata files), add exact-fingerprint entries to `.gitleaksignore` per the quality-gate exception policy.
  - Verify: `gitleaks detect --source . --log-opts="--all" --no-banner` returns 0 findings in each repo
- [x] 1.2 Create `.github/workflows/ci.yml` in agent-core with Docker-based gitleaks step matching test assertions (`docker://ghcr.io/gitleaks/gitleaks:v8.30.1`, `fetch-depth: 0`, `git --redact=100 --no-banner --verbose .`)
  - Verify: `uv run pytest tests/test_secret_scanning_policy.py -v` passes (1 test was failing)
  - Verify: `actionlint .github/workflows/ci.yml` exits 0
- [x] 1.3 Create `.github/workflows/ci.yml` in agent-docs-sync (same workflow)
  - Verify: `uv run pytest tests/test_secret_scanning_policy.py -v` passes (2 tests were failing — both `test_ci_scans_full_history_with_redaction` and `test_rollback_allows_only_a_synthetic_exact_fingerprint`)
  - Verify: `actionlint .github/workflows/ci.yml` exits 0
- [x] 1.4 Create `.github/workflows/ci.yml` in agent-harness (same workflow)
  - Verify: `uv run pytest tests/test_secret_scanning_policy.py -v` passes (1 test was failing)
  - Verify: `actionlint .github/workflows/ci.yml` exits 0

## 2. P1 — Fix Harness lifecycle_auth Docstring

- [x] 2.1 Update `agent_harness/lifecycle_auth.py` module docstring: remove "not wired into the public runner yet", replace with description reflecting actual wiring into `workflow/runner.py`, `workflow/graph.py`, and `cli.py`
  - Verify: `grep -n 'not wired' src/agent_harness/lifecycle_auth.py` returns 0 matches
  - Verify: `uv run pytest tests/ -q` — all existing tests still pass

## 3. P2 — Expand llm_gateway Tests

- [x] 3.1 Add BifrostGateway tests: `get_model()` returns valid model, `from_env()` reads env vars, error on missing BIFROST_URL
  - Verify: `uv run pytest tests/llm_gateway/ -v` includes new BifrostGateway tests
- [x] 3.2 Add ResilientGateway tests — use forced breaker state via `record_failure()` (NOT `_breaker._state` mutation which doesn't work because `_opened_at` stays 0):
  - `get_model()` delegates to inner gateway (mock inner, verify delegation)
  - `is_available()` returns True when breaker is closed AND inner reports available
  - `is_available()` returns False when inner reports unavailable (breaker still closed)
  - **Fallback test**: create ResilientGateway with `inner` (mock, always unavailable) + `fallbacks=[mock_fallback]`. Call `_breaker.record_failure()` 5 times to force breaker open. Then verify `is_available()` checks `fallbacks[0]`.
  - **Note**: the wrapper only checks `fallbacks[0]`, NOT the `FallbackChain`. The chain is constructed but never executed.
  - Verify: `uv run pytest tests/llm_gateway/ -v` includes new ResilientGateway tests
- [x] 3.3 Add factory edge cases: missing config fields
  - Note: unknown provider is already tested in `test_factory.py::test_factory_create_unknown_provider`
  - Verify: `uv run pytest tests/llm_gateway/ -v` passes all
- [x] 3.4 Verify coverage improved: `uv run pytest tests/llm_gateway/ --cov=src/agent_core/llm_gateway --cov-fail-under=80 --cov-report=term-missing`

## 4. P2 — Expand foundation Tests

- [x] 4.1 Add migration error path tests: connection failure handling, pool cleanup on exception in `run_migrations()`
  - Verify: `uv run pytest tests/foundation/test_migrations.py -v` includes new error tests
- [x] 4.2 Add tracing tests: OTel span creation, context propagation (currently 33% covered)
  - Verify: `uv run pytest tests/foundation/test_tracing.py -v` includes new tests
- [x] 4.3 Add foundation edge cases: settings validation errors, workspace resolution
  - Verify: `uv run pytest tests/foundation/ -v` passes all
- [x] 4.4 Verify coverage improved: `uv run pytest tests/foundation/ --cov=src/agent_core/foundation --cov-fail-under=80 --cov-report=term-missing`

## 5. P3 — Expand cli Edge-Case Tests

Note: Basic review/propose/explore command tests already exist (verified). This task adds edge-case coverage only.

- [x] 5.1 Add review error cases: agent failure (mock `_run_agent_prompt` to raise), gateway error propagation
  - Note: nonexistent paths are NOT errors — `_build_prompt_for_review()` treats them as generic URL/MR/path targets
  - Verify: `uv run pytest tests/cli/test_cli.py -v` includes new error-case tests
- [x] 5.2 Add propose/explore edge cases: empty input, malformed args
  - Verify: `uv run pytest tests/cli/test_cli.py -v` includes new edge-case tests
- [x] 5.3 Verify coverage improved: `uv run pytest tests/cli/ --cov=src/agent_core/cli --cov-fail-under=80 --cov-report=term-missing`

## 6. P3 — Reduce docs-sync SDK Coupling

- [x] 6.1 Add 7 re-exports to `agent_core.sdk.__init__.py`: Settings, AuthenticatedSubject, ConfigFileResolver, IdentityStatus, SignedSubjectAssertion, SubjectResolutionRequest, SubjectResolutionResult
  - Verify: `python -c "from agent_core.sdk import Settings, AuthenticatedSubject, ConfigFileResolver, IdentityStatus, SignedSubjectAssertion, SubjectResolutionRequest, SubjectResolutionResult; print('ok')"` succeeds
  - Verify: all symbols resolve to the same classes as their internal originals
  - Verify: all 7 appear in `agent_core.sdk.__all__`
- [x] 6.2 Update docs-sync imports to use SDK facade only (grep-based quick check)
  - Verify: `grep -rn 'from agent_core.agent_base\|from agent_core.foundation\|from agent_core.lifecycle_identity' src/ --include='*.py'` returns 0 matches
- [x] 6.3 Add persistent AST-based import boundary test to agent-docs-sync tests (catches bare imports, aliases, and future internal modules that grep misses)
  - Verify: `uv run pytest tests/test_sdk_boundary.py -v` passes
- [x] 6.4 Bump agent-docs-sync dependency floor: change `agent-core>=0.1.0` to `agent-core>=0.2.0` in `pyproject.toml` and run `uv lock` to update lockfile
  - Verify: `uv run python -c "import agent_core; print(agent_core.__version__)"` prints `0.2.0`
- [x] 6.5 Run full test suite across agent-core and agent-docs-sync
  - Verify: all tests pass, ruff clean

## 7. Final Validation

- [x] 7.1 Run `uv run ruff check src/ tests/` in all 3 repos — 0 violations
- [x] 7.2 Run `uv run mypy src/agent_core/ --strict` in agent-core — 0 errors
- [x] 7.3 Run `uv run mypy src/agent_docs_sync/ --strict` in agent-docs-sync — 0 errors (import changes must be type-clean)
- [x] 7.4 Run `uv run pytest tests/ -q` in all 3 repos — all pass
- [x] 7.5 Run `openspec validate --strict --all` — all pass
- [x] 7.6 Update SPEC_INDEX.md test metrics in affected repos
- [x] 7.7 Commit all changes with descriptive messages
