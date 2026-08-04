# Spec: CI/CD Pipeline Examples

## ADDED Requirements

### Requirement: Jenkins pipeline for Android
The system SHALL provide a Jenkins Declarative Pipeline for Android AAR publishing.

#### Scenario: Jenkins Android build
- **WHEN** Jenkins job runs on library module push
- **THEN** it executes `./gradlew :library:publish` to `maven-releases`
- **AND** credentials are injected from Jenkins Credentials Plugin (type: usernamePassword)
- **AND** build fails if version already exists (immutable releases)
- **AND** artifacts are published only on `main` or `release/*` branches

### Requirement: GitLab CI pipeline for Android
The system SHALL provide a GitLab CI configuration for Android AAR publishing.

#### Scenario: GitLab CI Android build
- **WHEN** `.gitlab-ci.yml` pipeline runs on merge request merge
- **THEN** it executes `./gradlew :library:publishReleasePublicationToNexusRepository`
- **AND** `NEXUS_USER` and `NEXUS_PASS` are injected from GitLab CI/CD Variables
- **AND** variables are masked in job logs
- **AND** only `main` branch publishes releases, feature branches validate only

### Requirement: Jenkins pipeline for iOS
The system SHALL provide a Jenkins Pipeline for Swift package publishing.

#### Scenario: Jenkins iOS build
- **WHEN** Jenkins job runs on iOS library tag push
- **THEN** it builds XCFramework via `xcodebuild` or `swift build`
- **AND** creates ZIP with Package.swift + XCFramework
- **AND** uploads to `swift-hosted` via Nexus REST API (curl)
- **AND** scope/name/version are derived from Git tag (e.g., `v1.0.0`)

### Requirement: GitLab CI pipeline for iOS
The system SHALL provide a GitLab CI configuration for Swift package publishing.

#### Scenario: GitLab CI iOS build
- **WHEN** GitLab CI runs on tag push
- **THEN** it builds Swift package on macOS runner
- **AND** archives source with `swift package archive-source`
- **AND** uploads ZIP to `swift-hosted` via REST API
- **AND** version matches Git tag name

### Requirement: CI version derivation
The system SHALL derive artifact versions from Git metadata.

#### Scenario: Version from Git tag
- **WHEN** Git tag `v1.2.3` is pushed
- **THEN** CI publishes version `1.2.3` to Nexus
- **AND** tag name is validated (semantic versioning format)

#### Scenario: Snapshot from branch commit
- **WHEN** commit is pushed to `develop` branch
- **THEN** CI publishes version `X.Y.Z-SNAPSHOT` to `maven-snapshots`
- **AND** snapshot includes Git short SHA for traceability
