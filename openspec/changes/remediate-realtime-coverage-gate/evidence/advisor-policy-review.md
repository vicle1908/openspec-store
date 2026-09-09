# Advisor Policy Review — Task 2.1 (coverage threshold policy)

Consulted during apply of `remediate-realtime-coverage-gate` at the task-2.1 decision point, before any `vitest.config.ts` edit. Slow-model advisor consultation presenting the full evidence (final14 measured coverage, provenance, spec requirements) and both design options.

## Advisor recommendation (verbatim summary)

**Option (b) — evidence-based baseline ratchet.** Key points:

1. Option (a) rejected: a permanently red CI gate on aspirational targets destroys the CI signal (engineers tune out failures, masking real regressions) and violates the spec's evidence-based-thresholds requirement ("SHALL use thresholds justified by the latest measured repository coverage", "without blocking a fully passing test suite on aspirational, unachievable thresholds"). A green gate is the prerequisite for an effective ratchet.
2. Floors must NOT equal exact measured values — V8 coverage percentages shift 0.05–0.2% on AST/import churn; exact-value thresholds turn formatting changes into CI blockers. Use integer floors with ~0.8–1.4% cushion below measured.
3. Flooring rule: floor to nearest integer; if remaining headroom < 0.5%, drop one more point. Applied values: global — statements 39, branches 33, functions 34, lines 40; Analytics — statements 21, branches 25, functions 16, lines 22.
4. Global thresholds must reset alongside Analytics; leaving global at 75 keeps the gate permanently red, defeating the policy.
5. Ratchet: thresholds are monotonic floors — decreases rejected; raises only via reviewed OpenSpec changes tied to the coverage work that earned them (e.g., Analytics lines 22 → 45 → 65 → 85 as the dedicated initiative tests the seven uncovered components). Optional non-blocking alert when measured exceeds floor by >3% to prompt locking in gains.
6. Compliance with "SHALL NOT claim coverage completion": floors are enforcement floors, not completion claims — tag the config block as a ratchet baseline citing provenance, keep all instrumentation/excludes untouched, and reports continue to show measured values (ScatterPlot 0.7%, GaugeChart 1.06% remain visible as debt).

## Disposition

Adopted in full as the approved policy (design.md Decisions 2–3, 5). The spec's controlling requirement independently mandates evidence-based thresholds, so the advisor review corroborates rather than overrides the spec.
