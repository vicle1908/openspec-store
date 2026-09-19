# workstation-tooling-maintenance Specification

## Purpose
Defines periodic maintenance, runtime upgrades, unmanaged application migration, and background LaunchAgent daemon health remediation standards for macOS developer workstations.

## Requirements

### Requirement: Verified package manager and runtime upgrades

The workstation maintenance workflow SHALL check and upgrade installed package managers and global developer runtimes against their primary distribution channels without installing unverified breaking changes.

#### Scenario: Global runtime upgrade verification
- **WHEN** the operator triggers a global package upgrade
- **THEN** the system verifies `npm` global packages, `bun`, `pnpm`, and Homebrew formulae against upstream registry release tags
- **AND** it verifies that post-upgrade tool binaries execute successfully with exit code 0.

#### Scenario: Preflight checks for workstation update scripts
- **WHEN** the canonical workstation maintenance update script executes
- **THEN** it SHALL verify that all approved core tools (`brew`, `bun`, `npm`, `pi`, `omp`, `jq`, `perl`) are present and meet security policy
- **AND** if any required tool is missing or unapproved, preflight MUST fail closed before attempting modifications.

### Requirement: Migration of standalone apps to declarative management

The workstation maintenance workflow SHALL inventory installed applications outside package management and migrate supported applications to Homebrew casks or formulae.

#### Scenario: Standalone application migration to Cask
- **WHEN** an application in `/Applications` is identified as supported by an official Homebrew cask but currently unmanaged
- **THEN** the workflow installs or adopts the application into Homebrew management
- **AND** existing application configuration, data directories, and user settings MUST remain preserved.

#### Scenario: Standalone CLI migration to Formula
- **WHEN** a standalone executable in `/usr/local/bin` is obsolete or non-native
- **THEN** the workflow replaces the unmanaged binary with a native Homebrew formula package
- **AND** it verifies native architecture compatibility and successful CLI version output.

### Requirement: LaunchAgent daemon health remediation

The workstation maintenance workflow SHALL detect failing or crash-looping user LaunchAgents, diagnose root causes, and apply non-destructive fixes.

#### Scenario: Missing virtual environment binary in LaunchAgent
- **WHEN** a LaunchAgent exits repeatedly with exit code 126 due to a missing Python virtual environment binary
- **THEN** the workflow SHALL recreate the required virtualenv from locked dependency definitions using `uv sync`
- **AND** it verifies the binary exists, is executable, and restarts the service cleanly via `launchctl`.

#### Scenario: Plist binary path naming discrepancy
- **WHEN** a LaunchAgent configuration targets an executable name differing from the installed application bundle binary
- **THEN** the workflow SHALL establish a non-destructive symlink bridging the configured name to the actual binary
- **AND** it verifies that the daemon executes without configuration failure (exit code 0).
