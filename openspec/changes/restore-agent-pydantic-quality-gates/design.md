## Context

See proposal.md for the motivation. The current default checkouts are dirty, so implementation must use one dedicated worktree per repository and bind every result to an immutable base SHA before editing.

## Goals / Non-Goals

**Goals:**

- Restore the repository-defined Ruff and strict-mypy gates with the smallest mechanical diff.
- Prove that the public SDK export is visible to both runtime imports and strict static analysis.
- Preserve current test behavior and unrelated dirty/generated state.

**Non-Goals:**

- No runtime capability or dependency behavior changes.
- No cleanup of unrelated CI, documentation, scheduler, or Graphify paths currently dirty in agent-core.

## Decisions

- **One writer per repository:** use dedicated worktrees based on a captured immutable SHA; the default dirty checkouts remain read-only.
- **Explicit SDK export:** expose `AssuranceLevel` through the existing `agent_core.sdk` public export convention, including `__all__`, rather than weakening mypy or importing a private module in agent-harness.
- **Mechanical import repair:** run Ruff’s import-order fixer only on the classified agent-harness and agent-docs-sync paths, review the resulting diff, and reject unrelated formatting churn.
- **Evidence before completion:** record raw status, content fingerprint, module origins, full gate commands, exit codes, and prerequisite-conditioned skips in a named ledger before checking tasks.

## Risks / Trade-offs

- [Dirty-owner collision] → stop before editing if a current owner claims any selected source/test path; recapture after a sole writer is established.
- [Editable dependency contamination] → assert `agent_core.__file__` and `agent_core.sdk.__file__` for agent-harness before mypy and tests.
- [Mechanical fix hides behavior drift] → compare changed paths and run focused plus full tests; no production source changes beyond the explicit SDK export.
- [Restricted cache] → use disposable UV/Ruff/mypy caches and classify missing cached build dependencies separately from source failures.

## Migration Plan

1. Freeze repository identities and dirty fingerprints.
2. Apply the SDK export and mechanical import repairs in separate repository worktrees.
3. Run focused gates, then full pytest/Ruff/strict-mypy with immutable dependency origins.
4. Commit each repository only after evidence review; retain rollback as per-repository Git revert plus cache regeneration.
