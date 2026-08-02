## Context

The three repositories already pass their comprehensive suites, but review found mismatches at failure and fallback boundaries. In docs-sync, `ScannerTool` failure is collapsed to an empty discovery result and `build_report` always marks execution successful. Source-scope mappings are exact-key only. In agent-core, diagnostics emits an included-skill load error while iterating candidates, before a later directory can supply the valid candidate that the loader selects.

The affected docs-sync pipeline symbols have CRITICAL aggregate blast radius, so the implementation must be test-first and keep its data-flow change minimal. No external service, credential, deployment mechanism, or dependency is involved.

## Goals / Non-Goals

**Goals:**

- Preserve discovery failure as structured state through report construction and strict CLI exit handling.
- Make explicit directory mappings deterministic for descendants, preferring the most-specific matching mapping.
- Make diagnostics reflect the loader's final active set while retaining malformed-candidate visibility.
- Verify the complete three-repository feature surface before preparing commits.

**Non-Goals:**

- Redesigning public result models or loader precedence.
- Suppressing malformed candidate warnings.
- Changing agent-harness production code for these findings.
- Adding Testcontainers or any other dependency.

## Decisions

1. **Characterize public behavior before implementation.** Add CLI/report, source-scope, and diagnostics regressions first. This protects the broad docs-sync call graph and proves each finding independently.

2. **Propagate discovery failure explicitly.** `_discover` will return enough structured failure information for `build_report` to set `execution_succeeded` accurately. Strict CLI handling will use this field in addition to compliance. Treating failure as a synthetic compliance finding was rejected because it conflates operational execution with documentation state.

3. **Use deterministic mapping precedence.** Exact mappings remain authoritative; otherwise matching directory prefixes are ordered by specificity and the longest prefix wins. Merging all prefixes was rejected because parent and child mappings could create surprising duplicate obligations.

4. **Defer included-skill unloadability errors.** Diagnostics may warn for each malformed candidate, but it will decide the included-skill error only after scanning all candidates and comparing against the final loadable active set. Stopping at the first malformed source was rejected because it contradicts the loader's ordered fallback behavior.

5. **Keep repository commits separate.** `agent-core`, `agent-docs-sync`, and `agent-harness` retain independent commit history. Existing dirty changes are preserved and reviewed with per-repository status and GitNexus change detection.

## Risks / Trade-offs

- **CRITICAL docs-sync blast radius** → focused regressions run before and after the change, followed by the full suite and real CLI reproduction.
- **Compatibility risk from report state** → retain existing fields and aliases; only correct values on operational failure.
- **Ambiguous overlapping mappings** → normalize paths and choose the longest matching directory prefix deterministically.
- **Diagnostics could hide malformed files** → keep candidate-level warnings even when a later fallback loads successfully.
- **Large pre-existing dirty worktrees obscure scope** → inspect corrective diffs separately and run GitNexus detection before commit preparation.

## Migration Plan

No data or deployment migration is required. Apply the regressions and fixes, run focused and complete verification in all three repositories, then prepare separate conventional commits referencing this change. Rollback is the corresponding per-repository commit revert.

## Open Questions

None.
