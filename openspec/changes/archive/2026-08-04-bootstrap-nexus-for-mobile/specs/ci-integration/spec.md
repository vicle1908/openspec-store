# Spec: CI/CD Integration

## ADDED Requirements

### Requirement: Dedicated CI user exists
The system SHALL have a service account for CI/CD publishing.

#### Scenario: CI authentication
- **WHEN** CI pipeline authenticates as `ci-user`
- **THEN** publish operations succeed
- **AND** read operations succeed without admin privileges

### Requirement: EULA auto-accepted
The system SHALL accept Community Edition EULA programmatically.

#### Scenario: First deployment
- **WHEN** bootstrap script runs on fresh Nexus instance
- **THEN** EULA is accepted via REST API
- **AND** write operations are unblocked

#### Scenario: EULA acceptance mechanism
- **WHEN** bootstrap GETs `/service/rest/v1/system/eula`
- **THEN** it receives JSON with `accepted: false` and full `disclaimer`
- **AND** POSTs same JSON back with `accepted: true`
- **AND** writes succeed after HTTP 204 response

### Requirement: Anonymous read enabled
The system SHALL allow unauthenticated read access.

#### Scenario: Developer build
- **WHEN** developer runs Gradle sync or SPM resolve
- **THEN** artifacts download without credentials
- **AND** only read access is granted

---

## MODIFIED Requirements

### Requirement: CI credentials storage
The system SHALL document how CI credentials are stored.

#### Scenario: Jenkins credential management
- **WHEN** Jenkins job uses Nexus credentials
- **THEN** credentials are stored in Jenkins Credentials Plugin
- **AND** injected as environment variables (`NEXUS_USER`, `NEXUS_PASS`)
- **AND** never committed to SCM

#### Scenario: GitLab CI variable management
- **WHEN** GitLab CI pipeline uses Nexus credentials
- **THEN** credentials are stored in GitLab CI/CD Variables (Settings then CI/CD)
- **AND** marked as Masked in variable settings
- **AND** exposed as environment variables in pipeline jobs

### Requirement: CI user roles
The system SHALL assign appropriate roles to the CI user.

#### Scenario: CI user role assignment
- **WHEN** `ci-user` is created
- **THEN** it is assigned `nx-anonymous` role for baseline read
- **AND** custom role `ci-publisher` is created with the following minimum privileges:
  - `nx-component-upload` (required for any upload operation)
  - `nx-repository-view-maven-*-*` (read all Maven repos)
  - `nx-repository-admin-maven-*-*` (write to Maven hosted repos)
  - `nx-repository-view-swift-*-*` (read all Swift repos)
  - `nx-repository-admin-swift-*-*` (write to Swift hosted repos)
- **AND** NOT assigned `nx-admin` (principle of least privilege)
