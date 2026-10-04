# Spec Delta: npm-audit-remediation

## MODIFIED Requirements

### Requirement: Transitive Vulnerability Elimination via Package Overrides
Node.js package manifests across `mcp-router`, `prime-agent`, `realtime/frontend`, and the
relocated workstation toolchain (`~/.local/share/home-toolchain`) SHALL declare explicit version
overrides for transitive dependencies with published security advisories where parent packages
have not released updated dependency ranges, and SHALL additionally raise any transitive
dependency that remains behind its latest published version while its parent's declared range
already permits the newer version. In dual-manager environments like `realtime/frontend`,
overrides MUST be synchronized across both `overrides` and `pnpm.overrides` to ensure
deterministic resolution.

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

#### Scenario: in-range transitive refresh in the relocated toolchain
- **WHEN** `npm update` is executed in `~/.local/share/home-toolchain`
- **THEN** every transitive dependency whose parent range already permits a newer version is
  raised to it, and a subsequent `npm outdated --all` reports no in-range moves remaining

#### Scenario: exact-pinned stragglers raised by upgrade-only override
- **WHEN** `aws4` is reachable only via `aws4@"^1.12.0"` and `extsprintf` is exact-pinned at
  `1.3.0` by `jsprim@2.0.2`
- **THEN** `aws4` resolves to `1.13.2` and `extsprintf` to `1.4.1` via `overrides` entries
  `">=1.13.2"` and `">=1.4.1"` respectively, with no downgrade of any package

#### Scenario: direct dependencies and override pins are at latest
- **WHEN** the relocated toolchain is inspected after the refresh
- **THEN** `npm outdated` reports no direct dependency behind latest, and every one of the 22
  `overrides` pins resolves to the latest published version of its package

#### Scenario: residual set is unchanged by the refresh
- **WHEN** `npm audit` is executed after the refresh
- **THEN** the count remains 12 high, because the residuals are rooted in `braces`
  (`<=3.0.3`), `node-forge` (`<=1.4.0`), and `@faker-js/faker` (`<=10.4.0`), each of which has
  no published version outside its advisory range reachable by upgrade
