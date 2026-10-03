# Proposal: Workspace Dependency Modernization and Audit Remediation

## Why
Security vulnerabilities and dependency drift accumulated across workspace packages (`/Users/androidteam/package.json`, `platform/mcp-router`, `tdt/realtime/frontend`, `platform/prime-agent`), exposing projects to denial-of-service and prototype pollution risks. Remediating these vulnerabilities and upgrading dependencies to the latest available compatible releases ensures supply-chain hygiene, establishes lockstep parity across package managers, and records durable evidence of unpatchable upstream residuals.

## What Changes
- **Home CLI Tooling (`/Users/androidteam/package.json`)**: Upgraded `newman` to `^6.2.2`, `newman-reporter-htmlextra` to `^1.23.1`, and modernized overrides (`sharp` 0.35.5, `jose` 6.2.12, `csv-parse` 7.0.3) while removing broken `@faker-js/faker` v10 override to protect Newman runtime execution.
- **TDT Realtime Frontend (`tdt/realtime/frontend`)**: Upgraded `react` and `react-dom` to `19.3.0`, `axios` to `^1.20.0`, `@tanstack/react-query` to `^5.104.1`, `ably` to `^2.29.0`, `react-router-dom` to `^7.18.4`, `@reduxjs/toolkit` to `^2.13.0`, `fast-check` to `^4.10.2`, `framer-motion` to `^12.43.0`, and established strict dual overrides (`dompurify >=3.4.16`, `brace-expansion >=5.0.12`) across both `overrides` and `pnpm.overrides`.
- **MCP Router Platform (`platform/mcp-router`)**: Upgraded root devDependencies (`prettier` 3.9.9, `@types/node` 26.6.4, `@types/react` 19.3.0, `@typescript-eslint` 8.71.0, `eslint` 10.12.0, `knip` 6.39.0, `turbo` 2.11.7) and workspace packages (`@modelcontextprotocol/sdk` ^1.32.0, Radix UI suite, `@codemirror/*`, `zustand` 5.0.15, `semver` 7.8.5, `posthog-js` 1.435.8), while pinning security overrides (`fast-uri`, `ip-address`, `hono`, `brace-expansion`, `undici`, `image-size`) under `pnpm.overrides` with zero `package-lock.json` generation.
- **Prime Agent Platform (`platform/prime-agent`)**: Upgraded `@anthropic-ai/sandbox-runtime` to `^0.0.77` across root and `packages/coding-agent/examples/extensions/sandbox`, `concurrently` to `^10.0.5`, `tsx` to `^4.23.15`, and `get-east-asian-width` to `^1.7.0`, with root security overrides (`ip-address >=10.7.1`, `brace-expansion >=5.0.12`).
- **Residual Evidence Accounting**: Formally document unpatched upstream residuals (`http-cache-semantics <=4.2.0`, `extract-zip <=2.0.1`, `node-forge <=1.4.0`, `basic-ftp <=6.2.0`, `braces <=3.0.3`) where upstream patches are absent (`<0.0.0`).

## Capabilities

### Modified Capabilities
- `npm-audit-remediation`: Extend requirements to mandate React 19.3 parity, dual-override synchronization across npm and pnpm, unconstrained latest semver upgrades, and explicit sandbox runtime deduplication across workspace packages.

## Impact
- **Affected Packages**:
  - `/Users/androidteam/package.json`
  - `/Users/androidteam/Developer/tdt/realtime/frontend/package.json`
  - `/Users/androidteam/Developer/platform/mcp-router/package.json` and child workspaces
  - `/Users/androidteam/Developer/platform/prime-agent/package.json` and child workspaces
- **Zero Breaking Regressions**: All verification gates (`npm run check` in prime-agent, `pnpm run build` & typecheck in mcp-router, property tests & typecheck in realtime/frontend, CLI executions in home) pass with status 0.
