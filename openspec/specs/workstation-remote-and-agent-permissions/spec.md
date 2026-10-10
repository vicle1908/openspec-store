# workstation-remote-and-agent-permissions Specification

## Purpose

Defines workstation standards for remote access software and AI coding assistant runtimes on macOS, enforcing single-version installation via Homebrew Cask and verifying complete system TCC permissions across Accessibility, Screen Recording, and Full Disk Access.

## Requirements

### Requirement: Workstation remote desktop applications SHALL maintain single-version Homebrew Cask installation

Remote desktop utilities SHALL be installed exclusively through official Homebrew Casks, maintaining exactly one application bundle on the filesystem, purging obsolete versions from Caskroom, and deploying native background services.

#### Scenario: Official Homebrew Cask installation and upgrade
- **WHEN** a remote desktop utility such as AnyDesk is provisioned or reinstalled
- **THEN** it SHALL be managed via `brew reinstall --cask anydesk` (or `brew upgrade --cask anydesk`)
- **AND** the installed application bundle in `/Applications` SHALL reflect the latest upstream release

#### Scenario: Single version integrity and duplicate elimination
- **WHEN** the host filesystem is inspected for application bundles matching the tool
- **THEN** exactly one application bundle SHALL exist across `/Applications` and user directories
- **AND** no duplicate binary versions or shadow bundles SHALL remain on disk

#### Scenario: Background service and privileged helper registration
- **WHEN** the application is installed and initialized
- **THEN** required system launch services (`com.philandro.anydesk.service`) and privileged helper tools (`com.philandro.anydesk.Helper`) SHALL be registered in `/Library/LaunchDaemons` and `/Library/PrivilegedHelperTools`
- **AND** the background service SHALL execute under native launchd supervision

### Requirement: Remote access and automation agents SHALL maintain verified macOS TCC permissions

Remote access utilities and automated AI coding assistants requiring screen capture, synthetic input, or filesystem access SHALL possess verified macOS Transparency, Consent, and Control (TCC) authorizations with active status in the system authorization database.

#### Scenario: Full permissions granted for remote desktop tooling
- **WHEN** AnyDesk is configured for complete remote assistance operations
- **THEN** `kTCCServiceAccessibility` (Accessibility), `kTCCServiceScreenCapture` (Screen Recording), and `kTCCServiceSystemPolicyAllFiles` (Full Disk Access) SHALL evaluate to `auth_value = 2` (Allowed) in the system TCC store
- **AND** no pending permission prompts or warning dialogs SHALL block unattended connection

#### Scenario: Full permissions verified for AI coding assistants and automation harnesses
- **WHEN** AI developer tools (Orca, OMP, ChatGPT, and Codex) execute on the host workstation
- **THEN** their associated application bundles and agent helpers (`com.stablyai.orca`, `com.stablyai.orca.computer-use`, `com.openai.codex`, `com.openai.sky.CUAService`, `com.codexuse.desktop`, and OMP execution runner) SHALL possess active authorizations for required operational domains (`kTCCServiceAccessibility`, `kTCCServiceScreenCapture`, and `kTCCServiceSystemPolicyAllFiles`)
- **AND** computer-use capabilities SHALL report granted status without permission rejection errors

#### Scenario: Value-blind audit of system authorization records
- **WHEN** operator verification is executed against `/Library/Application Support/com.apple.TCC/TCC.db`
- **THEN** audit queries SHALL verify `auth_value = 2` for all target client identifiers
- **AND** the report SHALL emit client identities, service names, and authorization integers without logging sensitive session tokens or system credentials
