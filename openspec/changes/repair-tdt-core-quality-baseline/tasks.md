## 1. Baseline Recapture & Isolated Worktree Setup

- [x] 1.1 Verify target repository state at accepted commit `e349009db28e73c70624071110a05a708998c454` in `/Users/androidteam/orca/workspaces/tdt-core/tdt-main` and confirm initial gate diagnostics match audit evidence
- [x] 1.2 Provision an isolated top-level git worktree branching from `e349009db28e73c70624071110a05a708998c454` and verify the isolated worktree environment

## 2. Ruff Lint & Import Formatting Remediation (Tiers 1 & 2)

- [x] 2.1 Apply automated import sorting across all test files using `uv run ruff check . --fix`, format with `uv run ruff format .`, and verify with `uv run ruff format --check .` plus a diff-scope review (`git diff --stat`) ensuring 18 `I001` violations are eliminated without unexpected file modifications
- [x] 2.2 Remediate `TC003` in `src/tdt_core/scheduler/health.py` by placing `Callable` under `if TYPE_CHECKING:` with `from __future__ import annotations`, verifying `uv run ruff check .` exits 0 with 0 errors

## 3. Strict Mypy Typing Remediation (Tiers 3 & 4)

- [x] 3.1 Remediate typing in `tests/scheduler/test_cli.py` using typed fixtures, concrete casts, and string monkeypatch targets without adding private helpers to public `__all__`, changing public exports, using file-wide ignores, or introducing bulk per-line `attr-defined` suppressions (allowing only isolated, evidence-justified narrow suppressions for genuine third-party or method-assignment typing limitations), verifying `uv run mypy tests/scheduler/test_cli.py --strict` exits 0
- [x] 3.2 Remediate typing in `tests/scheduler/test_health.py` by adding explicit return and parameter annotations to `_mock_get_client_and_destroy` and mock helpers, verifying `uv run mypy tests/scheduler/test_health.py --strict` exits 0
- [x] 3.3 Remediate typing issues in `tests/scheduler/test_serve_health_listener.py`, `tests/scheduler/test_engine.py`, `tests/scheduler/test_scheduling.py`, and `tests/scheduler/test_settings.py`, verifying with per-file strict-mypy checkpoints (`uv run mypy tests/scheduler/test_serve_health_listener.py --strict`, `uv run mypy tests/scheduler/test_engine.py --strict`, `uv run mypy tests/scheduler/test_scheduling.py --strict`, and `uv run mypy tests/scheduler/test_settings.py --strict`)
- [x] 3.4 Remediate typing in `tests/scheduler/test_registry_loader.py` and `tests/scheduler/test_schedule_manifest.py`: require exact diagnosis via `uv run mypy tests/scheduler/test_registry_loader.py --strict` before any generator annotation change and preserve code if the audit claim is stale; clean stale `unused-ignore` directives in `tests/scheduler/test_schedule_manifest.py`, verifying with per-file strict-mypy checkpoints (`uv run mypy tests/scheduler/test_registry_loader.py --strict` and `uv run mypy tests/scheduler/test_schedule_manifest.py --strict`)
- [x] 3.5 Remediate remaining strict mypy diagnostics across `src/` modules: begin with `uv run mypy src --strict` to identify and name exact `src/` files before making edits, and resolve issues without altering public API signatures or introducing blanket/bulk suppressions, verifying `uv run mypy src tests/scheduler --strict` exits 0

## 4. Comprehensive Quality Gate & Regression Verification

- [x] 4.1 Execute focused scheduler test suite `uv run pytest -q tests/scheduler` and full test suite `uv run pytest -q` (validating that root test import formatting caused no regressions), verifying all tests pass with zero failures or errors
- [x] 4.2 Verify lockfile consistency via `uv lock --check` and clean diff formatting via `git diff --check HEAD`
- [x] 4.3 Review modified files against expected blast radius (`git status` and `git diff --stat`), ensuring no unrelated generated files or untracked state are modified

## 5. Integration, Worktree Cleanup & Rollback Recording

- [x] 5.1 Record rollback baseline SHA (`e349009db28e73c70624071110a05a708998c454`) and patch evidence prior to integration
- [x] 5.2 Merge worktree branch cleanly into target main branch, remove isolated worktree, and verify working tree is clean
