# Spec Delta: npm-audit-remediation

## MODIFIED Requirements

### Requirement: Workstation Root Manifest Peer Conflict Resolution
The relocated workstation toolchain manifest (`~/.local/share/home-toolchain/package.json`) SHALL
retain the peer-resolution outcome achieved before relocation: `newman` and its reporter plugin
pinned to semver-compatible majors, overrides held at non-vulnerable thresholds, and `npm install`
completing without `ERESOLVE` errors and without `--force` or `--legacy-peer-deps`. No manifest
SHALL exist at `$HOME`.

#### Scenario: newman and htmlextra peer alignment
- **WHEN** `newman` is pinned to `^6.2.2` and `newman-reporter-htmlextra` to `^1.23.1` in
  `~/.local/share/home-toolchain/package.json`, with the `adm-zip` override held at `0.6.1`
- **THEN** npm installs cleanly without `--force` or `--legacy-peer-deps`, and peer dependency
  resolution succeeds

#### Scenario: relocated manifest preserves the peer resolution

- **WHEN** `~/.local/share/home-toolchain/package.json` declares `newman@^6.2.2` and
  `newman-reporter-htmlextra@^1.23.1` and `npm install` is executed there
- **THEN** the install completes with exit code 0 without `--force` or `--legacy-peer-deps`, and
  no `ERESOLVE` error is emitted

#### Scenario: npm audit execution after upgrade
- **WHEN** `npm audit` is executed in `~/.local/share/home-toolchain`
- **THEN** the command evaluates the dependency graph without `ERESOLVE` errors, and reports
  the 12 high advisories recorded as irreducible rather than the historical Newman v4 chain count

#### Scenario: no manifest remains at the home directory

- **WHEN** the home directory is inspected
- **THEN** no `package.json`, `package-lock.json`, or `node_modules` exists directly in `$HOME`,
  and `npm prefix` executed from any workspace directory resolves to that directory

### Requirement: Root Manifest Transitive Override Hardening
The relocated workstation toolchain manifest SHALL declare strict version overrides for the
transitive HTTP, form handling, and parser libraries required by the Git-native API testing
tooling (`axios`, `form-data`, `js-yaml`, `yaml`, `@faker-js/faker`), and SHALL record which
residual advisories remain regardless of those overrides, because no published version resolves
them.

#### Scenario: elimination of bruno transitive CVEs
- **WHEN** overrides for `axios@^1.20.0`, `form-data@4.0.6`, `js-yaml@>=4.3.2`, and
  `yaml@>=2.8.3` are active in `~/.local/share/home-toolchain/package.json`
- **THEN** `npm audit` reports no vulnerabilities attributable to the Bruno dependency chain
  other than the `@faker-js/faker` residual, which is recorded as irreducible because raising
  it breaks `newman` and `bru`

#### Scenario: override set survives relocation intact

- **WHEN** the relocated manifest is inspected
- **THEN** it declares the same override set as before relocation, and `axios@^1.20.0`,
  `form-data@4.0.6`, `js-yaml@>=4.3.2`, and `yaml@>=2.8.3` are all present and active

#### Scenario: residual set is recorded rather than claimed resolved

- **WHEN** `npm audit` is executed against the relocated manifest
- **THEN** the residuals rooted in `@faker-js/faker`, `braces`, and `node-forge` are recorded as
  irreducible with their no-fix evidence, and the remediation does NOT claim zero vulnerabilities
  for the Bruno dependency chain, because `@faker-js/faker` cannot be raised without breaking
  `newman` and `bru`
