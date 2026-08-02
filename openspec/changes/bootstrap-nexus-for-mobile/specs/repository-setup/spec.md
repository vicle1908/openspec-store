# Spec: Repository Configuration

## ADDED Requirements

### Requirement: Maven repositories pre-configured
The system SHALL have Maven2 repositories for Android artifact management.

#### Scenario: Android CI publish
- **WHEN** CI publishes AAR to `maven-releases`
- **THEN** artifact is stored with metadata
- **AND** artifact is accessible via `maven-public` group URL

#### Scenario: Maven snapshot support
- **WHEN** CI publishes snapshot build to `maven-snapshots`
- **THEN** snapshot version (e.g., `1.0.0-SNAPSHOT`) is accepted
- **AND** SNAPSHOT metadata is updated correctly
- **AND** older snapshots are cleanup-eligible per policy

#### Scenario: Maven Central proxy
- **WHEN** build requests dependency from `maven-public`
- **THEN** Nexus proxies to Maven Central if not cached
- **AND** subsequent requests serve from cache
- **AND** offline builds still work for cached dependencies


### Requirement: Nexus version supports Swift group repositories
The system SHALL use Nexus Repository 3.91.0 or later.

#### Scenario: Version validation
- **WHEN** checking Nexus version
- **THEN** it is 3.91.0 or later
- **AND** Swift group repository creation succeeds
- **AND** versions before 3.91.0 are rejected with clear error message

### Requirement: Swift repositories configured
The system SHALL have Swift repositories for iOS SPM integration.

#### Scenario: Swift hosted repository
- **WHEN** CI publishes Swift package to `swift-hosted`
- **THEN** package is stored with scope/name/version
- **AND** SPM registry API endpoints respond correctly

#### Scenario: Swift proxy repository
- **WHEN** build requests external Swift package
- **THEN** Nexus proxies to upstream registry
- **AND** package is cached for subsequent requests

#### Scenario: Swift group repository
- **WHEN** SPM client resolves dependency from `swift-group`
- **THEN** both hosted and proxy packages are discoverable
- **AND** correct package version is returned

### Requirement: Repository bootstrap automation
The system SHALL automate repository creation via REST API.

#### Scenario: Bootstrap script execution
- **WHEN** bootstrap script runs with admin credentials
- **THEN** all required repositories are created
- **AND** no manual UI interaction is needed

#### Scenario: Idempotent bootstrap
- **WHEN** bootstrap script runs on already-configured Nexus
- **THEN** existing repositories are verified, not recreated
- **AND** script completes without errors

### Requirement: Swift proxy remote URL configured
The system SHALL configure `swift-proxy` with a valid upstream registry URL.

#### Scenario: External Swift package caching
- **WHEN** `swift-proxy` is configured with an upstream Swift Package Registry URL
- **THEN** external Swift packages are cached when requested via `swift-group`
- **AND** group repository includes both `swift-hosted` and `swift-proxy`
- **NOTE** There is no official public Swift package registry; the proxy URL is environment-specific (e.g., GitHub Packages registry, another Nexus instance, or a private registry)

---

## MODIFIED Requirements

### Requirement: Snapshot policy
The system SHALL configure write policies correctly for release vs snapshot.

#### Scenario: Release repo policy
- **WHEN** `maven-releases` is configured
- **THEN** `writePolicy` is set to `allow_once` (immutable releases)
- **AND** overwrite attempts return HTTP 400

#### Scenario: Snapshot repo policy
- **WHEN** `maven-snapshots` is configured
- **THEN** `writePolicy` allows SNAPSHOT overwrites
- **AND** each build produces unique snapshot (timestamped)
