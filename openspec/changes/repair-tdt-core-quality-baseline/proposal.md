## Why

The `tdt-core` codebase at accepted commit `e349009db28e73c70624071110a05a708998c454` has pre-existing quality gate failures that prevent strict automated CI gating and block downstream developer verification. According to `/tmp/tdt-core-quality-audit.md`, the repository has 19 Ruff errors (18 `I001` un-sorted imports across test files and 1 `TC003` stdlib type import in `src/tdt_core/scheduler/health.py`) and approximately 52 strict-mypy errors concentrated across `tests/scheduler` and related modules. Remediation is required now to restore full CI quality gate compliance without altering runtime behavior or public API contracts.

### Non-Goals
- Modifying `tdt-core` public functional behavior, scheduler semantics, or runtime execution logic.
- Altering public APIs or contracts consumed by downstream repositories (`agent-core`, `agent-harness`, `agent-docs-sync`, `webhook-receiver`).
- Introducing broad typing suppressions (such as unscoped `# type: ignore` or replacing typed interfaces with `Any`).
- Introducing delta specs or modifying main OpenSpec capabilities (`skip_specs: true` is set for this quality baseline remediation).
- Modifying unrelated changes or store records (e.g., `align-jti-skill-runtime-contract`).

## What Changes

- **Baseline Recapture & Verification**: Re-verify baseline gate diagnostics on an isolated worktree branch rooted at `e349009db28e73c70624071110a05a708998c454`.
- **Ruff Lint & Import Remediation (Tier 1 & Tier 2)**:
  - Auto-fix all 18 `I001` un-sorted/un-formatted import violations across test files via `uv run ruff check . --fix` and format with `uv run ruff format .`.
  - Fix `TC003` in `src/tdt_core/scheduler/health.py` by placing `from collections.abc import Callable` inside an `if TYPE_CHECKING:` block with `from __future__ import annotations`.
- **Strict Mypy Type Remediation (Tier 3 & Tier 4)**:
  - Fix ~33 `attr-defined` and argument/indexing errors in `tests/scheduler/test_cli.py` via typed exports and explicit test typing without public API distortion.
  - Fix untyped helper functions and call mismatches in `tests/scheduler/test_health.py` (`no-untyped-def`, `no-untyped-call`).
  - Fix remaining strict mypy errors in `tests/scheduler/test_serve_health_listener.py`, `tests/scheduler/test_engine.py`, `tests/scheduler/test_scheduling.py`, `tests/scheduler/test_registry_loader.py`, `tests/scheduler/test_schedule_manifest.py`, `tests/scheduler/test_settings.py`, and any `src/` modules.
  - Remove stale `# type: ignore` directives (`unused-ignore`).
- **Comprehensive Quality Gate Verification**:
  - `uv run ruff check .` -> exit 0 (0 errors).
  - `uv run mypy src tests/scheduler --strict` -> exit 0 (0 errors).
  - `uv run pytest -q tests/scheduler` -> exit 0 (all 76+ tests pass).
  - `uv lock --check` -> exit 0 (lockfile clean).
  - `git diff --check HEAD` -> exit 0 (whitespace clean).
- **Worktree Lifecycle & Clean Integration**:
  - Perform all work in an isolated top-level git worktree.
  - Verify changed file scope and preserve unrelated generated state.
  - Clean merge into target main with rollback evidence recorded.

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
