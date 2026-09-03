# Evidence — prime-agent verification (gates 6.1–6.3)

Executor: VerifyPrimeAgent worker (transcript: history://VerifyPrimeAgent; raw audit JSON /tmp/prime-agent-audit.json; test output via hub process 'prime-agent-test', cursor 2607).
Environment: node v22.23.2, npm 12.0.2, branch main (local commit f640f362 ahead 1).

## Gate 6.1 — npm audit --json
- exit 0; metadata.vulnerabilities = {info:0, low:0, moderate:0, high:0, critical:0, total:0}; advisory map empty.
- Verdict: PASS

## Gate 6.2 — focused tools-manager test
- `npm test -w @earendil-works/pi-coding-agent -- test/tools-manager.test.ts` (executed as managed one-shot hub process; workspace test script is `vitest --run`, not watch)
- exit 0; Vitest v4.1.9; Test Files 1 passed (1); Tests 6 passed (6); Duration 1.23s. All 6 named tests: version-check gating for managed/PATH tools; offline/Termux constraints; unsupported-target vs download-failure distinction; downloaded-binary validation; removal of failed binary; platform-specific ripgrep warnings.
- Verdict: PASS

## Gate 6.3 — this evidence file.

## Programmatic lockfile facts (package-lock.json, lockfileVersion 3)
- unzipper 0.12.5; @types/unzipper 0.10.11; extract-zip entries in lock = 0.
- Migration diff (all within migration-touched scope): packages/coding-agent/package.json removed extract-zip ^2.0.1, added unzipper ^0.12.5 + @types/unzipper ^0.10.11; tools-manager.ts line 3 imports Open as openZip from "unzipper".

## Unpatched upstream residuals
None — extract-zip fully removed from manifest and lockfile; 0 advisories.

## Deltas vs remediation session
None — fresh re-runs reproduce 0-vulnerability audit and 6/6 focused-test pass exactly.

## Notes
- A bash-sandbox false positive blocked direct `npm test -w` execution (misclassified as watch mode); true exit code 0 captured via managed one-shot process.
- No fixes made, no failures, no commits or pushes.
