## 1. Freeze Integration and Repository Ownership

- [ ] 1.1 From `/Users/androidteam/Developer`, publish the integration coordinator and the planning source `/Users/androidteam/Developer/.worktrees/pydantic-ai-openspec-followups` at its current reviewed HEAD; verify that HEAD contains this three-change DAG and the planning worktree is clean before reading apply instructions.
- [ ] 1.2 Publish one writer packet for agent-core, agent-harness, agent-docs-sync, and openspec-store with branch, 40-character base SHA, raw dirty inventory, content-diff hash, selected paths, and preserved unrelated paths; verify no selected path has overlapping ownership.
- [ ] 1.3 Create dedicated repository worktrees from the accepted bases using change-specific branches and verify `git status --porcelain=v2 --untracked-files=all` is clean before any edit.
- [ ] 1.4 Create `openspec/changes/restore-agent-pydantic-quality-gates/EVIDENCE_MANIFEST.md` with frozen RED commands/results for full Ruff and strict mypy; recapture current counts, compare them with the planning-time `32` harness/`28` docs-sync I001 findings and `AssuranceLevel` error, and verify the ledger labels planning-time counts as historical rather than execution truth.

## 2. Restore the Public SDK Type Boundary

- [ ] 2.1 Add `AssuranceLevel` to the existing `agent_core.sdk` explicit export surface, including `__all__`, and verify runtime `hasattr`, `__all__` membership, and strict-mypy import resolution from the harness worktree.
- [ ] 2.2 Verify agent-harness imports the lifecycle type only through the accepted public surface and that `uv run mypy src/ --strict` passes with `agent_core.__file__` and `agent_core.sdk.__file__` bound to the accepted agent-core worktree.

## 3. Repair Mechanical Ruff Debt

- [ ] 3.1 Apply Ruff import-order fixes only to the recaptured agent-harness I001 paths and verify `git diff --word-diff=porcelain` contains no semantic test changes.
- [ ] 3.2 Apply Ruff import-order fixes only to the recaptured agent-docs-sync I001 paths and verify `git diff --word-diff=porcelain` contains no semantic test changes.
- [ ] 3.3 Re-run `uv run ruff check .`, `uv run ruff check . --select I001`, and `uv run ruff format --check .` in both repositories with disposable caches and verify all commands exit `0`.

## 4. Verify Repository Results

- [ ] 4.1 Run agent-core full Ruff, strict mypy, and pytest from its accepted worktree and record exact pass/skip counts, warnings, exit codes, and import origins in the evidence manifest.
- [ ] 4.2 Run agent-harness full Ruff, strict mypy, and pytest from its accepted worktree and record exact pass/skip counts, warnings, exit codes, and import origins in the evidence manifest.
- [ ] 4.3 Run agent-docs-sync full Ruff, strict mypy, and pytest from its accepted worktree and record exact pass/skip counts, warnings, exit codes, and import origins in the evidence manifest.
- [ ] 4.4 Recompute every repository HEAD, raw dirty inventory, content-diff hash, and imported dependency path after gates; verify evidence and source identities still match before checking any completion task.

## 5. Rehearse Rollback and Commit One Owner at a Time

- [ ] 5.1 Rehearse agent-core Git-revert rollback in a disposable worktree, rerun the focused SDK export tests and strict mypy, and record exit codes without mutating the default checkout.
- [ ] 5.2 Rehearse agent-harness Git-revert rollback in a disposable worktree, rerun focused Ruff/mypy/tests, and record exit codes without mutating the default checkout.
- [ ] 5.3 Rehearse agent-docs-sync Git-revert rollback in a disposable worktree, rerun focused Ruff/tests, and record exit codes without mutating the default checkout.
- [ ] 5.4 Review and commit the scoped agent-core diff, record its full result SHA, and verify only the SDK export path plus owned tests changed.
- [ ] 5.5 Review and commit the scoped agent-harness diff, record its full result SHA, and verify only recaptured mechanical import-order paths changed.
- [ ] 5.6 Review and commit the scoped agent-docs-sync diff, record its full result SHA, and verify only recaptured mechanical import-order paths changed.
- [ ] 5.7 Update and commit the openspec-store evidence manifest with all three accepted result SHAs, then verify the capability-contract change remains unimplemented and every default dirty path is preserved.
