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

## Second advisor catch (during apply, post-2.2) — dead `global:` wrapper

After the initial 2.2 edit, the advisor flagged that Vitest does not support Jest's `global:` threshold wrapper: any key besides metric names is treated as a glob pattern, so `thresholds.global` matches zero files and leaves global thresholds unenforced. Verified against the installed vitest 4.1.10 source (`coverage.DM_a_rWm.js` `resolveThresholds` — non-metric keys are globs; real global thresholds are the top-level `lines/branches/functions/statements` keys) and corroborated empirically by final14 emitting only the four Analytics errors despite 41.32% global lines against the configured "75". Confirmed root cause of the silent skip: the "global" glob matches zero files, istanbul's `blankSummary` returns `pct: 'Unknown'` (string), and `'Unknown' < threshold` → `NaN < threshold` → false. The advisor also confirmed the ratchet3 `coverage-34.json` ENOENT was a worker thread dying before writing its coverage slice under heavy swap pressure (consistent with the environmental analysis in `verification.md`).

Disposition: config corrected — four global metrics moved to top-level `coverage.thresholds` keys; diff re-verified (+22/−11, single file); `npm run type-check` exit 0. Recorded in `design.md` Decision 2 and `tasks.md` 2.2.

## Disposition (first consultation)

Adopted in full as the approved policy (design.md Decisions 2–3, 5). The spec's controlling requirement independently mandates evidence-based thresholds, so the advisor review corroborates rather than overrides the spec.
