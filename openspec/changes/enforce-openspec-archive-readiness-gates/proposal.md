## Why

Recent Pydantic AI changes were moved into the archive with incomplete tasks and were marked complete in later commits, even though existing specs already prohibit unsupported completion claims. The store needs executable enforcement so archive readiness is checked at the mutation boundary rather than reconstructed after the fact.

## What Changes

- Add a repository-owned archive-readiness validator that checks task completion, required artifact presence, authoritative delta-spec paths, exact source/evidence identities, required gate results, and rollback evidence before a change can be reported ready.
- Add deterministic checks for archived changes that still contain incomplete tasks or whose completion-only task edits occurred after the archive move.
- Produce a corrective ledger for the four reviewed dependency/capability archives and cross-reference the owning active corrective change instead of rewriting archived artifacts.
- Integrate the validator into store verification and agent archive guidance so single and bulk archive workflows stop before mutation when readiness is incomplete.
- Require archive evidence to bind source HEADs, raw dirty inventories, content-diff fingerprints, imported dependency origins, prerequisite-aware passes/skips, spec-sync results, and final store identity.
- Add tests covering no-delta changes, skipped specs, missing evidence, incomplete tasks, source drift, failed or unavailable gates, post-archive mutation detection, and clean successful archive readiness.

## Non-goals

- No modification of the external OpenSpec CLI package or user-global authentication/configuration.
- No rewriting, deleting, moving, or retroactively checking tasks in existing archives.
- No implementation of Pydantic AI runtime behavior or repair of Python Ruff/mypy findings.
- No mutation of the current untracked observability change or unrelated active JTI change.

## Capabilities

### New Capabilities

None. This change enforces existing archive, readiness-evidence, and framework-verification requirements and sets `skip_specs: true`.

### Modified Capabilities

None. Existing normative requirements already cover corrective ledgers, evidence-gated completion, inline spec sync, and pre-archive revalidation.

## Impact

- **openspec-store owner:** validation scripts, tests, store verification entry points, archive guidance, and the corrective evidence ledger.
- **workspace skill owner:** only the reviewed canonical archive workflow surface, followed by the required managed-skill sync/check; no hand-edited generated mirrors.
- **code repository owners:** read-only evidence providers; this change does not edit agent-core, agent-harness, or agent-docs-sync.
- The validator must remain fail-closed for required evidence while distinguishing an intentional `skip_specs: true` no-op from a missing delta spec.
