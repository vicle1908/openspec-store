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
- Achieve 0 Ruff violations across the entire codebase (`uv run ruff check .`).
- Achieve 0 mypy violations across `src` and `tests/scheduler` under `--strict` mode (`uv run mypy src tests/scheduler --strict`).
- Maintain 100% test pass rate across all 76+ scheduler tests (`uv run pytest -q tests/scheduler`).
- Implement typed, test-safe fixes without broad `# type: ignore` suppressions or distorting the public API surface of `tdt_core`.
- Maintain clean lockfile (`uv lock --check`) and clean whitespace (`git diff --check HEAD`).
- Execute all changes in an isolated top-level git worktree with verified clean merge and recorded rollback point.

**Non-Goals:**
- Altering scheduler scheduling algorithms, execution flow, or runtime behavior.
- Altering public API exports consumed by downstream services (`agent-core`, `agent-harness`, `agent-docs-sync`, `webhook-receiver`).
- Introducing broad `# noqa` or un-annotated `# type: ignore` bypasses.
- Modifying unrelated files or generated state in the workspace.

## Decisions

### Decision 1: Tiered Remediation Sequence
- **Rationale**: Progressing from mechanical linting (Tiers 1 & 2) to semantic test typing (Tiers 3 & 4) isolates formatting changes from type adjustments and provides clean intermediate validation checkpoints.
- **Alternatives Considered**: Modifying tests and formatting simultaneously. *Rejected* because combined diffs complicate regression debugging if a test fails.

### Decision 2: Typed & Test-Safe Fixes over Blanket Suppressions
- **Rationale**: Strict mypy errors in `tests/scheduler/test_cli.py` (mainly `attr-defined` and object index/assignment) will be resolved through explicit type annotations, properly typed fixtures/mocks, and explicit attribute access rather than sweeping `# type: ignore` directives or `cast(Any, ...)` bypasses.
- **Alternatives Considered**: Adding file-level `# type: ignore` to `test_cli.py`. *Rejected* as it violates the strict quality baseline mandate and masks legitimate interface regressions.

### Decision 3: Type-Checking Block for TC003 in `health.py`
- **Rationale**: Adding `from __future__ import annotations` and moving `from collections.abc import Callable` inside `if TYPE_CHECKING:` in `src/tdt_core/scheduler/health.py` satisfies Ruff rule `TC003` cleanly while avoiding runtime import overhead.
- **Alternatives Considered**: Inlining string type annotations without `TYPE_CHECKING` or disabling TC003 in `pyproject.toml`. *Rejected* because conforming to standard modern Python typing conventions maintains project consistency.

### Decision 4: Isolated Top-Level Git Worktree & Rollback Evidence
- **Rationale**: Performing work in an isolated worktree (`git worktree add ../tdt-repair-worktree e349009db28e73c70624071110a05a708998c454`) guarantees that the active workspace remains undisturbed, intermediate edits cannot corrupt unrelated state, and merge back to main occurs only after 100% gate verification. Rollback evidence (base commit SHA and patch) is recorded before merge.
- **Alternatives Considered**: In-place edits directly on `main`. *Rejected* due to risk of dirty workspace state during multi-step typing fixes.

## Risks / Trade-offs

- **[Risk]** Test mock typing adjustments in `test_health.py` or `test_cli.py` could alter mock behavior or return values.
  - **Mitigation**: Run focused pytest (`uv run pytest -q <test_file>`) immediately following each file edit, followed by full test suite execution.
- **[Risk]** Auto-formatting (`ruff format`) might touch files beyond the 19 identified Ruff error files.
  - **Mitigation**: Perform a scoped diff review (`git diff --stat`) to verify that changes are strictly confined to known violation sites.
- **[Risk]** Downstream API surface accidental modification during `src/` typing fixes.
  - **Mitigation**: Enforce that changes in `src/` are restricted to `src/tdt_core/scheduler/health.py` (and any minimal strict-mypy type signatures), leaving public method signatures and module exports unchanged.

## Migration & Rollback Strategy

1. **Pre-Implementation**: Verify baseline commit `e349009db28e73c70624071110a05a708998c454` and record initial gate outputs.
2. **Worktree Setup**: Provision `../tdt-repair-worktree` branching from `e349009db28e73c70624071110a05a708998c454`.
3. **Execution**: Apply Ruff fixes (Tiers 1-2) -> Strict mypy fixes (Tiers 3-4) -> Full gate validation.
4. **Integration**: Merge worktree branch cleanly into target main branch and remove worktree.
5. **Rollback**: If any regression or downstream incompatibility is observed, revert the merge commit or reset to `e349009db28e73c70624071110a05a708998c454`.
