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
2. **Approved policy (task 2.1 decision): option (b) — evidence-based baseline ratchet.** Thresholds move from the aspirational 75/85 block (provenance: initial tracking commit `95e031de`, untouched by migration `71b99ca3`, never once met) to integer safety floors set ~1% below the final14 measured values, so the canonical gate stops blocking the fully green 580-test suite while regression protection remains in force. The advisor review (slow-model consultation, this change) recommended exactly this option: permanent-red CI on unachievable thresholds destroys the CI signal and violates the spec's evidence-based-thresholds requirement; a green gate is the prerequisite for an effective ratchet. Exact values: global — statements 39 (measured 39.95), branches 33 (34.09), functions 34 (34.90), lines 40 (41.32); `src/components/Analytics/**/*` — statements 21 (21.96), branches 25 (26.19), functions 16 (17.42), lines 22 (22.83). Floors are integers ~0.8–1.4% below measured, per the advisor's flakiness analysis: V8 coverage percentages shift 0.05–0.2% on AST/import churn, so exact-value thresholds would make formatting changes CI-blocking. Both scopes reset together; leaving global at 75 would keep the gate permanently red, defeating the policy.
3. **Ratchet path toward 75/85:** threshold values are monotonic floors — decreases are rejected by policy; raises happen only through reviewed OpenSpec changes tied to the coverage work that earned them (e.g., a dedicated Analytics initiative testing ScatterPlot, GaugeChart, Heatmap, DrillDownPanel, AnalyticsFilters, Pagination, ExportManager bumps Analytics lines 22 → 45 → 65 → 85). The quality targets remain 75 global / 85 Analytics; the floors are enforcement floors, not completion claims. When measured coverage exceeds a floor by >3%, a follow-up OpenSpec change locks in the gain. Instrumentation, reporters, and excludes are untouched; the config block is commented as a ratchet baseline citing this change and the final14 run.
4. Separate the test result (580/580) from coverage enforcement in verification evidence. A green test dimension does not imply a green coverage dimension; under the approved floors both dimensions must be green for exit 0.
5. Task group 3 (focused component tests) is explicitly out of scope under this decision: the approved policy is the baseline ratchet, not the coverage-initiative path now. Focused tests for the seven substantially uncovered Analytics components belong to the follow-up initiative that earns the first threshold raise. Tasks 3.1/3.2 are annotated not-applicable in tasks.md accordingly; no test files are added in this change.

## Risks / Trade-offs

- Keeping aspirational thresholds preserves quality intent but leaves the canonical command nonzero until a policy decision is implemented.
- Adjusting thresholds to the baseline would restore a usable gate but could reduce enforcement; a ratchet and explicit review are required.
- Adding focused tests is higher effort but improves confidence and permits thresholds to rise without masking debt.
