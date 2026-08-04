# TDT_HOME Provider Rollout Specification

## Purpose

Define the evidence and ownership gates that qualify and stage a `tdt-core`
provider release without treating provider-only checks as consumer or live-root
readiness.

## ADDED Requirements

### Requirement: A provider release candidate SHALL be reproducible

The release gate SHALL bind one source revision, provider version, wheel hash,
locked dependency closure, and value-free artifact inventory.

#### Scenario: A clean candidate qualifies

- **GIVEN** a fresh wheelhouse contains the provider and its locked closure
- **WHEN** installation runs without a checkout or `PYTHONPATH`
- **THEN** version equality, package resources, `tdt --help`, provider doctor,
  and provider contract checks pass
- **AND** the evidence records hashes and versions without credentials

#### Scenario: Candidate evidence disagrees

- **GIVEN** wheel metadata, imported runtime version, lockfile, or hash inventory
  disagree
- **WHEN** the release gate runs
- **THEN** qualification fails before staging
- **AND** the previous artifact remains the rollback candidate

### Requirement: Staging SHALL prove provider-only runtime readiness

Staging SHALL identify its target, package source, principal, configuration
profile, and health evidence before rollout approval.

#### Scenario: Provider-only staging passes

- **GIVEN** an identified disposable target with an approved package source
- **WHEN** the provider is installed and its base diagnostics execute
- **THEN** startup, packaged contracts, doctor, and redacted health evidence
  pass without importing sibling checkout code
- **AND** no live `~/.tdt` path is opened or mutated

#### Scenario: Staging ownership is unknown

- **GIVEN** the target, writer principal, package source, or configuration owner
  is missing or contradictory
- **WHEN** rollout readiness is evaluated
- **THEN** the gate remains blocked
- **AND** it does not infer approval from a successful local test

### Requirement: Rollout SHALL require explicit approval and preserve rollback

Every rollout SHALL retain the exact pre-change artifact and record an
operator-approved release, target, and rollback action.

#### Scenario: Rollout is approved

- **GIVEN** candidate, staging, ownership, health, and compatibility evidence
  are complete
- **WHEN** the authorized operator approves the rollout
- **THEN** the record names the release, target, approval, and rollback artifact
- **AND** consumer adoption and live-root cutover remain separate gates

#### Scenario: Rollback is requested

- **GIVEN** a rollout health gate fails or approval is withdrawn
- **WHEN** rollback is executed
- **THEN** the exact pre-change artifact is restored
- **AND** operator data, credentials, databases, and consumer source remain
  unchanged

### Requirement: Provider rollout evidence SHALL distinguish readiness scopes

Reports SHALL classify provider artifact, staging, consumer, deployment, and
live-root evidence separately.

#### Scenario: Provider-only evidence is complete

- **GIVEN** local and staging provider checks pass but consumer evidence is
  absent
- **WHEN** the rollout report is generated
- **THEN** provider and staging scopes may be marked ready
- **AND** consumer and live-root scopes remain unverified or blocked
