# Spec Delta: npm-audit-remediation

## MODIFIED Requirements

### Requirement: Workstation Root Manifest Residual Identity Coverage
The unpatched-upstream residual inventory SHALL cover the relocated workstation toolchain manifest
(`~/.local/share/home-toolchain/package.json`) alongside the repository surfaces already governed,
and SHALL record each residual by package name, advisory identity, and dependency path. No
inventory entry SHALL reference a manifest in `$HOME`, which no longer exists.

#### Scenario: residual inventory enumerates the workstation root manifest

- **WHEN** `npm audit` is executed in `~/.local/share/home-toolchain` on 2026-10-04
- **THEN** evidence enumerates the reported advisories by package and dependency chain,
  recording the total as 12 high vulnerabilities and attributing them to the `@faker-js/faker`,
  `braces`, and `node-forge` roots

#### Scenario: residual surfaces are attributed distinctly

- **WHEN** residuals are recorded
- **THEN** the two contributing surfaces are distinguished — the `newman` |
  `newman-reporter-htmlextra` chain and the `@usebruno/cli` chain — rather than merged into a
  single undifferentiated count

### Requirement: Archived Prior Art Reconciliation Before New Remediation
Before a remediation change asserts a dependency upgrade is outstanding, the change SHALL check
the store's archive for a completed change covering the same manifest, so the upgrade is not
repeated.

#### Scenario: already-archived upgrades are recognised

- **WHEN** a remediation proposal is authored for the relocated toolchain manifest at
  `~/.local/share/home-toolchain/package.json`
- **THEN** the proposal references the archived changes that already performed the
  `newman`/`newman-reporter-htmlextra`/`@usebruno/cli` upgrades and does not re-execute them
