# TDT_HOME Source Conformance Specification

## Purpose

Define a read-only, ownership-aware audit that identifies provider-boundary
violations and reports repository/deployment conformance without inventing
consumer facts or changing source trees.

## ADDED Requirements

### Requirement: The source audit SHALL detect provider-boundary bypasses

The audit SHALL inspect supported source syntax for hard-coded `~/.tdt`
construction, ad-hoc environment/config/credential reads, and unapproved
provider-boundary bypasses.

#### Scenario: A hard-coded root is found

- **GIVEN** a participant source file constructs `Path.home() / ".tdt"` or an
  equivalent literal outside an approved provider adapter
- **WHEN** the AST audit runs
- **THEN** it emits a stable rule id, repository-relative path, line, and
  symbol context
- **AND** it does not include surrounding secret-shaped values

#### Scenario: Approved provider usage is scanned

- **GIVEN** a source file calls an approved `tdt-core` path or environment API
- **WHEN** the audit runs
- **THEN** it records the usage as compliant or neutral evidence
- **AND** it does not report a false positive solely because the call mentions
  `TDT_HOME`

### Requirement: Participant manifests SHALL be explicit and identity-bound

Each registered participant SHALL provide a value-free manifest declaring its
repository identity, role, provider contract/version floor, approved entry
points, and deployment-attestation status.

#### Scenario: A valid manifest is loaded

- **GIVEN** a manifest identity marker and repository/role match the packaged
  participant registry
- **WHEN** conformance loads the manifest
- **THEN** it accepts the manifest and validates all required fields
- **AND** it preserves unknown principal facts as unknown rather than true

#### Scenario: A manifest is missing or mismatched

- **GIVEN** a registered participant has no manifest or its identity/role does
  not match the registry
- **WHEN** strict conformance runs
- **THEN** it returns a deterministic failure for that participant
- **AND** it does not infer compliance from source files or directory names

#### Scenario: A manifest scaffold is requested

- **GIVEN** an operator requests the provider-owned scaffold command for a
  repository
- **WHEN** `tdt config create-manifest` runs without an output path
- **THEN** it emits a value-free `.tdt/governance-manifest.json` scaffold to
  standard output without changing the repository
- **AND** an explicitly requested output path is created only when it does not
  already exist
- **AND** the command never overwrites or silently writes a consumer manifest

### Requirement: Exceptions SHALL be repository-owned, scoped, and expiring

An exception SHALL include a rule, bounded file/symbol scope, reason, owner,
approval reference, and expiry; exceptions SHALL NOT suppress provider security
rules globally.

#### Scenario: A current exception covers one finding

- **GIVEN** a finding matches one non-security rule and an unexpired,
  identity-bound exception with the same scope
- **WHEN** the report is generated
- **THEN** the finding is classified as excepted with the exception metadata
- **AND** the exception does not hide other rules or files

#### Scenario: An exception is expired or unsafe

- **GIVEN** an exception is expired, duplicated, scope-mismatched, or attempts
  to suppress a security rule
- **WHEN** strict conformance runs
- **THEN** it remains a failure
- **AND** the report names the exception problem without exposing its values

### Requirement: Conformance reports SHALL be deterministic, redacted, and read-only

The audit SHALL emit stable text/JSON findings and SHALL leave audited source,
manifest, deployment, and runtime trees unchanged.

#### Scenario: A report contains unresolved findings

- **GIVEN** the audit finds bypasses, missing manifests, or unknown required
  deployment attestations
- **WHEN** strict mode is requested
- **THEN** it exits non-zero and sorts findings by repository, path, line, and
  rule id
- **AND** it omits environment values, credentials, DSNs, and raw file bodies

#### Scenario: Audit is repeated

- **GIVEN** the same repository snapshots and manifests are audited twice
- **WHEN** both reports are generated
- **THEN** their normalized findings and exit status are identical
- **AND** the audited trees have identical content hashes before and after
