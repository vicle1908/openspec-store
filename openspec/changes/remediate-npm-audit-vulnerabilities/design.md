# Design

## Context

See `proposal.md` for motivation and vulnerability counts across repositories.

The workstation environment hosts four distinct Node.js management contexts:
1. **Workstation Root (`/Users/androidteam/package.json`)**: Managed via `npm`. Contains developer CLI tools (`gitnexus`, `newman`, `newman-reporter-htmlextra`, `pyright`, `yaml-language-server`). The lockfile is currently locked to `newman@4.6.1`, but `newman-reporter-htmlextra` is already declared as `^1.23.1`, which requires `peer newman@"^6.0.0"`. This creates an `ERESOLVE` conflict that blocks `npm audit fix`, `npm install`, and `npm outdated`. Furthermore, `overrides` currently pins `"adm-zip": "0.6.0"`, which is within the vulnerable range `<0.6.1`.
2. **MCP Router (`/Users/androidteam/Developer/mcp-router`)**: Managed strictly via `pnpm` (`packageManager: pnpm@10.22.0`). No `package-lock.json` is permitted. Houses an Electron desktop application and multiple MCP tool services. Overrides are managed via `pnpm.overrides` in `package.json`. Currently reports exactly 7 vulnerabilities in `pnpm audit`:
   - `smol-toml` (high): `<=1.7.0`, patched in `>=1.7.1` (current override is outdated `<1.6.1`)
   - `fflate` (moderate): 2 paths (`apps/electron>@anthropic-ai/dxt` and `apps/electron>posthog-js`), patched in `>=0.8.3` and `>=0.4.9`
   - `image-size` (high): 2 advisories for ICNS and JXL/HEIF infinite loops; both have `patched: <0.0.0` (unpatched upstream residual)
   - `extract-zip` (high): 2 advisories for symlink path traversal and arbitrary file write; both have `patched: <0.0.0` (unpatched upstream residual)
3. **Realtime Frontend (`/Users/androidteam/Developer/realtime/frontend`)**: Managed via `npm` with its own `package-lock.json`. (Running `pnpm audit` here inadvertently audits `/Users/androidteam/pnpm-lock.yaml` because `realtime/frontend` has no `pnpm-lock.yaml`.) `npm audit` in `realtime/frontend` reports 6 vulnerabilities:
   - `js-yaml` (high): `4.0.0 - 4.3.1`, patched in `>=4.3.2`
   - `fflate` (moderate): `0.8.0 - 0.8.2`, patched in `>=0.8.3`
   - `vitest`, `@vitest/mocker`, `@vitest/coverage-v8`, `@vitest/ui` (moderate): `2.1.0-beta.1 - 4.1.10`, patched in `>=4.1.11`
4. **Prime Agent (`/Users/androidteam/Developer/prime-agent`)**: Multi-package workspace managed via `npm`. Reports 2 moderate vulnerabilities in `@vitest/mocker` / `vitest` across `packages/agent`, `packages/ai`, and `packages/coding-agent`. A dry-run of `npm audit fix` attempts to downgrade 67 packages (including TypeScript and Biome); therefore, manual package.json bumps must be used.

## Goals / Non-Goals

**Goals:**
- Resolve the `ERESOLVE` deadlock in `~/package.json` by upgrading `newman` to `^6.2.2` and updating `adm-zip` override to `0.6.1`.
- Update `pnpm.overrides` in `mcp-router` to resolve `smol-toml` and `fflate`, leaving only the 4 unpatched upstream residuals.
- Eliminate all 6 vulnerabilities in `realtime/frontend` by adding `overrides` for `js-yaml` and `fflate` and bumping `vitest` packages to `^4.1.11`.
- Eliminate the 2 vulnerabilities in `prime-agent` by directly bumping `vitest` in the three workspace package.json files.
- Maintain repository package-manager invariants: `mcp-router` stays pnpm-only; `realtime/frontend` and `prime-agent` stay npm-managed.

**Non-Goals:**
- Attempting monkey-patching or forking `image-size` or `extract-zip` in `mcp-router` while upstream maintainers have no published patch (`patched: <0.0.0`).
- Running `npm audit fix` in `prime-agent` that causes cascading package downgrades.
- Converting `realtime/frontend` to pnpm or generating `pnpm-lock.yaml` there.

## Decisions

