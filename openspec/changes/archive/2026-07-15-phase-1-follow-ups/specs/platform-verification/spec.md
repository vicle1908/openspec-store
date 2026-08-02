## ADDED Requirements

### Requirement: Release evidence retention
The release evidence SHALL be retained for at least one year. Pull-request evidence SHALL be retained for at least 30 days.

#### Scenario: Release tag publishes year-long evidence
- **WHEN** a maintainer pushes a `v*` tag and the release-evidence workflow completes successfully
- **THEN** the published artifact has `retention-days: 365` enforced by `.github/workflows/release-evidence.yml`, and the artifact contents include `evidence.json`, `coverage.out`, `go-test.json`, `govulncheck.json`, `trivy-fs.json`, and `sbom.cdx.json`

#### Scenario: Pull request publishes 30-day evidence
- **WHEN** a pull request pushes commits and the verify workflow completes
- **THEN** the published artifact has `retention-days: 30` and the contents match the release evidence schema

## ADDED Requirements

### Requirement: Release gate requires rollback rehearsal
A release candidate SHALL pass `make test-rollback-rehearsal` against the immediately previous release fixture before the tag can be annotated as shippable.

#### Scenario: Release tag without a passed rehearsal
- **WHEN** the release-evidence workflow runs `make test-rollback-rehearsal` and the rehearsal reports `failed` or `planned`
- **THEN** the workflow exits non-zero, the year-long artifact is NOT published, and the tag is not annotated as shippable

#### Scenario: Release tag with a passed rehearsal
- **WHEN** the release-evidence workflow runs `make test-rollback-rehearsal` and the rehearsal reports `passed`
- **THEN** the rehearsal outcome is recorded as `passed` in the evidence manifest and the tag may be annotated as shippable

### Requirement: Release-cadence workflow is version-controlled and discoverable
The `.github/workflows/release-evidence.yml` workflow SHALL be committed to the repository, SHALL declare its trigger, permissions, and required checks inline, and SHALL be visible in the repository's Actions tab alongside `verify.yml`.

#### Scenario: Reviewer audits the release workflow
- **WHEN** a reviewer reads `.github/workflows/release-evidence.yml` during a release-process audit
- **THEN** the workflow's `on:` trigger, `permissions:` block, retention policy, and gate list are visible without leaving the file and match the design's release-cadence decisions