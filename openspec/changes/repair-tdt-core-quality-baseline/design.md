## Context

See `proposal.md` for background and problem motivation.

The remediation target is `/Users/androidteam/orca/workspaces/tdt-core/tdt-main` at base commit `e349009db28e73c70624071110a05a708998c454`. Current audit evidence (`/tmp/tdt-core-quality-audit.md`) identifies:
- **Ruff**: 19 violations (18 `I001` import-sorting errors across test files, 1 `TC003` stdlib type-checking import in `src/tdt_core/scheduler/health.py`).
- **mypy --strict**: ~52 errors across 13 files (predominantly `attr-defined` in `tests/scheduler/test_cli.py`, `no-untyped-def` / `no-untyped-call` in `test_health.py`, generator return types in `test_registry_loader.py`, and stale `unused-ignore` directives).
- **pytest**: 76 tests in `tests/scheduler` currently passing.
- **uv lock & git diff**: Currently clean.

## Goals / Non-Goals

**Goals:**
- Recapture baseline diagnostics prior to code edits to confirm exact error signatures.
- Achieve 0 Ruff violations across the entire codebase (`uv run ruff check .` and `uv run ruff format --check .`).
- Achieve 0 mypy violations across `src` and `tests/scheduler` under `--strict` mode (`uv run mypy src tests/scheduler --strict`), validated via per-file strict-mypy checkpoints on all affected scheduler test files.
- Maintain 100% test pass rate across both focused scheduler tests (`uv run pytest -q tests/scheduler`) and full test suite (`uv run pytest -q`).
- Implement typed, test-safe fixes without file-wide ignores or bulk per-line `attr-defined` suppressions, and without distorting the public API surface or `__all__` exports of `tdt_core`.
- Maintain clean lockfile (`uv lock --check`) and clean whitespace (`git diff --check HEAD`).
- Execute all changes in an isolated top-level git worktree with verified clean merge and recorded rollback point (`e349009db28e73c70624071110a05a708998c454`).

**Non-Goals:**
- Altering scheduler scheduling algorithms, execution flow, or runtime behavior.
- Altering public API exports or adding private helpers to `__all__` in `src/tdt_core/` to satisfy test typing.
- Introducing file-wide `# type: ignore` directives or bulk per-line `attr-defined` suppressions.
- Modifying unrelated files or generated state in the workspace.

## Decisions

### Decision 1: Tiered Remediation Sequence
- **Rationale**: Progressing from mechanical linting (Tiers 1 & 2) to semantic test typing (Tiers 3 & 4) isolates formatting changes from type adjustments and provides clean intermediate validation checkpoints:
  1. *Tier 1 & 2 (Ruff)*: Run `uv run ruff check . --fix`, `uv run ruff format .`, verify with `uv run ruff format --check .` and conduct diff-scope review (`git diff --stat`); fix `TC003` in `health.py`.
  2. *Tier 3 & 4 (Strict Mypy)*: Remediate test files with per-file strict-mypy checkpoints (groups 3.3 and 3.4). Require exact diagnosis via `uv run mypy tests/scheduler/test_registry_loader.py --strict` before any generator annotation edits (preserving code if the audit claim is stale). Begin `src/` remediation (Task 3.5) with `uv run mypy src --strict` and name exact `src/` files before editing.
  3. *Tier 5 (Quality Gate & Regression)*: Validate full gate, running both focused scheduler tests (`uv run pytest -q tests/scheduler`) and full `uv run pytest -q` across the entire codebase to catch any import-formatting regressions in root test files.
- **Alternatives Considered**: Modifying tests and formatting simultaneously. *Rejected* because combined diffs complicate regression debugging if a test fails.

### Decision 2: Typed & Test-Safe Fixes over Blanket Suppressions
- **Rationale**: File-wide ignores and bulk per-line `attr-defined` suppressions are explicitly prohibited. Instead, the implementation prioritizes:
  - Typed helpers and explicit parameter/return type annotations.
  - Protocols and concrete type casts where dynamic interfaces are mocked.
  - Direct imports where symbols are available.
  - String monkeypatch targets (e.g. `monkeypatch.setattr(cli, "_settings", ...)` or `monkeypatch.setattr("tdt_core.cli._settings", ...)`) and typed fixtures rather than polluting public `__all__` with private module internals in `test_cli.py`.
  - Isolated, evidence-justified narrow suppressions strictly reserved for genuine third-party or method-assignment typing limitations (e.g. dynamic database engine connection assignment `# type: ignore[method-assign]`).
  - Task 3.1 must never add private helpers to public `__all__` or modify public exports.
