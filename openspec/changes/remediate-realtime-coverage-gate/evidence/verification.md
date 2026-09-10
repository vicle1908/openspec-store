# Verification Record — remediate-realtime-coverage-gate

## Canonical command

From `realtime/frontend`: `npm run test:ci -- --reporter=dot --maxWorkers=1`
(`test:ci` = `vitest run --coverage`; Vitest 4.1.10, v8 coverage provider, Node 22.23.2)

## Strict OpenSpec validation (task 4.2) — PASSED

Command: `openspec validate remediate-realtime-coverage-gate --strict --json --store openspec-store`
Result: `{"id": "remediate-realtime-coverage-gate", "valid": true, "issues": []}`, summary `1/1 passed`, exit code `0`.

## Implementation verification (tasks 1.1–2.2) — PASSED

- 1.1: `evidence/coverage-baseline.md` contains the full 15-file Analytics table (all four metrics per file) from the final14 run — read back and verified.
- 1.2: threshold provenance recorded: thresholds entered at `95e031de` (initial tracking, `git show` threshold block present), byte-identical at `71b99ca3` (migration) and at HEAD `21c790e7`.
- 2.1: policy decision recorded in `design.md` Decisions 2–3 (option (b), integer safety floors, monotonic ratchet toward 75/85); advisor review captured in `evidence/advisor-policy-review.md`.
- 2.2: `realtime/frontend/vitest.config.ts` `coverage.thresholds` block only — `git diff --stat` one file (final: +22/−11); floors global 39/33/34/40 (top-level metric keys), Analytics 21/25/16/22; instrumentation/reporters/excludes untouched; `npm run type-check` exit 0. **Correction during apply:** the first edit (+16/−9) kept the inherited Jest-style `global: {...}` wrapper. Advisor review flagged, and vitest 4.1.10 source confirmed (`node_modules/vitest/dist/chunks/coverage.DM_a_rWm.js`, `resolveThresholds`: non-metric keys are glob patterns; real global thresholds come from top-level metric keys), that the wrapper is dead config: glob "global" matches zero files and istanbul's `blankSummary` returns `pct: 'Unknown'`, so every comparison is `NaN < threshold` → false — never enforced, never errored. Empirical corroboration: the final14 run emitted only the four Analytics threshold errors and no global error despite 41.32% lines vs the configured "75". The corrected config makes global thresholds enforceable for the first time in this repo.
- Enforcement smoke proof (post-correction, 23:14–23:15, logs `/tmp/threshold-smoke.log`, `/tmp/threshold-smoke2.log`): `npx vitest run <file> --coverage --reporter=dot --maxWorkers=1` — (a) OfflineBanner (90/100/83.33/89.47): passes floors, exit 0; (b) VideoCall (29.85/17.39/11.11/31.49, below floors): emits `ERROR: Coverage for lines (31.49%) does not meet global threshold (40%)` (+ functions/statements/branches) and exits 1 — the first global-threshold enforcement ever in this repo. Both runs took 1.8–3.5s under load ~59, confirming single-file runs are unaffected by the contention that blocks the full suite.

## Canonical gate (task 4.1) — PASSED

**Final run: `npm run test:ci -- --reporter=dot --maxWorkers=1` from `realtime/frontend`, 2026-09-10 03:46:00, log `/tmp/realtime-test-ci-final-gate.log`, exit code 0.**

- Test Files: **78 passed | 5 skipped (83)** — zero failures
- Tests: **580 passed | 43 skipped (623)** — zero failures, zero unhandled errors
- Duration: 131.46s (normal quiet-machine profile)
- Coverage summary (All files): Statements 39.95% (1636/4095), Branches 34.09% (1018/2986), Functions 34.9% (400/1146), Lines 41.32% (1575/3811)
- `src/components/Analytics` directory: Statements 21.96, Branches 26.19, Functions 17.42, Lines 22.83
- Threshold errors: **none** (no "does not meet" anywhere in the log)
- Floor checks: global 39.95≥39, 34.09≥33, 34.9≥34, 41.32≥40; Analytics 21.96≥21, 26.19≥25, 17.42≥16, 22.83≥22 — all 8 pass
- Both dimensions green: test gate (580/580) AND coverage gate (all floors met) → exit 0. Coverage numbers are identical to the final14 baseline, confirming the change is enforcement-only (numbers unchanged, thresholds now evidence-based and — for the first time — globally enforceable).

The gate now satisfies the spec's "Both tests and coverage pass" scenario: canonical command exits successfully with both gates green.

