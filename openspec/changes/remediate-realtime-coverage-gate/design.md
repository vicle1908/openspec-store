## Context

See proposal.md - Why. The realtime frontend's canonical Vitest command now runs 580 tests successfully, but coverage reports 22.83% lines for `src/components/Analytics/**/*` against an 85% threshold. The configured thresholds predate the Vitest migration and the prior failing runs did not emit coverage reports.

## Goals / Non-Goals

**Goals:**

- Preserve coverage instrumentation and make test and coverage outcomes independently visible.
- Establish a conservative, measurable baseline policy through OpenSpec rather than silently lowering or deleting thresholds.
- Leave room for a future coverage initiative to raise thresholds as component coverage improves.

**Non-Goals:**

- Do not author broad new component suites in this corrective planning change.
- Do not alter production Analytics behavior to improve percentages.
- Do not modify concurrent OpenSpec changes.

## Decisions

1. Treat the measured final14 values as the evidence baseline: 41.32% lines globally and 22.83% Analytics lines, with the existing configured targets of 75% and 85% respectively.
2. Keep the existing thresholds unchanged until this change's implementation phase has an explicit reviewed policy decision. No threshold is removed or silently reduced.
3. Separate the test result (580/580) from coverage enforcement in verification evidence. A green test dimension does not imply a green coverage dimension.
4. If a realistic threshold policy is approved, change only the coverage configuration and document the ratchet target. Otherwise, defer threshold adjustment to a dedicated coverage initiative with focused tests for the seven substantially uncovered Analytics components.

## Risks / Trade-offs

- Keeping aspirational thresholds preserves quality intent but leaves the canonical command nonzero until a policy decision is implemented.
- Adjusting thresholds to the baseline would restore a usable gate but could reduce enforcement; a ratchet and explicit review are required.
- Adding focused tests is higher effort but improves confidence and permits thresholds to rise without masking debt.
