## Why

OpenSpec strict validation currently fails for 66 of TDT's 212 main specs even
though all active changes pass. The legacy failures obscure real regressions and
prevent the runtime migration from using a fully green root-level validation
gate, so they need a separate, reviewable remediation rather than being mixed
into the OpenSpec 1.7 upgrade.

## What Changes

- Add a semantic-preservation contract for repairing legacy main-spec structure
  in bounded capability batches.
- Add concise `## Purpose` sections to the 64 main specs that lack one, deriving
  wording from their existing requirements and repository history without
  inventing product behavior.
- Restore a valid `## Requirements` section for
  `ai-review-durable-scheduler` without changing its existing requirement intent.
- Convert the four scenario-shape findings in `consumer-config-composition` into
  valid level-4 scenarios while preserving their current meaning.
- Validate each batch independently, compare requirement/scenario inventories
  before and after, and finish with a full strict-validation ratchet.
- Keep all existing capability directories and planning-root topology unchanged.

## Capabilities

### New Capabilities

- `openspec-main-spec-hygiene`: Semantic-preserving, batch-based requirements for repairing and validating legacy OpenSpec main-spec structure.

### Modified Capabilities

- None. The 66 repaired capability files receive structural/documentation fixes
  only; their normative product requirements do not change.

## Impact

- **Specs:** 66 existing files under `openspec/specs/*/spec.md` plus the new
  `openspec-main-spec-hygiene` governance capability.
- **Validation:** the root-level OpenSpec strict baseline moves from 146/212
  valid main specs toward an all-valid baseline, with every batch required to
  reduce—not reshuffle—the known failure set.
- **Applications/APIs:** no application code, API, database, deployment, auth,
  dependency, or runtime behavior change.
- **Coordination:** this follow-up begins only after the OpenSpec 1.7 runtime
  migration records its baseline; it does not weaken that migration's scoped
  non-regression gate.
- **Risk:** MEDIUM documentation-contract radius because inaccurate Purpose or
  scenario edits could misstate existing behavior across many capabilities.

## Non-Goals

- No store extraction, `defaultStore`, workset, nested-spec migration, directory
  rename, symlink removal, or dedicated planning repository.
- No new product requirements, implementation work, application tests, or
  behavioral cleanup hidden inside validation repairs.
- No bulk mechanical placeholder text and no copying Purpose text between
  unrelated capabilities.
- No archive, commit, push, or remediation of active-change artifacts as part of
  this proposal.
