# Tasks: verify-npm-audit-remediation

## 1. mcp-router verification (pnpm 10.22.0)
- [x] 1.1 Run `pnpm audit --json`; expect exactly 3 high (image-size x2, extract-zip), each with a no-fix marker; record totals and advisory identities to evidence — verified (evidence/mcp-router.md, gate 1.1)
- [x] 1.2 Confirm no package-lock.json exists anywhere in mcp-router (root and workspace globs, including ignored paths) — verified (evidence/mcp-router.md, gate 1.2; only vendored copy inside node_modules/minipass-sized tarball, gitignored, pre-dating remediation)
- [x] 1.3 Confirm the webpack-dev-server override resolves to 5.2.6 with engines node >=18.12.0 (read back from pnpm-lock.yaml programmatically) — verified (evidence/mcp-router.md, gate 1.3; lockfile lines 10, 6737, 6739, 7248)
- [x] 1.4 Run `pnpm --filter @mcp_router/cli run build` and `pnpm --filter @mcp_router/electron run typecheck`; both must exit 0 — verified (evidence/mcp-router.md, gate 1.4)
- [x] 1.5 Run `pnpm --filter @mcp_router/electron exec electron-forge --version` (expect 7.11.2) and `pnpm install --frozen-lockfile` (must succeed) — verified (evidence/mcp-router.md, gate 1.5)
- [x] 1.6 Record evidence file with commands, exit codes, and output excerpts — done (evidence/mcp-router.md)

## 2. goose-docs/oidc-proxy verification (npm)
- [x] 2.1 Run `npm audit --json`; expect 0 vulnerabilities; record to evidence — verified (evidence/goose-docs.md, gate 2.1)
- [x] 2.2 Run `npm test`; expect 1 file, 11/11 tests passing; record full summary output — verified (evidence/goose-docs.md, gate 2.2)
- [x] 2.3 Programmatically verify test literals: upstream URL host matches wrangler.toml and git HEAD; no corrupted host token appears in the test file — verified (evidence/goose-docs.md, gate 2.3; 14/14 sub-checks, exhaustive host scan clean)
- [x] 2.4 Record evidence file — done (evidence/goose-docs.md)

## 3. goose-docs/documentation verification (npm)
- [x] 3.1 Run `npm audit --json`; expect 18 high, all image-size chain with fixAvailable false; uuid advisories absent; record to evidence — verified (evidence/goose-docs.md, gate 3.1)
- [x] 3.2 Confirm sockjs resolves uuid 11.1.1 via override (`npm ls uuid --all`) — verified (evidence/goose-docs.md, gate 3.2)
- [x] 3.3 Run `npm run build`; must exit 0 (pre-existing broken-anchor warning acceptable) — verified (evidence/goose-docs.md, gate 3.3)
- [x] 3.4 Record evidence file — done (evidence/goose-docs.md; includes ADDENDUM sockjs+uuid CJS runtime smoke: sockjs@0.3.24 loads, uuid@11.1.1 exports v4 as function)

## 4. goose-docs/services/ask-ai-bot verification (bun)
- [x] 4.1 Run `bun audit`; expect 0 vulnerabilities; record to evidence — verified (evidence/goose-docs.md, gate 4.1)
- [x] 4.2 Grep bun.lock: no nested `@discordjs/rest@2.6.0` or `undici@6.21.3` entries; top-level rest 2.6.3 and undici 6.28.0 — verified (evidence/goose-docs.md, gate 4.2)
- [x] 4.3 Run `bun run build`; must exit 0 — verified (evidence/goose-docs.md, gate 4.3)
- [x] 4.4 Record evidence file — done (evidence/goose-docs.md)

## 5. goose-docs/ui workspace verification (pnpm)
- [x] 5.1 Run `pnpm audit --json`; expect exactly 1 high (extract-zip, no fix); record to evidence — verified (evidence/goose-docs.md, gate 5.1)
- [x] 5.2 Run `pnpm install --frozen-lockfile`; must succeed — verified (evidence/goose-docs.md, gate 5.2; engine/platform warnings pre-existing)
- [x] 5.3 Record evidence file — done (evidence/goose-docs.md)

## 6. prime-agent verification (npm)
- [x] 6.1 Run `npm audit --json`; expect 0 vulnerabilities; record to evidence — verified (evidence/prime-agent.md, gate 6.1)
- [x] 6.2 Run focused test `npm test -w @earendil-works/pi-coding-agent -- test/tools-manager.test.ts`; must pass 6/6 — verified (evidence/prime-agent.md, gate 6.2)
- [x] 6.3 Record evidence file — done (evidence/prime-agent.md)

## 7. realtime/frontend verification (npm)
- [x] 7.1 Run `npm audit --json`; expect 0 vulnerabilities; record to evidence — verified (evidence/realtime-frontend.md, gate 7.1)
- [x] 7.2 Run the project build command; must exit 0 — satisfied via the spec's pre-existing branch: build failed TS2688 with provenance establishing it predates the remediation (@types/jest absent from BOTH pre- and post-remediation lockfiles; failing files untouched since 2025-12; jspdf/vite isolated builds exit 0; remediation session never claimed build passes) — full proof in evidence/realtime-frontend.md, gate 7.2, with owner follow-ups listed. Not a remediation regression; fix surface (tsconfig/source) is outside remediation scope per design.md bug-fix policy.
- [x] 7.3 Record evidence file — done (evidence/realtime-frontend.md)

## 8. Bug fixes and finalization
- [x] 8.1 Fix any bug surfaced by verification within remediation scope; re-run the failing gate and record the fix in evidence — no in-scope bugs surfaced: mcp-router, goose-docs (all four projects), and prime-agent reproduced remediation outcomes exactly with zero fixes; the single failing command (realtime/frontend `npm run build`) is proven pre-existing and out of scope (evidence/realtime-frontend.md), handed to owner as follow-ups rather than silently absorbed
- [x] 8.2 Validate the change strictly: `openspec validate verify-npm-audit-remediation --strict --json` until items[].valid=true — valid:true, zero issues (run after artifact creation and re-run after evidence/ticks below)
- [x] 8.3 Confirm all evidence files exist with file+line-anchored citations and all gates ticked with verified evidence only — confirmed: evidence/mcp-router.md, evidence/goose-docs.md, evidence/prime-agent.md, evidence/realtime-frontend.md; every tick above cites its evidence file and gate
