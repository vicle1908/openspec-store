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
- 2.2: `realtime/frontend/vitest.config.ts` `coverage.thresholds` block only — `git diff --stat` one file (+16/−9); floors global 39/33/34/40, Analytics 21/25/16/22; instrumentation/reporters/excludes untouched.

## Canonical gate (task 4.1) — NOT YET ACHIEVED (blocked by workstation contention)

**The canonical command has NOT exited 0 under the new floors. No claim is made that the coverage gate is fixed.**

Five attempts on 2026-09-09, all failing environmentally (never by a threshold miss):

| Run | Start | Duration | Result | Failure mode |
|---|---|---|---|---|
| ratchet1 (`/tmp/realtime-test-ci-ratchet.log`) | 21:26:58 | 305s | exit 1 | 2 property tests timed out (10s) in `ColorUniqueness.property.test.tsx`; machine load 37–49 |
| ratchet2 (`/tmp/realtime-test-ci-ratchet2.log`) | 21:37 | 106s | exit 1 | `Error: Worker exited unexpectedly` (Node worker crash; quiet dip, ~15GB swap in use) |
| ratchet3 (`/tmp/realtime-test-ci-ratchet3.log`) | 21:44 | 456s | exit 1 | All tests ran (no FAIL lines); unhandled `ENOENT coverage/.tmp/coverage-34.json` during v8 coverage collection — worker died before writing its tmp coverage file |
| ratchet4 (`/tmp/realtime-test-ci-ratchet4.log`) | 22:01:23 | 144s | exit 1 | 2 tests failed in `integrationProperties.test.tsx`: one 30s timeout + one timing-sensitive property assertion (`expected undefined to be defined`, counterexample [3,18]) under contention |
| ratchet5 (window poll) | 22:11–22:56 | 45min | no run | No 45-min window with 1-min load < 5 and 5-min load < 20; load oscillated 6–88, swap ~15GB of 16GB throughout |

Environmental evidence that the suite and config are sound:

- Baseline final14 run (log `/tmp/realtime-test-ci-final14.log`, pre-change): 78 files / 580 tests passed, coverage table emitted, exit nonzero solely from the old aspirational thresholds.
- `ColorUniqueness.property.test.tsx` re-run in isolation at 21:33 under the same memory pressure: **5/5 passed, exit 0** (3.46s test time).
- `integrationProperties.test.tsx` re-run in isolation at 22:05 under the same memory pressure: **10/10 passed, exit 0** (4.78s test time).
- The 2.2 config edit changes threshold numbers only; it cannot affect test execution. Every full-suite failure above is a timeout/crash artifact of memory contention (12 concurrent users, 5-day uptime, 15GB swap used), not a code regression.

Coverage-table validation status: no post-change run has reached the coverage table (runs with failed tests print no coverage report; ratchet3, which passed all tests, crashed during coverage tmp-file collection). The floors (global 39/33/34/40, Analytics 21/25/16/22) are derived from final14 measured values (39.95/34.09/34.90/41.32; 21.96/26.19/17.42/22.83) with a ~1% cushion per the advisor's flakiness analysis, but their exit-0 demonstration remains pending a quiet-machine run.

## Remaining work

- 4.1: one clean canonical-gate run (exit 0) on an uncontended machine; record exact numbers (test files, tests, coverage summary, threshold errors = none expected, exit code).
- 4.3: commit frontend `vitest.config.ts` edit + final store artifacts after 4.1 verifies green.
