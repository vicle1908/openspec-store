# Verification Evidence

- Baseline commit: `f196754`, isolated worktree `/tmp/realtime-f196754`.
- Baseline command: `cd /tmp/realtime-f196754/frontend && npm install --no-audit --no-fund && npx vitest run`.
- Baseline result: 51 failed, 33 passed, 6 skipped test files; 57 failed, 282 passed, 44 skipped tests; 2 errors. The historical lockfile was inconsistent, so `npm ci` was not usable.
- Migration changes: `test:ci` uses `vitest run --coverage`; test globals use `vitest/globals`; setup helpers are excluded; async Vitest mock factories and remaining fast-check imports were migrated; JSX-bearing property tests were renamed to `.tsx`; focused WebSocket/chart/property fixtures were corrected.
- Current focused verification: `ColorUniqueness.property.test.tsx` passed 5/5; `TimeSeriesDataIntegrity.property.test.tsx` passed 5/5; `WebSocketCleanup.property.test.tsx` passed 4/4; the analytics property group passed 28/28; `performanceProperties.test.tsx` passed 10/10 in 2.25s; `integrationProperties.test.tsx` passed 10/10 in 7.72s; `npm run type-check` passed.
- Production build: `npm run build` passed; TypeScript and Vite completed, transforming 2795 modules. Existing chunking/size warnings remain.
- OOM root cause resolution: identified that in fast-check v4, positional `fc.integer(min, max)` generated unconstrained 32-bit integers up to 2 billion (e.g. 178 million widgets), causing V8's `invalid table size` crash in `Array.from`. Converted all positional `fc.integer` calls to `fc.integer({ min, max })` across all property test suites, completely eliminating the crash.
- Full-suite gate: `performanceProperties` and `integrationProperties` now run to completion in seconds; task 6 remains open for the remaining pre-existing unit test assertion mismatches.
- Strict OpenSpec validation: `openspec validate align-realtime-vitest-docs --strict --json` passed after the latest evidence update.
