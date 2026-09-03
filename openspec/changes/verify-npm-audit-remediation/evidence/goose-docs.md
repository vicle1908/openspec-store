# Evidence — goose-docs verification (gates 2.1–2.4, 3.1–3.4, 4.1–4.4, 5.1–5.3)

Executor: VerifyGooseDocs worker (sole writer for goose-docs; transcript: history://VerifyGooseDocs; raw outputs at /tmp: oidc-audit.json, oidc-test.out, oidc-litcheck2.out, oidc-barescan.out, docs-audit.json, docs-audit-analysis.out, docs-chain2.out, docs-uuid.out, docs-imgsz.out, docs-build.out, bot-audit.out, bot-lock-check2.out, bot-build.out, ui-audit.json, ui-audit-final.out, ui-install.out). Parent additionally ran the sockjs/uuid CJS runtime smoke (gate 3.4 addendum).

## oidc-proxy (npm)
- 2.1 `npm audit --json` → exit 0; totals all 0; deps prod 1 / dev 212 / optional 87. PASS
- 2.2 `npm test` → exit 0; RUN v4.1.11 — Test Files 1 passed (1); Tests 11 passed (11); Duration 3.21s. PASS
- 2.3 Fresh HEAD/worktree comparison PASS. Worktree wrangler.toml:22 and HEAD wrangler.toml:22 both use `UPSTREAM_URL = "https://api.anthropic.com"`. The test harness is a deliberate migration, not a HEAD/worktree identity claim: HEAD test/index.test.js contains zero `api.anthropic.com` literals, while the worktree contains two, at line 93 (new MSW handler) and line 119 (test env). The `testEnv()` block also contains a single synthetic credential-shaped fixture (test/index.test.js:115-126), classified as a false positive rather than a live credential. Exhaustive host scan (worktree + HEAD): every https:// host ∈ {api.anthropic.com, token.actions.githubusercontent.com (== wrangler OIDC_ISSUER), proxy.example.com, evil.example.com (RFC2606 fixtures)} — zero foreign hosts, zero corrupted tokens. PASS
- 2.4 This evidence file. PASS

## documentation (npm)
- 3.1 `npm audit --json` → exit 1 (expected); totals: high 18, all else 0. 18 identities: image-size + 17 @docusaurus/* packages, ALL fixAvailable:false. All 18 chain to image-size@2.0.2 (via @docusaurus/core@3.10.2 -> @docusaurus/mdx-loader@3.10.2 -> image-size@2.0.2; advisories GHSA-w3rx-r6r6-pgpr ICNS infinite-loop DoS + GHSA-5p2g-fcmc-qvqq JXL/HEIF infinite-loop DoS, both range <=2.0.2, CVSS 7.5). uuid advisories ABSENT. PASS
- 3.2 `npm ls uuid --all` → exit 0; @docusaurus/core@3.10.2 -> webpack-dev-server@5.2.6 -> sockjs@0.3.24 -> uuid@11.1.1 overridden; package.json overrides block: qs 6.16.0, serialize-javascript 7.1.1, uuid 11.1.1. PASS
- 3.3 `npm run build` → exit 0; [SUCCESS] Generated static files in "build"; 169 markdown files exported. Pre-existing broken-anchor warning on /docs/guides/remote-goose-server (content-level; git diff of documentation = package.json overrides + package-lock.json only, no content files touched). PASS
- 3.4 This evidence file. PASS
- ADDENDUM (runtime smoke of the overridden chain — production build does not load sockjs, which is webpack-dev-server/dev-path only): `node -e "require('sockjs'); const u=require('uuid'); ..."` run by parent in documentation/ → exit 0: `sockjs loads OK; typeof uuid.v4 = function; resolved uuid: 11.1.1; sockjs: 0.3.24`. Proves sockjs's `require('uuid').v4` call surface is satisfied by the overridden 11.1.1. PASS

## services/ask-ai-bot (bun)
- 4.1 `bun audit` → exit 0; "No vulnerabilities found (checked 130 packages)". PASS
- 4.2 Programmatic bun.lock text scan: `@discordjs/rest@2.6.0` occurrences = 0; `undici@6.21.3` occurrences = 0; top-level `@discordjs/rest@2.6.3` (L48) and `undici@6.28.0` (L276) each exactly 1. Exhaustive token scan: all rest version tokens = ['2.6.3'], all undici tokens = ['6.28.0']. Root deps + package.json overrides consistent. PASS
- 4.3 `bun run build` → exit 0; discraft build — Bundled 22 modules in 34ms; index.js 31.0 KB; [success] Output ./dist. PASS
- 4.4 This evidence file. PASS

## ui workspace (pnpm)
- 5.1 `pnpm audit --json` → exit 1 (expected); exactly 1 advisory: extract-zip 2.0.1 "unvalidated symlink path traversal", high, vulnerable_versions <=2.0.1, patched_versions None (no fix), 38 dependency paths (desktop > @electron-forge/cli > ... > @electron/packager > extract-zip). PASS
- 5.2 `pnpm install --frozen-lockfile` → exit 0; all 9 workspace projects; Done in 263ms (pnpm v11.23.0, node v22.23.2). Non-fatal pre-existing warnings: desktop engine wants node ^24.10.0 (environmental; git diff of ui/desktop/package.json touches zero engines lines); 4 optional goose-binary cross-OS platform mismatches. PASS
- 5.3 This evidence file. PASS

## Unpatched upstream residuals (no-fix markers cited)
- image-size 2.0.2 @ documentation — GHSA-w3rx-r6r6-pgpr, GHSA-5p2g-fcmc-qvqq; fixAvailable:false ×18
- extract-zip 2.0.1 @ ui (desktop) — advisory 1139346; patched_versions:None

## Fixes made
None required in this repo — no gate regressed.

## Deltas vs remediation session
None — every gate reproduces the recorded outcome exactly.
