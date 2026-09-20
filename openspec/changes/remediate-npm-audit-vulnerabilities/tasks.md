# Tasks

## 1. Workstation Root Manifest Peer Alignment (`~/package.json`)

- [x] 1.1 Update `newman` to `^6.2.2` and update the `adm-zip` override to `0.6.1` in `/Users/androidteam/package.json`
- [x] 1.2 Run `npm install` in `/Users/androidteam` and verify dependency resolution succeeds without `ERESOLVE` errors or `--legacy-peer-deps`
- [x] 1.3 Verify `npm audit` and `npm outdated` in `/Users/androidteam` exit cleanly with 0 vulnerabilities reported

## 2. MCP Router Transitive Vulnerability Remediation (`mcp-router`)

- [x] 2.1 Update `pnpm.overrides` in `/Users/androidteam/Developer/mcp-router/package.json` with `"smol-toml@<=1.7.0": ">=1.7.1"`, `"fflate@>=0.8.0 <0.8.3": ">=0.8.3"`, and `"fflate@>=0.4.5 <0.4.9": ">=0.4.9"`
- [x] 2.2 Run `pnpm install` in `/Users/androidteam/Developer/mcp-router` and verify `pnpm-lock.yaml` updates cleanly
- [x] 2.3 Verify `mcp-router` build and typecheck (`pnpm --filter @mcp_router/electron run typecheck` and `turbo run build`) pass with overridden dependencies
- [x] 2.4 Verify `pnpm audit` in `mcp-router` confirms exactly 4 remaining advisories, all belonging to unpatched upstream residuals

## 3. Realtime Frontend Vulnerability Remediation (`realtime/frontend`)

- [x] 3.1 Add `overrides` in `/Users/androidteam/Developer/realtime/frontend/package.json` for `js-yaml` (`>=4.3.2`) and `fflate` (`>=0.8.3`)
- [x] 3.2 Update devDependencies in `/Users/androidteam/Developer/realtime/frontend/package.json` for `vitest`, `@vitest/coverage-v8`, and `@vitest/ui` to `^4.1.11`
- [x] 3.3 Run `npm install` in `/Users/androidteam/Developer/realtime/frontend` and verify `package-lock.json` updates cleanly
- [x] 3.4 Verify `npm audit` in `/Users/androidteam/Developer/realtime/frontend` reports 0 vulnerabilities
- [x] 3.5 Verify build or typecheck succeeds (`npm run build` or `npm run type-check`) in `/Users/androidteam/Developer/realtime/frontend`

## 4. Prime Agent Workspace Vitest Upgrade (`prime-agent`)

- [x] 4.1 Update `"vitest": "^4.1.11"` in `packages/agent/package.json`, `packages/ai/package.json`, and `packages/coding-agent/package.json` in `/Users/androidteam/Developer/prime-agent`
- [x] 4.2 Run `npm install` in `/Users/androidteam/Developer/prime-agent` (avoiding destructive `npm audit fix`) and verify `package-lock.json` updates cleanly
- [x] 4.3 Run `npm run check` in `/Users/androidteam/Developer/prime-agent` to verify TypeScript, Biome, and installer checks pass
- [x] 4.4 Verify `npm audit` in `/Users/androidteam/Developer/prime-agent` reports 0 vulnerabilities

## 5. Verification and Evidence Recording

- [x] 5.1 Re-run audit commands in fresh processes across all four targets (`~`, `mcp-router`, `realtime/frontend`, `prime-agent`) and capture exit codes and output
- [x] 5.2 Confirm no unintended `package-lock.json` exists in `mcp-router` and no `pnpm-lock.yaml` exists in `realtime/frontend`
- [x] 5.3 Compile residual advisory inventory recording the 4 unpatched `mcp-router` advisories (`image-size` x 2, `extract-zip` x 2) with package names, versions, and `patched: <0.0.0` markers
