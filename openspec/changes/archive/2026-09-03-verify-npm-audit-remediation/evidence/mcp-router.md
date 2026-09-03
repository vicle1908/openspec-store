# Evidence — mcp-router verification (gates 1.1–1.6)

Executor: VerifyMcpRouter worker (transcript: history://VerifyMcpRouter; raw logs /tmp/mcp-router-audit.json, /tmp/mcp-cli-build.log, /tmp/mcp-electron-typecheck.log, /tmp/mcp-forge-version.log, /tmp/mcp-frozen-install.log).
Environment: node v22.23.2, pnpm 10.22.0 (repo pin; all gates run with 10.22.0, not the 11.23.0 on PATH). Repo HEAD 64086a74cf0766d72ea9d0aef3038f21861bd596.

## Gate 1.1 — pnpm audit --json
- exit 1 (expected: documented unpatched highs only)
- metadata.vulnerabilities = {info:0, low:0, moderate:0, high:3, critical:0}
- Exactly 3 advisories, each patched_versions `<0.0.0` (no-fix marker), matching documented residuals: image-size ×2, extract-zip ×1.
- Verdict: PASS

## Gate 1.2 — no package-lock.json
- `/usr/bin/find /Users/androidteam/Developer/mcp-router -name package-lock.json` → only hit: node_modules/minipass-sized/package-lock.json (vendored inside published dependency tarball; gitignored via .gitignore:2; untracked; dated Aug 5 2026, predates remediation). Zero workspace/root npm lockfiles. git ls-files cross-check clean.
- Verdict: PASS (pnpm-only workflow preserved)

## Gate 1.3 — webpack-dev-server override (programmatic pnpm-lock.yaml readback)
- pnpm-lock.yaml line 10: `webpack-dev-server@<=5.2.5: 5.2.6`
- pnpm-lock.yaml line 6737: snapshot `webpack-dev-server@5.2.6`; line 6739: `engines: {node: ">= 18.12.0"}`; consumer entry line 7248 references 5.2.6. Single resolved version repo-wide.
- Verdict: PASS (patched 5.x line; no Node-22 engine conflict)

## Gate 1.4 — builds
- `pnpm --filter @mcp_router/cli run build` → exit 0 (tsc --build, no errors) — log /tmp/mcp-cli-build.log
- `pnpm --filter @mcp_router/electron run typecheck` → exit 0 — log /tmp/mcp-electron-typecheck.log
- Verdict: PASS

## Gate 1.5 — forge version + frozen install
- `pnpm --filter @mcp_router/electron exec electron-forge --version` → exit 0, output 7.11.2 — log /tmp/mcp-forge-version.log
- `pnpm install --frozen-lockfile` → exit 0 (lockfile/config consistent) — log /tmp/mcp-frozen-install.log
- Verdict: PASS

## Gate 1.6 — this evidence file.

## Deltas vs remediation session
None: 3-high audit total and identities, resolved override, and all build gates reproduce the remediation outcomes exactly. Working tree left untouched (pre-existing remediation-era modifications + untracked churn, no commits).
