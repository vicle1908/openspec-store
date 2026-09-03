# Evidence — realtime/frontend verification (gates 7.1–7.3)

Executor: VerifyRealtimeFrontend worker (transcript: history://VerifyRealtimeFrontend; raw logs /tmp/rt-frontend-audit.json, /tmp/rt-frontend-build.log, /tmp/rt-tsc-probe.log, /tmp/rt-tsc-withjest.log, /tmp/rt-vite-only.log).
Environment: node v22.23.2.

## Gate 7.1 — npm audit --json
- exit 0; metadata.vulnerabilities all 0 (total 0); dependencies prod 164 / dev 600 / optional 66 / peer 9, total 776.
- Verdict: PASS (matches remediation outcome exactly)

## Gate 7.2 — project build (`npm run build` = tsc && vite build)
- Initial verification exposed a real configuration defect: undeclared `jest` types and test-only files included in the production TypeScript program.
- Corrective change `fix-realtime-frontend-build` updated `realtime/frontend/tsconfig.json`: removed `jest` from `compilerOptions.types`; excluded `src/tests/**/*` and `src/test-utils.tsx`.
- Fresh `npm run build` → exit 0; TypeScript and Vite completed, 2795 modules transformed, dist generated. Remaining warnings are non-blocking: authService dynamic/static import and chunks over 500 kB.
- Verdict: PASS after corrective fix.
- Fresh jspdf runtime smoke → exit 0; jspdf 4.2.1 generated a valid 3157-byte PDF ArrayBuffer.

## Gate 7.3 — this evidence file.

## Unpatched upstream residuals
None (audit total 0).

## Deltas vs remediation session
Audit and jspdf smoke: none. The original build failure was fixed by corrective OpenSpec change `fix-realtime-frontend-build`; fresh build now exits 0.

## Fixes made
`/Users/androidteam/Developer/realtime/frontend/tsconfig.json`: removed undeclared Jest types and excluded test-only TypeScript inputs. Verified by fresh audit, build, and jspdf smoke.
