## 1. Freeze Ownership and Baselines

- [ ] 1.1 Publish one writer per `/Users/androidteam/Developer/agent-core`, `/Users/androidteam/Developer/agent-harness`, `/Users/androidteam/Developer/agent-docs-sync`, and openspec-store worktree with branch, 40-character base SHA, raw dirty inventory, content-diff hash, and preserved unrelated paths; verify no selected path has overlapping ownership.
- [ ] 1.2 Create dedicated repository worktrees from the accepted bases and verify `git status --porcelain=v2 --untracked-files=all` is clean before any edit.
- [ ] 1.3 Create `openspec/changes/restore-agent-pydantic-quality-gates/EVIDENCE_MANIFEST.md` with frozen RED commands/results for full Ruff and strict mypy, including current `32` agent-harness I001 findings, `28` docs-sync I001 findings, and the agent-harness `AssuranceLevel` export error; verify the ledger separates current evidence from historical counts.

## 2. Restore the Public SDK Type Boundary

- [ ] 2.1 Add `AssuranceLevel` to the existing `agent_core.sdk` explicit export surface, including `__all__`, and verify runtime `hasattr`, `__all__` membership, and strict-mypy import resolution from the harness worktree.
- [ ] 2.2 Verify agent-harness imports the lifecycle type only through the accepted public surface and that `uv run mypy src/ --strict` passes with `agent_core.__file__` and `agent_core.sdk.__file__` bound to the accepted agent-core worktree.

## 3. Repair Mechanical Ruff Debt

- [ ] 3.1 Apply Ruff import-order fixes only to the classified agent-harness test paths and verify `git diff --word-diff=porcelain` contains no semantic test changes.
- [ ] 3.2 Apply Ruff import-order fixes only to the classified agent-docs-sync test paths and verify `git diff --word-diff=porcelain` contains no semantic test changes.
- [ ] 3.3 Re-run `uv run ruff check .`, `uv run ruff check . --select I001`, and `uv run ruff format --check .` in both repositories with disposable caches and verify all commands exit `0`.

## 4. Verify and Freeze the Prerequisite

- [ ] 4.1 Run agent-core full Ruff, strict mypy, and pytest from the accepted worktree and record exact pass/skip counts, warnings, exit codes, and import origins in the evidence manifest.
- [ ] 4.2 Run agent-harness full Ruff, strict mypy, and pytest from the accepted worktree and record exact pass/skip counts, warnings, exit codes, and import origins in the evidence manifest.
- [ ] 4.3 Run agent-docs-sync full Ruff, strict mypy, and pytest from the accepted worktree and record exact pass/skip counts, warnings, exit codes, and import origins in the evidence manifest.
- [ ] 4.4 Recompute every repository HEAD, raw dirty inventory, content-diff hash, and imported dependency path after gates; verify evidence and source identities still match before checking any completion task.
- [ ] 4.5 Rehearse per-repository Git-revert rollback in disposable worktrees, rerun focused Ruff/mypy tests, and record rollback exit codes without mutating default checkouts.
- [ ] 4.6 Commit each repository’s scoped result only after independent diff review, record full result SHAs in the manifest, and verify the capability-contract change remains unimplemented and all default dirty work is preserved.