- **Alternatives Considered**: Adding private helpers to `cli.py`'s `__all__` or adding file-level `# type: ignore` to `test_cli.py`. *Rejected* because adding private symbols to `__all__` leaks internal implementation details into the public API surface, and file-wide ignores violate the strict quality baseline mandate.

### Decision 3: Type-Checking Block for TC003 in `health.py`
- **Rationale**: Adding `from __future__ import annotations` and moving `from collections.abc import Callable` inside `if TYPE_CHECKING:` in `src/tdt_core/scheduler/health.py` satisfies Ruff rule `TC003` cleanly while avoiding runtime import overhead.
- **Alternatives Considered**: Inlining string type annotations without `TYPE_CHECKING` or disabling TC003 in `pyproject.toml`. *Rejected* because conforming to standard modern Python typing conventions maintains project consistency.

### Decision 4: Isolated Top-Level Git Worktree & Rollback Evidence
- **Rationale**: Performing work in an isolated worktree (`git worktree add ../tdt-repair-worktree e349009db28e73c70624071110a05a708998c454`) guarantees that the active workspace remains undisturbed, intermediate edits cannot corrupt unrelated state, and merge back to main occurs only after 100% gate verification. Rollback evidence (base commit SHA `e349009db28e73c70624071110a05a708998c454` and patch) is recorded before merge.
- **Alternatives Considered**: In-place edits directly on `main`. *Rejected* due to risk of dirty workspace state during multi-step typing fixes.

## Risks / Trade-offs

- **[Risk]** Test mock typing adjustments in `test_health.py` or `test_cli.py` could alter mock behavior or return values.
  - **Mitigation**: Run focused pytest (`uv run pytest -q <test_file>`) immediately following each file edit, followed by full test suite execution (`uv run pytest -q`).
- **[Risk]** Auto-formatting (`ruff format`) might touch files beyond the 19 identified Ruff error files.
  - **Mitigation**: Perform a scoped diff review (`git diff --stat`) and run `uv run ruff format --check .` to verify that changes are strictly confined to expected files.
- **[Risk]** Stale or inaccurate audit findings (e.g. generator return claim in `test_registry_loader.py` or unused ignore in `test_engine.py`).
  - **Mitigation**: Require exact diagnosis via `uv run mypy tests/scheduler/test_registry_loader.py --strict` prior to editing, and preserve existing code if the audit claim is stale.
- **[Risk]** Unidentified `src/` type errors causing unexpected scope expansion in Task 3.5.
  - **Mitigation**: Make Task 3.5 begin with `uv run mypy src --strict` and explicitly name all identified `src/` files before making any edits.
- **[Risk]** Downstream API surface accidental modification during `src/` typing fixes or `test_cli.py` helper exposure.
  - **Mitigation**: Enforce that changes in `src/` are restricted to `src/tdt_core/scheduler/health.py` (and minimal strict-mypy annotations in named `src/` files), leaving public method signatures, `__all__`, and module exports unchanged.

## Migration & Rollback Strategy

1. **Pre-Implementation**: Verify baseline commit `e349009db28e73c70624071110a05a708998c454` and record initial gate outputs.
2. **Worktree Setup**: Provision `../tdt-repair-worktree` branching from `e349009db28e73c70624071110a05a708998c454`.
3. **Execution**: Apply Ruff fixes (Tiers 1-2 with `ruff format --check .` and diff review) -> Strict mypy fixes (Tiers 3-4 with per-file checkpoints for 3.3/3.4, exact diagnosis for generator types, and naming exact `src/` files in 3.5) -> Full gate validation (running both scheduler pytest and full `uv run pytest -q`).
4. **Integration**: Merge worktree branch cleanly into target main branch and remove worktree.
5. **Rollback**: If any regression or downstream incompatibility is observed, revert the merge commit or reset to `e349009db28e73c70624071110a05a708998c454`.
