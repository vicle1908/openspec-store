# Proposal: verify-npm-audit-remediation

## Why
A workspace-wide npm/bun/pnpm audit remediation was executed across mcp-router, goose-docs, prime-agent, and realtime/frontend on 2026-09-03. The upgrades, dependency replacements, and test migrations are uncommitted working-tree changes with claimed (but not independently re-verified) audit/build/test outcomes. Before commit, an end-to-end verification pass is required to catch regressions introduced by the remediation itself, and the work must be governed under the OpenSpec workflow with concrete operational evidence.

## What Changes
- Re-verify, per repository, that: (a) the package-manager audit reports the expected residual count (0 except documented unpatched-upstream findings), (b) builds/typechecks/tests relevant to the changed dependency surfaces pass, (c) the changes are confined to dependency manifests, lockfiles, and the migration-touched source files.
- Fix any bug surfaced by the verification pass (audit regressions, broken tests, install failures) within the remediation's scope.
- Record evidence in this change and leave the change active until all gates hold.

## Scope
In-scope repos and their verification commands:
- mcp-router (pnpm 10.22.0): `pnpm audit --json` (expect 3 high, all unpatched upstream: image-size x2, extract-zip), CLI build, Electron typecheck, electron-forge version, frozen-lockfile install.
- goose-docs/oidc-proxy (npm): `npm audit` (expect 0), `npm test` (expect 11/11 passing via @cloudflare/vitest-plugin + @msw/cloudflare).
- goose-docs/documentation (npm): `npm audit` (expect only image-size chain, uuid eliminated), docs build.
- goose-docs/services/ask-ai-bot (bun): `bun audit` (expect 0), `bun run build`.
- goose-docs/ui (pnpm): `pnpm audit` (expect 1 high unpatched upstream extract-zip), workspace install.
- prime-agent (npm): `npm audit` (expect 0), focused tools-manager test.
- realtime/frontend (npm): `npm audit` (expect 0), build.
- hermes-webui: no changes made; nothing to verify beyond the recorded 0-vulnerability isolated audit.

Out of scope: upgrading the unpatched upstream advisories (image-size, extract-zip in forge/appdmg chains) — no patched version exists; full project-wide test/lint suites; committing or pushing (owner decision).

## Expected Outcome
All verification gates green (or explicitly documented as unpatched-upstream residuals), bugs found during verification fixed, and evidence recorded under this change's evidence directory, making the remediation safe for the owner to review and commit.
