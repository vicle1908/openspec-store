# npm-audit-remediation Specification

## Purpose
Governs remediation contracts, dependency upgrade matrices, peer-resolution conflict reconciliation, and unpatched upstream residual tracking across workstation and repository package manifests.

## Requirements

### Requirement: Workstation Root Manifest Peer Conflict Resolution
The workstation root package manifest (`/Users/androidteam/package.json`) SHALL resolve all peer dependency conflicts and version deadlocks between `newman` and its reporter plugins by pinning semver-compatible major versions, updating overrides to non-vulnerable thresholds, and ensuring `npm audit` and `npm outdated` exit without `ERESOLVE` errors.

#### Scenario: newman and htmlextra peer alignment
- **WHEN** `newman` is updated to `^6.2.2` and `adm-zip` override is updated to `0.6.1` in `/Users/androidteam/package.json`
- **THEN** npm installs cleanly without `--force` or `--legacy-peer-deps`, and peer dependency resolution succeeds

#### Scenario: npm audit execution after upgrade
- **WHEN** `npm audit` is executed in `/Users/androidteam`
- **THEN** the command evaluates the dependency graph without `ERESOLVE` errors, and the 28 vulnerabilities associated with the Newman v4 dependency chain are resolved

### Requirement: Transitive Vulnerability Elimination via Package Overrides
Node.js package manifests across `mcp-router` and `realtime/frontend` SHALL declare explicit version overrides for transitive dependencies with published security advisories where parent packages have not released updated dependency ranges.

#### Scenario: transitive overrides applied in mcp-router
- **WHEN** `mcp-router` specifies `pnpm.overrides` for `smol-toml` (`<=1.7.0` -> `>=1.7.1`) and `fflate` (`>=0.8.0 <0.8.3` -> `>=0.8.3`, `>=0.4.5 <0.4.9` -> `>=0.4.9`)
- **THEN** `pnpm install` resolves only versions meeting or exceeding the patched version thresholds, resolving 3 out of 7 reported vulnerabilities

#### Scenario: transitive overrides applied in realtime frontend
- **WHEN** `realtime/frontend` specifies `overrides` in `package.json` for `js-yaml` (`>=4.3.2`) and `fflate` (`>=0.8.3`)
- **THEN** `npm install` binds the override versions throughout the dependency tree, resolving the high-severity `js-yaml` advisory and moderate `fflate` advisory

### Requirement: Test Runner Security Alignment
The `prime-agent` and `realtime/frontend` workspaces SHALL pin test framework dependencies (`vitest` and `@vitest/mocker`) across all workspace packages to versions containing security patches for arbitrary file read and path traversal vulnerabilities without downgrading unrelated tooling packages.

#### Scenario: vitest path traversal fix in prime-agent
- **WHEN** `vitest` is updated to `^4.1.11` in `packages/agent/package.json`, `packages/ai/package.json`, and `packages/coding-agent/package.json`
- **THEN** `npm audit` in `prime-agent` reports zero vulnerabilities, and workspace test suites execute normally

#### Scenario: vitest path traversal fix in realtime frontend
- **WHEN** `vitest`, `@vitest/coverage-v8`, and `@vitest/ui` are updated to `^4.1.11` in `realtime/frontend/package.json`
- **THEN** `npm audit` confirms the `@vitest/mocker` path traversal vulnerability is eliminated

### Requirement: Unpatched Upstream Residual Documentation
When a package manager audit reports vulnerabilities for which no upstream patched version exists (`patched: <0.0.0`), the remediation SHALL record verifiable evidence identifying each residual advisory rather than attempting unvetted monkey-patches.

#### Scenario: unpatched residuals identified in mcp-router
- **WHEN** `pnpm audit` is executed in `mcp-router` after applying overrides
- **THEN** exactly 4 residual advisories are reported (`image-size` x 2, `extract-zip` x 2), each carrying `patched: <0.0.0` with no available upstream fix
