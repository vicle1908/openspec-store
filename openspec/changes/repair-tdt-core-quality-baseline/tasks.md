## 1. Baseline Recapture & Isolated Worktree Setup

- [ ] 1.1 Verify target repository state at accepted commit `e349009db28e73c70624071110a05a708998c454` in `/Users/androidteam/orca/workspaces/tdt-core/tdt-main` and confirm initial gate diagnostics match audit evidence
- [ ] 1.2 Provision an isolated top-level git worktree branching from `e349009db28e73c70624071110a05a708998c454` and verify the isolated worktree environment

## 2. Ruff Lint & Import Formatting Remediation (Tiers 1 & 2)

- [ ] 2.1 Apply automated import sorting across all test files using `uv run ruff check . --fix` and format with `uv run ruff format .`, verifying 18 `I001` violations are eliminated
- [ ] 2.2 Remediate `TC003` in `src/tdt_core/scheduler/health.py` by placing `Callable` under `if TYPE_CHECKING:` with `from __future__ import annotations`, verifying `uv run ruff check .` exits 0 with 0 errors

## 3. Strict Mypy Typing Remediation (Tiers 3 & 4)

- [ ] 3.1 Remediate `attr-defined`, index, and assignment errors in `tests/scheduler/test_cli.py` with typed fixtures and explicit module exports, verifying `uv run mypy tests/scheduler/test_cli.py --strict` exits 0
- [ ] 3.2 Remediate typing in `tests/scheduler/test_health.py` by adding explicit return/parameter annotations to `_mock_get_client_and_destroy` and mock helpers, verifying `uv run mypy tests/scheduler/test_health.py --strict` exits 0
- [ ] 3.3 Remediate typing issues in `tests/scheduler/test_serve_health_listener.py`, `tests/scheduler/test_engine.py`, `tests/scheduler/test_scheduling.py`, and `tests/scheduler/test_settings.py`, verifying each passes `--strict`
- [ ] 3.4 Remediate generator types in `tests/scheduler/test_registry_loader.py` and clean stale `unused-ignore` directives in `tests/scheduler/test_schedule_manifest.py`, verifying all scheduler test files pass `--strict`
- [ ] 3.5 Remediate any remaining strict mypy diagnostics across `src/` modules without altering public API signatures or introducing blanket `# type: ignore` suppressions, verifying `uv run mypy src tests/scheduler --strict` exits 0

## 4. Comprehensive Quality Gate & Regression Verification

- [ ] 4.1 Execute focused scheduler test suite `uv run pytest -q tests/scheduler` and verify all 76+ tests pass with zero failures or errors
- [ ] 4.2 Verify lockfile consistency via `uv lock --check` and clean diff formatting via `git diff --check HEAD`
- [ ] 4.3 Review modified files against expected blast radius (`git status` and `git diff --stat`), ensuring no unrelated generated files or untracked state are modified

## 5. Integration, Worktree Cleanup & Rollback Recording

- [ ] 5.1 Record rollback baseline SHA (`e349009db28e73c70624071110a05a708998c454`) and patch evidence prior to integration
- [ ] 5.2 Merge worktree branch cleanly into target main branch, remove isolated worktree, and verify working tree is clean
