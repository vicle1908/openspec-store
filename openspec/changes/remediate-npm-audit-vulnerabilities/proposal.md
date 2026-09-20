# Proposal

## Why

Multiple Node.js package manifests across the workstation and repository tree (`/Users/androidteam/package.json`, `mcp-router`, `realtime/frontend`, and `prime-agent`) contain active security advisories totaling 43 reported vulnerabilities across targets, while an `ERESOLVE` peer dependency deadlock in `~/package.json` prevents `npm audit fix` and clean package updates. Remediating these vulnerabilities now eliminates critical prototype pollution, code injection, and DoS risks while unblocking automated dependency updates across all affected environments.

## What Changes

- **Home Directory (`~/package.json`)**:
  - Upgrade `newman` from `^4.6.1` to `^6.2.2` (**BREAKING** CLI/runtime major version bump for Postman collection execution).
  - Resolve the `ERESOLVE` peer dependency conflict with `newman-reporter-htmlextra@^1.23.1` (which requires `peer newman@"^6.0.0"`).
  - Update the `adm-zip` entry in `overrides` from `0.6.0` (vulnerable to arbitrary file overwrite and DoS) to `0.6.1` (patched).
- **MCP Router (`~/Developer/mcp-router`)**:
  - Update `pnpm.overrides` in `package.json` to resolve active advisories:
    - `"smol-toml@<=1.7.0": ">=1.7.1"` (replaces outdated `<1.6.1` override)
    - `"fflate@>=0.8.0 <0.8.3": ">=0.8.3"`
    - `"fflate@>=0.4.5 <0.4.9": ">=0.4.9"`
  - Re-run `pnpm install` and verify build and typecheck pass.
  - Formally record the 4 unpatched upstream residuals in verification evidence:
    - `image-size <=2.0.2` (2 high advisories: ICNS parser infinite loop, JXL/HEIF infinite loop; patched `<0.0.0`)
    - `extract-zip <=2.0.1` (2 high advisories: symlink path traversal, arbitrary file writes; patched `<0.0.0`)
- **Realtime Frontend (`~/Developer/realtime/frontend`)**:
  - Add `overrides` in `package.json` for `js-yaml` (`>=4.3.2`) and `fflate` (`>=0.8.3`).
  - Upgrade `vitest`, `@vitest/coverage-v8`, and `@vitest/ui` to `^4.1.11`.
  - Re-run `npm install` and verify `npm audit` reports zero vulnerabilities.
- **Prime Agent (`~/Developer/prime-agent`)**:
  - Upgrade `vitest` to `^4.1.11` in `packages/agent/package.json`, `packages/ai/package.json`, and `packages/coding-agent/package.json` to eliminate the `@vitest/mocker` redirect mock path traversal advisory (GHSA-82fw-gwwq-j7x9).
  - Re-run targeted `npm install` (avoiding destructive `npm audit fix` which downgrades workspace packages).
- **Non-Goals**:
  - Forking or monkey-patching `image-size` or `extract-zip` while upstream maintainers have not released a patched version (`patched: <0.0.0`).
  - Running global or aggressive `npm audit fix` in `prime-agent` that downgrades TypeScript, Biome, or AWS SDK packages.
  - Adding or modifying pnpm files in `realtime/frontend` (which is an npm-managed repository with its own `package-lock.json`).

## Capabilities

### New Capabilities
- `npm-audit-remediation`: Governs remediation contracts, dependency upgrade matrices, peer-resolution conflict reconciliation, and unpatched upstream residual tracking across workstation and repository package manifests.

### Modified Capabilities
- `verify-npm-audit-remediation`: Extends the verification gate criteria to cover the 2026-09-20 audit baseline across all 4 targets, verifying clean audit exits, exact unpatched residual markers (`patched: <0.0.0`), and repository-specific package manager invariants.

## Impact

- **Affected Ownership Boundaries**:
  - Workstation global environment: `/Users/androidteam/package.json`
  - MCP infrastructure: `/Users/androidteam/Developer/mcp-router`
  - Realtime services: `/Users/androidteam/Developer/realtime/frontend`
  - Coding agent platform: `/Users/androidteam/Developer/prime-agent`
- **Breaking Changes**:
  - `newman@6.2.2` introduces semver-major changes over `v4.6.1`. Existing test scripts or collections relying on deprecated Newman v4 internal APIs or node runtime flags must be verified against Newman v6.
- **User-Facing / Operational Impact**:
  - Resolves 39 out of 43 security advisories across the workstation, with the remaining 4 classified and documented as unpatched upstream residuals.
  - Restores working `npm audit` / `npm outdated` execution in `~`.
