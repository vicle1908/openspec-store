# Spec Delta: npm-audit-remediation

## ADDED Requirements

### Requirement: Downgrade-Only Remedy Indicates Unpatched Upstream

When `npm audit` reports an advisory for a package that is already installed at its latest
published version, and the only remedy the audit offers is a version *downgrade*, the
remediation SHALL classify that advisory as unpatched-upstream, SHALL record its identity,
and SHALL NOT apply the proposed downgrade.

#### Scenario: latest-pinned direct dependency reported vulnerable

- **WHEN** `newman@6.2.2` is the latest published release of `newman`, `npm audit` reports
  `newman` within range `>=6.0.0`, and the offered fix is `newman@5.3.2` (a downgrade)
- **THEN** the advisory is recorded as unpatched-upstream with the installed version and the
  offered downgrade cited, and `newman` is left at `6.2.2`

#### Scenario: force-fix convergence is impossible

- **WHEN** every direct dependency in the manifest is at its latest published version and each
  residual advisory's only offered remedy is a downgrade
- **THEN** `npm audit fix --force` is recorded as non-convergent, and is not re-run as a
  remediation step

### Requirement: Workstation Root Manifest Residual Identity Coverage

The unpatched-upstream residual inventory SHALL cover `/Users/androidteam/package.json`
alongside the repository surfaces already governed, and SHALL record each residual by package
name, advisory identity, and dependency path.

#### Scenario: residual inventory enumerates the workstation root manifest

- **WHEN** `npm audit` is executed in `/Users/androidteam` on 2026-10-04
- **THEN** evidence enumerates the reported advisories by package and dependency chain,
  recording the total as 19 vulnerabilities (2 moderate, 17 high)

#### Scenario: residual surfaces are attributed distinctly

- **WHEN** residuals are recorded
- **THEN** the two contributing surfaces are distinguished — the `newman` |
  `newman-reporter-htmlextra` chain and the `@usebruno/cli` chain — rather than merged into a
  single undifferentiated count

### Requirement: Home-Directory Manifest Footgun Recording

Because a `package.json` in `$HOME` causes `npm` and `npx` to resolve to it from any directory
beneath `$HOME` that lacks its own manifest, the remediation SHALL record the hazard and the
resulting invocation discipline.

#### Scenario: prefix resolution hazard is documented

- **WHEN** the incident is recorded in evidence
- **THEN** the evidence states that `npm prefix` from `~/Developer` resolves to
  `/Users/androidteam` and that dependency commands MUST be issued from the owning repository
  root

### Requirement: Archived Prior Art Reconciliation Before New Remediation

Before a remediation change asserts a dependency upgrade is outstanding, the change SHALL
check the store's archive for a completed change covering the same manifest, so the upgrade is
not repeated.

#### Scenario: already-archived upgrades are recognised

- **WHEN** a remediation proposal is authored for `/Users/androidteam/package.json`
- **THEN** the proposal references the archived changes that already performed the
  `newman`/`newman-reporter-htmlextra`/`@usebruno/cli` upgrades and does not re-execute them