### Decision 1: Upgrade Newman to v6 in `~/package.json` and Correct `adm-zip` Override
- **Context**: `newman@4.6.1` creates an `ERESOLVE` peer deadlock with `newman-reporter-htmlextra@^1.23.1` (which requires `peer newman@"^6.0.0"`). Transitive dependencies of Newman v4 account for 28 vulnerabilities. Additionally, `overrides` pins `"adm-zip": "0.6.0"`, which is vulnerable.
- **Decision**: Update `~/package.json`:
  ```json
  "newman": "^6.2.2",
  "newman-reporter-htmlextra": "^1.23.1"
  ```
  and in `overrides`:
  ```json
  "adm-zip": "0.6.1"
  ```
- **Rationale**: Aligns peer dependencies cleanly, eliminates all 28 Newman v4-linked vulnerabilities, and restores working `npm audit` and `npm outdated` in `~`.

### Decision 2: Refine `pnpm.overrides` in `mcp-router`
- **Context**: `mcp-router` already has extensive overrides in `package.json`, but `smol-toml` uses an outdated override `"smol-toml@<1.6.1": ">=1.6.1"` (the new advisory affects `<=1.7.0`), and `fflate` has no override.
- **Decision**: Update `pnpm.overrides` in `mcp-router/package.json`:
  - `"smol-toml@<=1.7.0": ">=1.7.1"` (replaces `<1.6.1`)
  - `"fflate@>=0.8.0 <0.8.3": ">=0.8.3"`
  - `"fflate@>=0.4.5 <0.4.9": ">=0.4.9"`
- **Rationale**: Directly resolves the 3 fixable advisories (`smol-toml` and both `fflate` paths) via pnpm's native override mechanism without modifying direct dependencies.

### Decision 3: Formally Document Unpatched Residuals in `mcp-router`
- **Context**: `image-size` (2 advisories) and `extract-zip` (2 advisories) have `patched: <0.0.0`. They are deep transitive dependencies of `@electron-forge/maker-dmg` and `@electron-forge/cli`.
- **Decision**: Document these 4 advisories in verification evidence as unpatched upstream residuals, noting their exact versions, paths, and `patched: <0.0.0` markers. Do not attempt speculative version overrides that could break Electron packaging.
- **Rationale**: Matches the established OpenSpec `verify-npm-audit-remediation` pattern: identify by package, version, and no-fix marker.

### Decision 4: Remediate `realtime/frontend` via npm Overrides and devDependencies Bump
- **Context**: `realtime/frontend` has `package-lock.json` and is tested via `npm run test:ci`. `npm audit` reports 6 vulnerabilities: `js-yaml` (high), `fflate` (moderate), and 4 in `vitest` packages.
- **Decision**:
  - Add to `realtime/frontend/package.json`:
    ```json
    "overrides": {
      "js-yaml": ">=4.3.2",
      "fflate": ">=0.8.3"
    }
    ```
  - Bump devDependencies:
    ```json
    "vitest": "^4.1.11",
    "@vitest/coverage-v8": "^4.1.11",
    "@vitest/ui": "^4.1.11"
    ```
  - Run `npm install` to update `package-lock.json`.
- **Rationale**: Cleanly resolves all 6 vulnerabilities in `realtime/frontend` with zero remaining advisories.

### Decision 5: Non-Destructive Vitest Bump in `prime-agent`
- **Context**: `npm audit fix` in `prime-agent` attempts to downgrade 67 packages across the workspace.
- **Decision**: Directly update `"vitest": "^4.1.11"` in:
  - `packages/agent/package.json`
  - `packages/ai/package.json`
  - `packages/coding-agent/package.json`
  Then run `npm install` (NOT `npm audit fix`).
- **Rationale**: Surgical bump resolves the 2 `@vitest/mocker` vulnerabilities without touching any other workspace dependencies.

## Risks / Trade-offs

- **Newman v6 Breaking Changes**: Newman v6 dropped older Node versions and changed some CLI options. *Mitigation*: Verify `newman --version` runs cleanly and check that any CI scripts use standard `newman run` syntax.
- **Transitive Override Incompatibility in `mcp-router`**: Overriding `fflate` and `smol-toml` could theoretically affect parser behavior. *Mitigation*: Run `pnpm --filter @mcp_router/electron run typecheck` and `turbo run build` immediately to verify compilation.
- **Residual Advisories in `mcp-router`**: 4 high vulnerabilities in `image-size` and `extract-zip` remain active. *Mitigation*: These are build-time tools (`@electron-forge`), not runtime production code. They are documented with `patched: <0.0.0` and will be resolved when Electron Forge updates its dependency tree.
