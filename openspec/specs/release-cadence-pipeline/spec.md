# release-cadence-pipeline Specification

## Purpose

Defines the GitHub Actions release workflow (.github/workflows/release-evidence.yml) that triggers on version tags, runs the full verification gate (make verify-release), and publishes structured evidence with 365-day retention.

## Requirements

> **Status**: IMPLEMENTED. release-evidence.yml workflow exists with tag trigger, verify-release gate, and 365-day artifact retention.

### Requirement: Release tags invoke a release-cadence CI job

The repository SHALL publish a `.github/workflows/release-evidence.yml` workflow that triggers on any `v*` tag push. The workflow SHALL run `make verify-release`, publish the resulting evidence directory as a GitHub Actions artifact with `retention-days: 365`, and SHALL fail the tag if any required gate fails.

#### Scenario: Tag push triggers the release workflow
- **WHEN** a maintainer pushes a tag matching the `v*` glob to the repository
- **THEN** the release-evidence workflow starts within 60 seconds, the workflow run is visible in the repository Actions tab, and the run executes `make verify-release` against the pinned Go toolchain

#### Scenario: Release evidence is retained for one year
- **WHEN** the release-evidence workflow completes successfully
- **THEN** the uploaded artifact has `retention-days: 365` enforced by the workflow YAML and the artifact's manifest lists the per-SHA evidence directory contents with their SHA-256 checksums

#### Scenario: A reachable High vulnerability fails the release tag
- **WHEN** `make test-security` reports a reachable High or Critical vulnerability that is not covered by an unexpired entry in `verification/vulnerability-exceptions.json`
- **THEN** the release-evidence workflow exits non-zero, the year-long artifact is NOT published, and the tag remains unannotated as a shippable release

### Requirement: Rollback rehearsal is a release-gate requirement

The release-evidence workflow MUST invoke `make test-rollback-rehearsal` and MUST block the release tag if the rehearsal reports any `failed` verification. The rehearsal target SHALL be wired so that, when no previous-release fixture exists, the target exits with `planned` status and the release-evidence workflow records the gap explicitly in the evidence manifest without falsely passing.

#### Scenario: Rollback rehearsal passes against a pinned prior fixture
- **WHEN** a `v0.2.0` tag push invokes the release-evidence workflow and `make test-rollback-rehearsal` proves the v0.2.0 candidate can be rolled back against the v0.1.0 image, prior schema, prior event fixtures, and prior Temporal histories
- **THEN** the rehearsal outcome is recorded as `passed` in the year-long evidence, the release tag is annotated as shippable, and no manual override is required

#### Scenario: First tagged release without a previous-release fixture
- **WHEN** the release-evidence workflow runs against the first tag and no `proto-baseline/v0.0.0/`, prior migration fixture, or prior Temporal history fixture exists
- **THEN** `make test-rollback-rehearsal` reports `planned`, the evidence manifest records the gap with an owner and expiry date, and the workflow fails the tag until a prior fixture is captured

