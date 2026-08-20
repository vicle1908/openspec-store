## Why

The current Pydantic AI consumer baseline cannot serve as an implementation prerequisite because agent-harness and agent-docs-sync fail full Ruff, and agent-harness also fails strict mypy at the public `agent_core.sdk` boundary. These mechanical failures must be repaired and frozen separately before product behavior is changed so later capability evidence is attributable to the capability change rather than unrelated tooling debt.

## What Changes

- Capture exact pre-edit HEADs, raw dirty inventories, content-diff fingerprints, runtime import origins, and current Ruff/mypy failure classifications for agent-core, agent-harness, and agent-docs-sync.
- Resolve the current `AssuranceLevel` public-export/type-checking mismatch without widening production types or bypassing strict mode.
- Normalize the current Ruff `I001` import-order findings in agent-harness and agent-docs-sync while preserving test behavior byte-for-byte apart from formatting.
- Re-run focused and full Ruff, strict mypy, and pytest gates from dedicated repository worktrees with isolated caches and immutable dependency bindings.
- Retain a named evidence ledger that distinguishes current passes, prerequisite-conditioned skips, infrastructure limitations, and unrelated dirty/generated state.

## Non-goals

- No Pydantic AI or pydantic-ai-harness version change.
- No capability default, public API, runtime, provider, model-resolution, guardrail, persistence, or observability behavior change.
- No edits to current dirty default checkouts, generated Graphify state, or the active observability change.
- No task reconciliation, sync, or archive of the capability-contract change.

## Capabilities

### New Capabilities

None. This change restores existing quality gates and sets `skip_specs: true`.

### Modified Capabilities

None. Existing quality and framework-verification requirements already require these gates.

## Impact

- **agent-core owner:** public SDK export metadata and exact import-origin verification only.
- **agent-harness owner:** strict-mypy repair and mechanical test import ordering.
- **agent-docs-sync owner:** mechanical test import ordering.
- **openspec-store owner:** planning artifacts and immutable evidence ledger only.
- Implementation must use one writer and one dedicated worktree per repository and must stop if the current dirty owner matrix is unresolved.
