# Security Audit

## Purpose

Define requirements for systematic vulnerability remediation across the workspace using npm/pnpm dependency overrides.

## ADDED Requirements

### Requirement: Vulnerability Assessment

The system SHALL identify all npm/pnpm vulnerabilities in workspace repositories.

#### Scenario: Home Directory Assessment
- **Given** the home directory has `package.json` with dependencies
- **When** `npm audit` is executed
- **Then** the system reports all vulnerabilities with severity levels
- **And** the system identifies the source package for each vulnerability

#### Scenario: mcp-router Assessment
- **Given** the mcp-router workspace has `pnpm-workspace.yaml`
- **When** `pnpm audit` is executed from workspace root
- **Then** the system reports all vulnerabilities across packages
- **And** the system identifies transitive dependency chains

### Requirement: Deprecated Package Removal

The system SHALL remove deprecated packages that have modern replacements.

#### Scenario: Standalone npx Removal
- **Given** `npx@3.0.0` is installed as a standalone package
- **And** modern npm includes npx built-in
- **When** `npm uninstall npx` is executed
- **Then** the package is removed
- **And** the built-in npx remains functional
- **And** 135+ transitive packages are removed

### Requirement: Package Upgrades

The system SHALL upgrade packages to latest compatible versions.

#### Scenario: Newman Upgrade
- **Given** `newman@4.6.1` is installed
- **And** `newman@6.2.2` is available
- **When** `npm install newman@latest` is executed
- **Then** newman is upgraded to 6.2.2
- **And** peer dependencies are resolved
- **And** CLI remains functional

#### Scenario: Reporter Replacement
- **Given** `newman-reporter-html@1.0.5` has peer dependency on `newman@4`
- **And** `newman@6` is installed
- **When** `newman-reporter-htmlextra@1.23.1` is installed
- **Then** the old reporter is removed
- **And** the new reporter works with newman 6
- **And** HTML reports generate correctly

### Requirement: Dependency Overrides

The system SHALL use npm/pnpm overrides to force patched versions of transitive dependencies.

#### Scenario: Override Application
- **Given** `lodash@4.17.x` has known vulnerabilities
- **And** `lodash@4.18.1` is the patched version
- **When** `"lodash": "4.18.1"` is added to overrides
- **Then** all transitive lodash dependencies resolve to 4.18.1
- **And** `npm audit` no longer reports lodash vulnerabilities

#### Scenario: Override Verification
- **Given** overrides are configured in `package.json`
- **When** `npm install` is executed
- **Then** all overridden packages install at specified versions
- **And** `npm ls <package>` shows the overridden version
- **And** no peer dependency conflicts occur

### Requirement: Build Verification

The system SHALL verify that changes don't break builds.

#### Scenario: Electron Rebuild
- **Given** mcp-router has native modules (argon2, better-sqlite3)
- **When** `pnpm install` completes
- **Then** electron-rebuild runs successfully
- **And** native modules are compiled for current platform

#### Scenario: CLI Tool Verification
- **Given** CLI tools are installed (npx, newman, pyright)
- **When** `which <tool>` is executed
- **Then** the tool is found in PATH
- **And** `<tool> --version` returns expected version

### Requirement: Vulnerability Reduction

The system SHALL measurably reduce vulnerability counts.

#### Scenario: Home Directory Success
- **Given** home directory had 51 vulnerabilities
- **When** all fixes are applied
- **Then** vulnerability count is 0
- **And** `npm audit` exits with code 0

#### Scenario: mcp-router Improvement
- **Given** mcp-router had 62 vulnerabilities
- **When** updates and overrides are applied
- **Then** vulnerability count is reduced by at least 30%
- **And** no new critical vulnerabilities are introduced
