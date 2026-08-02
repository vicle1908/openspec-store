# Spec: Validation and Verification

## ADDED Requirements

### Requirement: Docker Compose file validation
The system SHALL validate `docker-compose.yml` syntax before deployment.

#### Scenario: Docker Compose config check
- **WHEN** user runs `docker compose config`
- **THEN** Docker Compose parses and validates the YAML structure
- **AND** any syntax errors are reported with line numbers
- **AND** the command exits 0 if the file is valid

#### Scenario: Pre-deployment validation script
- **WHEN** setup script or CI runs validation
- **THEN** it executes `docker compose config`
- **AND** aborts if the configuration is invalid

### Requirement: Pre-flight checks
The system SHALL verify prerequisites before starting Nexus.

#### Scenario: Prerequisites check
- **WHEN** pre-flight script runs
- **THEN** it verifies:
  - Docker daemon is running
  - Docker Compose plugin is installed (v2+)
  - Host port 80 is available (or configured port)
  - Minimum disk space (5GB free recommended)
  - Minimum RAM (4GB for single-host deployment)
- **AND** reports pass/fail for each check

### Requirement: Nexus version verification
The system SHALL verify Nexus version meets minimum requirements.

#### Scenario: Bootstrap version check
- **WHEN** bootstrap script connects to Nexus
- **THEN** it reads version from `GET /service/rest/v1/status`
- **AND** version is 3.91.0 or later
- **AND** bootstrap aborts if version is too old with clear message

#### Scenario: Swift group availability check
- **WHEN** bootstrap creates Swift repositories
- **THEN** it verifies Swift group format is supported
- **AND** attempts creation of swift-group via API
- **AND** failure indicates version problem

### Requirement: Bootstrap dry-run mode
The system SHALL support dry-run mode for bootstrap script.

#### Scenario: Dry run without changes
- **WHEN** bootstrap script runs with `--dry-run` flag
- **THEN** it reports what operations would be performed
- **AND** exits without making any API calls
- **AND** shows EULA text, repository list, user details

### Requirement: Bootstrap idempotency verification
The system SHALL verify bootstrap is idempotent.

#### Scenario: Re-run bootstrap
- **WHEN** bootstrap runs on existing instance
- **THEN** existing repositories are checked (not error)
- **AND** existing user is updated if settings differ
- **AND** final state matches fresh bootstrap

### Requirement: Health verification after start
The system SHALL verify all systems are healthy after startup.

#### Scenario: Post-startup verification
- **WHEN** 120 seconds pass after container start
- **THEN** all healthchecks report healthy
- **AND** all repositories are accessible via API
- **AND** bootstrap user can authenticate