### History: six earlier environmental failures (2026-09-09, preserved for the record)

Six attempts on 2026-09-09, all failing under environmental contention (12 concurrent users, 5-day uptime, 15–17.5GB swap of 16–18GB used) — every failure a timeout, worker crash, or environment error, never a code or threshold failure:

| Run | Start | Duration | Result | Failure mode |
|---|---|---|---|---|
| ratchet1 (`/tmp/realtime-test-ci-ratchet.log`) | 21:26:58 | 305s | exit 1 | 2 property tests timed out (10s) in `ColorUniqueness.property.test.tsx`; machine load 37–49 |
| ratchet2 (`/tmp/realtime-test-ci-ratchet2.log`) | 21:37 | 106s | exit 1 | `Error: Worker exited unexpectedly` (Node worker crash; quiet dip, ~15GB swap in use) |
| ratchet3 (`/tmp/realtime-test-ci-ratchet3.log`) | 21:44 | 456s | exit 1 | All tests ran (no FAIL lines); ENOENT `coverage/.tmp/coverage-34.json` during v8 coverage summary readback — suspected OOM kill of worker, not confirmed (no coverage summary was emitted; test results are unverified) |
| ratchet4 (`/tmp/realtime-test-ci-ratchet4.log`) | 22:01:23 | 144s | exit 1 | 2 tests failed in `integrationProperties.test.tsx`: one 30s timeout + one timing-sensitive property assertion (`expected undefined to be defined`, counterexample [3,18]) under contention |
| ratchet5 (window poll) | 22:11–22:56 | 45min | no run | No 45-min window with 1-min load < 5 and 5-min load < 20; load oscillated 6–88, swap ~15GB of 16GB throughout |
| ratchet6 (`/tmp/realtime-test-ci-ratchet6.log`) | 23:25:39 | ~5min | exit 1 | `Error: Worker exited unexpectedly` late in the suite (during Analytics ErrorScenarios stderr); window had load1 6.46 / load5 15.02 — consistent with memory (swap) contention but root cause not confirmed |

Environmental evidence that the suite and config are sound:

- Baseline final14 run (log `/tmp/realtime-test-ci-final14.log`, pre-change): 78 files / 580 tests passed, coverage table emitted, exit nonzero solely from the old aspirational thresholds.
- `ColorUniqueness.property.test.tsx` re-run in isolation at 21:33 under the same memory pressure: **5/5 passed, exit 0** (3.46s test time).
- `integrationProperties.test.tsx` re-run in isolation at 22:05 under the same memory pressure: **10/10 passed, exit 0** (4.78s test time).
- The 2.2 config edit changes threshold numbers only; it cannot affect test execution. Every full-suite failure above occurred under heavy environmental contention (12 concurrent users, 5-day uptime, 15GB swap used), manifesting as timeouts, worker crashes, or environment errors — none are code regressions or threshold failures (the exact root causes were not individually confirmed).

Coverage-table validation status: **validated by the final green run** — the floors (global 39/33/34/40, Analytics 21/25/16/22) derived from final14 measured values (39.95/34.09/34.90/41.32; 21.96/26.19/17.42/22.83) with a ~1% cushion all passed with zero threshold errors and exit 0 on 2026-09-10 (log `/tmp/realtime-test-ci-final-gate.log`).

## Strict validation (task 4.2) — PASSED

Command: `openspec validate remediate-realtime-coverage-gate --strict --json --store openspec-store`
Result: `{"id": "remediate-realtime-coverage-gate", "valid": true, "issues": []}`, summary `1/1 passed`, exit code `0` — re-run after every artifact/evidence update through apply, and confirmed once more after the final commits (`d9215e79` in realtime, `b201a692` in the store): same result, exit `0`.

## Final state (task 4.3) — COMMITTED

- `realtime` @ `d9215e79` `test(frontend): set evidence-based coverage floors with monotonic ratchet` — one file (`frontend/vitest.config.ts`, +22/−11), stacks directly on `21c790e7`. Working tree clean except the pre-existing untracked `frontend/Makefile` (not part of this change).
- `openspec-store` — change artifacts fully committed: `24252605` (planning), `cc6d3142` (evidence + decision), `f99a98a3` (enforceable-thresholds correction), `30e3131f` (enforcement proof + attempt record), `b201a692` (gate-green completion + 4.3 tick). Change dir clean.
- Concurrent sessions' paths in both repos untouched throughout.
