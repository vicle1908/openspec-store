# Spec Delta: npm-audit-remediation

## MODIFIED Requirements

### Requirement: Transitive Vulnerability Elimination via Package Overrides
Node.js package manifests across `mcp-router`, `prime-agent`, and `realtime/frontend` SHALL declare explicit version overrides for transitive dependencies with published security advisories where parent packages have not released updated dependency ranges. In dual-manager environments like `realtime/frontend`, overrides MUST be synchronized across both `overrides` and `pnpm.overrides` to ensure deterministic resolution.

#### Scenario: transitive overrides applied in mcp-router
- **WHEN** `mcp-router` specifies `pnpm.overrides` for `smol-toml` (`<=1.7.0` -> `>=1.7.1`) and `fflate` (`>=0.8.0 <0.8.3` -> `>=0.8.3`, `>=0.4.5 <0.4.9` -> `>=0.4.9`)
- **THEN** `pnpm install` resolves only versions meeting or exceeding the patched version thresholds, resolving 3 out of 7 reported vulnerabilities

#### Scenario: transitive overrides applied in realtime frontend
- **WHEN** `realtime/frontend` specifies `overrides` in `package.json` for `js-yaml` (`>=4.3.2`) and `fflate` (`>=0.8.3`)
- **THEN** `npm install` binds the override versions throughout the dependency tree, resolving the high-severity `js-yaml` advisory and moderate `fflate` advisory

#### Scenario: dual-override parity in realtime frontend
- **WHEN** security overrides are declared in `realtime/frontend/package.json`
- **THEN** both `overrides` and `pnpm.overrides` contain identical version pins for `dompurify` (`>=3.4.16`) and `brace-expansion` (`>=5.0.12`), eliminating DOM XSS and regex DoS advisories across both npm CI and pnpm workspaces

#### Scenario: prime-agent security overrides and extension deduplication
- **WHEN** overrides are added to `platform/prime-agent/package.json`
- **THEN** `ip-address` resolves to `>=10.7.1` and `brace-expansion` resolves to `>=5.0.12`, while `@anthropic-ai/sandbox-runtime` in root devDependencies and `packages/coding-agent/examples/extensions/sandbox` are aligned to `^0.0.77` without duplicate older dependency trees

### Requirement: Unpatched Upstream Residual Documentation
When a package manager audit reports vulnerabilities for which no upstream patched version exists (`patched: <0.0.0`), the remediation SHALL record verifiable evidence identifying each residual advisory by package name, advisory ID, and dependency chain rather than attempting unvetted monkey-patches or breaking downgrades.

#### Scenario: unpatched residuals identified in mcp-router
- **WHEN** `pnpm audit` is executed in `mcp-router` after applying overrides
- **THEN** exactly 4 residual advisories are reported (`image-size` x 2, `extract-zip` x 2), each carrying `patched: <0.0.0` with no available upstream fix

#### Scenario: unpatched residuals identified across workspace
- **WHEN** audit commands are executed post-remediation
- **THEN** residual advisories are documented with no-fix markers: `http-cache-semantics <=4.2.0` (in `realtime/frontend` and `mcp-router`), `extract-zip <=2.0.1` (in `mcp-router`), `node-forge <=1.4.0` (in `mcp-router`, `prime-agent`, and `~`), `basic-ftp <=6.2.0` (in `prime-agent`), and `braces <=3.0.3` (in `mcp-router`, `prime-agent`, and `~`)

## ADDED Requirements

### Requirement: React 19.3 Ecosystem Parity
Client frontend applications SHALL upgrade to React 19.3.0 and corresponding type definitions without breaking rendering, router integration, or property test suites.

#### Scenario: realtime frontend react 19.3 upgrade
- **WHEN** `realtime/frontend/package.json` is updated to `react@19.3.0`, `react-dom@19.3.0`, `@types/react@^19.3.0`, and `@types/react-dom@^19.3.0`
- **THEN** `npm run type-check`, property-based test suites, and production build succeed with exit code 0
