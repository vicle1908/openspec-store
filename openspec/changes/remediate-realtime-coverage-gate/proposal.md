## Why

The Vitest test suite is green, but `test:ci` still exits nonzero because pre-existing coverage thresholds are unmet: global coverage is about 40% against 75%, and `src/components/Analytics/**/*` is 22.83% against 85%. The threshold failure became visible only after the migration-related test failures were fixed, so it needs a separately governed coverage decision rather than a silent config change. This is distinct from `remediate-2026-09-06-archive-gaps`, which addresses evidence and archive-integrity gaps; this change addresses measured frontend coverage policy and component test debt.

## What Changes

- Inventory the exact Analytics files and metrics responsible for the threshold failure.
- Establish an evidence-based coverage policy for the realtime frontend.
- Add focused behavioral tests for the highest-value uncovered Analytics components where practical.
- Preserve existing thresholds until the corrective decision is reviewed and validated.
- Record the final policy, coverage evidence, and follow-up work in OpenSpec artifacts.

Explicit non-goals:

- Do not delete or silently lower coverage thresholds.
- Do not rewrite unrelated migration tests or production behavior solely to inflate coverage.
- Do not modify concurrent OpenSpec changes.

## Capabilities

### New Capabilities

- `realtime-analytics-coverage`: Evidence-based coverage enforcement and focused test coverage for Analytics components.

### Modified Capabilities

- None. This change governs verification and test coverage; it does not intentionally change end-user Analytics behavior.

## Affected Ownership Boundaries

- `realtime/frontend`: Analytics component tests, coverage configuration only if explicitly approved by the resulting spec.
- `openspec-store`: proposal, specification, design, tasks, and verification evidence.
