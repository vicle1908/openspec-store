# Spec Delta: npm-audit-remediation

## ADDED Requirements

### Requirement: Failed Force-Fix Recovery via Coordinated Peer-Consistent Upgrade

When `npm audit fix --force` fails and leaves the workstation root manifest's dependency
tree in an `ELSPROBLEMS` state (packages absent from `node_modules` while still recorded in
`package-lock.json`), the remediation SHALL restore the tree using a single coordinated,
peer-consistent dependency change rather than by re-invoking `--force`, and SHALL verify the
restored CLI binaries resolve and execute.

#### Scenario: peer-consistent Newman chain upgrade replaces forbidden force path

- **WHEN** `newman` is raised to `^6.2.2` and `newman-reporter-htmlextra` to `^1.23.1`
  together in `/Users/androidteam/package.json`
- **THEN** `npm install` completes with exit code 0 without `--force` or
  `--legacy-peer-deps`, and the previously deleted `newman` and `newman-reporter-htmlextra`
  directories exist in `node_modules` at versions satisfying both `package.json` ranges

#### Scenario: no force flag is used during recovery

- **WHEN** the recovery install is executed
- **THEN** the command line contains neither `--force` nor `--legacy-peer-deps`, so peer
  incompatibilities surface as errors instead of being silently overridden

### Requirement: Override-to-Transitive-Pin Reconciliation

Where a manifest `overrides` entry pins a package to a major version that conflicts with a
newly selected parent's pinned transitive dependency, the remediation SHALL reconcile the
override so the resolved tree is internally consistent, or SHALL document the override as an
intentional, verified exception with evidence that resolution still succeeds.

#### Scenario: csv-parse override reconciled against newman 6 pin

- **WHEN** `newman@6.2.2` declares `csv-parse@4.16.3` and the manifest override pins
  `csv-parse` to `7.0.3`
- **THEN** the conflict is either removed or explicitly recorded, and `npm install` resolves
  a single consistent tree with no `ERESOLVE` error in the output

### Requirement: Residual Advisory Identity Recording

Audit remediation SHALL record residual advisories by package name, advisory identity, and
dependency path rather than by aggregate count alone, so verification can distinguish fixed
advisories from unpatched-upstream residues and from newly published advisories.

#### Scenario: residual advisory set recorded by identity

- **WHEN** `npm audit` is executed in `/Users/androidteam` after recovery
- **THEN** evidence enumerates each remaining advisory by package and dependency chain, and
  the total is reconciled against the pre-remediation count of 12 (3 moderate, 9 high)

#### Scenario: exit-status semantics of npm audit are not conflated with remediation failure

- **WHEN** `npm audit` exits non-zero because advisories remain that have no patched version
- **THEN** the non-zero exit is recorded as an unpatched-upstream residual condition with its
  advisory identities, not reported as a failure of the recovery

### Requirement: Home-Directory Manifest Footgun Recording

Because a `package.json` in `$HOME` causes `npm` and `npx` to resolve to it from any directory
beneath `$HOME` that lacks its own manifest, the remediation SHALL record the hazard and the
correct invocation discipline so the incident is not silently repeated.

#### Scenario: prefix resolution hazard is documented

- **WHEN** the incident is recorded in evidence
- **THEN** the evidence states that `npm prefix` from `~/Developer` resolves to
  `/Users/androidteam` and that dependency commands MUST be issued from the owning repository
  root
