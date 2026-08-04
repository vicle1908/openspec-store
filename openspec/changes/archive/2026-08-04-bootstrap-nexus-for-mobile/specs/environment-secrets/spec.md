# Spec: Environment and Secrets Management

## ADDED Requirements

### Requirement: Environment variables via dotenv
The system SHALL provide a `.env.template` file for configuration.

#### Scenario: Environment setup
- **WHEN** user copies `.env.template` to `.env`
- **THEN** all required variables are documented with examples
- **AND** sensitive values are clearly marked

### Requirement: Secrets excluded from version control
The system SHALL prevent secret files from being committed.

#### Scenario: Git safety
- **WHEN** `.gitignore` is configured
- **THEN** it excludes: `nexus-data/`, `.env`, `admin.password`, `*.tar.gz`, `keystore.*`
- **AND** `git status` shows no untracked secrets

### Requirement: CI credential injection patterns
The system SHALL document credential injection for both CI platforms.

#### Scenario: Jenkins credentials
- **WHEN** Jenkins uses Credentials Plugin
- **THEN** credentials are stored as `Username with password` type
- **AND** ID is `nexus-publish-credentials`
- **AND** exposed as env vars: `NEXUS_USER`, `NEXUS_PASS`

#### Scenario: GitLab CI variables
- **WHEN** GitLab project uses CI/CD Variables
- **THEN** `NEXUS_USER` and `NEXUS_PASS` are in Settings then CI/CD then Variables
- **AND** `NEXUS_PASS` is masked (Protect + Mask flags enabled)
- **AND** scope is limited to protected branches

### Requirement: Admin password management
The system SHALL handle the initial admin password securely.

#### Scenario: First boot password retrieval
- **WHEN** Nexus starts for the first time
- **THEN** `admin.password` file appears in `nexus-data/`
- **AND** bootstrap script reads it to perform setup
- **AND** password file is deleted after bootstrap completes
- **AND** admin user password is changed to a secure value
