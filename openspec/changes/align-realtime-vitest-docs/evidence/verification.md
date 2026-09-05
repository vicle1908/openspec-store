# Verification Evidence

- Baseline commit: `f196754`, isolated worktree `/tmp/realtime-f196754`.
- Baseline command: `cd /tmp/realtime-f196754/frontend && npm install --no-audit --no-fund && npx vitest run`.
- Baseline result: 51 failed, 33 passed, 6 skipped test files; 57 failed, 282 passed, 44 skipped tests; 2 errors. The historical lockfile was inconsistent, so `npm ci` was not usable.
- Migration changes: `test:ci` uses `vitest run --coverage`; test globals use `vitest/globals`; setup helpers are excluded; async Vitest mock factories and remaining fast-check imports were migrated; JSX-bearing property tests were renamed to `.tsx`; focused WebSocket/chart/property fixtures were corrected.
- Current focused verification: `ColorUniqueness.property.test.tsx` passed 5/5; `TimeSeriesDataIntegrity.property.test.tsx` passed 5/5; `WebSocketCleanup.property.test.tsx` passed 4/4; the analytics property group passed 28/28; `Integration Property 1` passed in 3.03s; `npm run type-check` passed.
- Production build: `npm run build` passed; TypeScript and Vite completed, transforming 2795 modules. Existing chunking/size warnings remain.
- Canonical full-suite attempt: `NODE_OPTIONS=--max-old-space-size=8192 npm run test:ci -- --reporter=dot --maxWorkers=1` progressed for 190.88s through `Integration Property 8` before the worker exited unexpectedly (artifact `470`). No green full-suite result exists; task 6 remains incomplete.
- Heavy-suite diagnostics: the remaining integration/performance workload still has resource/worker termination behavior; this is documented rather than treated as a pass.
- Strict OpenSpec validation: `openspec validate align-realtime-vitest-docs --strict --json` passed after the latest evidence update. Current frontend `npm run type-check` and `npm run build` passed.
