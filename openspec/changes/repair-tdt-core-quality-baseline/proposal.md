## Why

The `tdt-core` codebase at accepted commit `e349009db28e73c70624071110a05a708998c454` has pre-existing quality gate failures that prevent strict automated CI gating and block downstream developer verification. According to `/tmp/tdt-core-quality-audit.md`, the repository has 19 Ruff errors (18 `I001` un-sorted imports across test files and 1 `TC003` stdlib type import in `src/tdt_core/scheduler/health.py`) and approximately 52 strict-mypy errors concentrated across `tests/scheduler` and related modules. Remediation is required now to restore full CI quality gate compliance without altering runtime behavior or public API contracts.

### Non-Goals
- Modifying `tdt-core` public functional behavior, scheduler semantics, or runtime execution logic.
- Altering public APIs or contracts consumed by downstream repositories (`agent-core`, `agent-harness`, `agent-docs-sync`, `webhook-receiver`).
- Adding private helpers to public `__all__` or modifying public API exports to satisfy test typing.
- Introducing file-wide ignores (`# type: ignore`) or bulk per-line `attr-defined` suppressions; only isolated, evidence-justified narrow suppressions for genuine third-party or method-assignment typing limitations are allowed, with typed helpers, Protocols, direct imports, concrete casts, or string monkeypatch targets preferred.
- Introducing delta specs or modifying main OpenSpec capabilities (`skip_specs: true` is set for this quality baseline remediation).
- Modifying unrelated changes or store records (e.g., `align-jti-skill-runtime-contract`).

## What Changes

- **Baseline Recapture & Verification**: Re-verify baseline gate diagnostics on an isolated worktree branch rooted at `e349009db28e73c70624071110a05a708998c454`.
- **Ruff Lint & Import Remediation (Tier 1 & Tier 2)**:
  - Auto-fix all 18 `I001` un-sorted/un-formatted import violations across test files via `uv run ruff check . --fix`, format with `uv run ruff format .`, and verify with `uv run ruff format --check .` alongside a diff-scope review (`git diff --stat`) ensuring formatting changes do not touch unexpected files.
  - Fix `TC003` in `src/tdt_core/scheduler/health.py` by placing `from collections.abc import Callable` inside an `if TYPE_CHECKING:` block with `from __future__ import annotations`.
- **Strict Mypy Type Remediation (Tier 3 & Tier 4)**:
  - Fix `attr-defined`, index, and assignment errors in `tests/scheduler/test_cli.py` via typed fixtures, concrete casts, and string monkeypatch targets without adding private helpers to public `__all__` or altering public exports. Prohibit file-wide ignores and bulk per-line `attr-defined` suppressions, allowing only isolated, evidence-justified narrow suppressions for genuine third-party or method-assignment typing limitations.
  - Fix untyped helper functions and call mismatches in `tests/scheduler/test_health.py` (`no-untyped-def`, `no-untyped-call`) with explicit parameter and return annotations.
  - Fix remaining strict mypy errors in `tests/scheduler/test_serve_health_listener.py`, `tests/scheduler/test_engine.py`, `tests/scheduler/test_scheduling.py`, and `tests/scheduler/test_settings.py`, verifying each with per-file strict-mypy checkpoints.
  - Remediate typing in `tests/scheduler/test_registry_loader.py` and `tests/scheduler/test_schedule_manifest.py`: require exact diagnosis via `uv run mypy tests/scheduler/test_registry_loader.py --strict` before any generator annotation change and preserve code if the audit claim is stale; clean stale `unused-ignore` directives in `tests/scheduler/test_schedule_manifest.py`, verifying each with per-file strict-mypy checkpoints.
  - Remediate remaining strict mypy diagnostics across `src/` modules: begin by running `uv run mypy src --strict` to identify and name exact `src/` files before making edits, resolving issues without altering public API signatures or introducing blanket/bulk suppressions.
- **Comprehensive Quality Gate Verification**:
  - `uv run ruff check .` -> exit 0 (0 errors).
  - `uv run ruff format --check .` -> exit 0 (0 formatting issues).
  - Per-file strict mypy checkpoints for all scheduler test files -> exit 0.
  - `uv run mypy src tests/scheduler --strict` -> exit 0 (0 errors).
  - `uv run pytest -q tests/scheduler` and full `uv run pytest -q` -> exit 0 (all tests pass, validating that root test import formatting caused no regressions).
  - `uv lock --check` -> exit 0 (lockfile clean).
  - `git diff --check HEAD` -> exit 0 (whitespace clean).
- **Worktree Lifecycle & Clean Integration**:
  - Perform all work in an isolated top-level git worktree.
  - Verify changed file scope and preserve unrelated generated state.
  - Clean merge into target main with rollback evidence recorded (`e349009db28e73c70624071110a05a708998c454`).

## Capabilities

### New Capabilities
None (`skip_specs: true` declared; pure tooling and test quality repair).

### Modified Capabilities
None (`skip_specs: true` declared; no functional requirement changes).

## Impact

- **Target Repository**: `tdt-core` (`/Users/androidteam/orca/workspaces/tdt-core/tdt-main`).
- **Target Files**:
  - `src/tdt_core/scheduler/health.py` (`TC003` fix).
  - `tests/scheduler/test_cli.py`, `tests/scheduler/test_health.py`, `tests/scheduler/test_serve_health_listener.py`, `tests/scheduler/test_engine.py`, `tests/scheduler/test_scheduling.py`, `tests/scheduler/test_registry_loader.py`, `tests/scheduler/test_schedule_manifest.py`, `tests/scheduler/test_settings.py`.
  - 12 root test files for import formatting (`tests/test_canonical_agent_contract.py`, `tests/test_manifest_cli.py`, etc.).
- **Downstream Consumers**: Zero breaking changes; all public interfaces and runtime behavior remain identical.
- **CI / Developer Gating**: Restores strict Ruff and mypy gates to fully passing status.

## Ownership Boundaries

- **tdt-core Scheduler & Core Module**: Owner of scheduler implementation, typing, and test suites.
- **openspec-store**: Owner of specification and change tracking artifacts.
