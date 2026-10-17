# workstation-remote-and-agent-permissions Specification

## Purpose

Defines workstation standards for remote access software, AI coding assistant runtimes, and scripting automation interpreters on macOS, enforcing single-version installation via Homebrew Cask, Gatekeeper quarantine bypass, and complete system TCC permissions across Accessibility, Screen Recording, Full Disk Access, and programmatic computer control.

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

### Requirement: Runtime scripting interpreters and host automation runners SHALL maintain full computer control permissions

Interpreters and automation harnesses executing on the workstation (Python, Ruby, OMP) SHALL maintain verified host permissions enabling unrestricted programmatic computer control, including accessibility tree inspection, synthetic event posting, screen buffer capture, and full filesystem traversal.

#### Scenario: Python automation runtime control verification
- **WHEN** Python automation scripts execute via host or `uv` environments (`cpython-3.11`, `cpython-3.12`)
- **THEN** `ApplicationServices.AXIsProcessTrusted()` SHALL evaluate to true
- **AND** CoreGraphics display bounds queries SHALL succeed without permission error
- **AND** reading protected directories such as `/Library/Application Support/com.apple.TCC` SHALL succeed under Full Disk Access

#### Scenario: Ruby automation runtime control verification
- **WHEN** Ruby automation scripts execute via Homebrew Ruby runtimes
- **THEN** `ApplicationServices.AXIsProcessTrusted()` SHALL evaluate to true
- **AND** CoreGraphics display ID and bounds queries SHALL succeed without permission error
- **AND** reading protected directories such as `/Library/Application Support/com.apple.TCC` SHALL succeed under Full Disk Access

#### Scenario: OMP native computer-use harness capability verification
- **WHEN** OMP computer-use APIs (`computer.capabilities()`, `computer.windows()`, `computer.screenshot()`, `computer.click()`, `win.ax()`) execute
- **THEN** the capability report SHALL indicate `capturePermission: "granted"`, `inputPermission: "granted"`, and `axPermission: "granted"`
- **AND** window enumeration, AX tree parsing, and synthetic input generation SHALL execute without runtime permission rejection

### Requirement: Homebrew Cask applications SHALL bypass Gatekeeper quarantine attributes

Developer workstations SHALL configure Homebrew Cask options to prevent the attachment of `com.apple.quarantine` extended attributes on installed bundles, and existing application bundles SHALL maintain zero quarantine metadata.

#### Scenario: Persistent Cask options configuration
- **WHEN** user and system shell sessions initialize (`~/.zshrc`, `~/.zprofile`)
- **THEN** `HOMEBREW_CASK_OPTS="--no-quarantine"` SHALL be exported
- **AND** `brew config` SHALL report `HOMEBREW_CASK_OPTS: ["--no-quarantine"]`

#### Scenario: Application bundle quarantine attribute elimination
- **WHEN** installed bundles in `/Applications` and `/opt/homebrew/Caskroom` are inspected via `xattr`
- **THEN** no `com.apple.quarantine` attribute SHALL be present
- **AND** launching applications SHALL execute directly without Gatekeeper download confirmation dialogs

### Requirement: Autonomous AI agents and developer toolchains SHALL maintain complete pre-authorized TCC privileges without modal prompts

All host AI coding assistants, supervisor LaunchAgents, and automation interpreters SHALL possess pre-authorized permissions across Accessibility, Screen Recording, Full Disk Access, and AppleEvents IPC in the macOS TCC store, eliminating interactive authorization dialogs during autonomous execution.

#### Scenario: Pre-authorized Accessibility and Screen Recording for all AI toolchains
- **WHEN** any registered coding assistant or runtime executes (`hermes`, `osascript`, `omp`, `kimi`, `goose`, `claude`, `codex`, `opencode`, `Cursor`, `CuaDriver`, `python3.14`, `python3.11`, `node`, `bun`, `uv`, `bash`, `zsh`)
- **THEN** `kTCCServiceAccessibility` SHALL evaluate to `auth_value = 2` (Allowed) in `/Library/Application Support/com.apple.TCC/TCC.db`
- **AND** `kTCCServiceScreenCapture` SHALL evaluate to `auth_value = 2` (Allowed) for all screen-capturing agents and drivers
- **AND** zero `universalAccessAuthWarn` or `UserNotificationCenter` authorization dialogs SHALL be raised.

#### Scenario: Persistent AppleEvents IPC authorization for osascript supervisor
- **WHEN** Hermes Gateway or scripting tasks execute AppleScript via `/usr/bin/osascript`
- **THEN** `kTCCServiceAppleEvents` SHALL maintain allowed authorization targeting `System Events.app`, `Google Chrome.app`, `Calendar.app`, `iTerm.app`, and `Codex Computer Use.app`
- **AND** queries to `System Events` for window hierarchy and process enumeration SHALL return exit code 0 without prompting.

#### Scenario: Suppression of periodic ScreenCaptureKit privacy alerts and crash dialogs
- **WHEN** ScreenCaptureKit verifies authorization under macOS
- **THEN** `ScreenCaptureApprovals.plist` in `group.com.apple.replayd` SHALL carry far-future hint dates preventing recurring monthly consent popups
- **AND** `com.apple.CrashReporter` SHALL maintain `DialogType = none` to prevent modal error alerts from background processes.

### Requirement: Post-upgrade TCC provenance reconciliation SHALL keep active CLI binaries authorized

Workstation TCC governance SHALL reconcile `/Library/Application Support/com.apple.TCC/TCC.db` after package or vendor upgrades so that active resolved Mach-O executables (`omp`, `node` covering shebang-wrapped `pi` and `codex`, `opencode`, `goose`, `claude`, and `kimi`) retain valid `auth_value = 2` grants in `kTCCServiceAccessibility` and `kTCCServiceScreenCapture`.

#### Scenario: Active upgraded CLI realpaths are enrolled in TCC.db
- **WHEN** `realpath` is resolved for `/opt/homebrew/bin/omp`, `/opt/homebrew/bin/node` (backing `~/.pi/agent/bin/pi`), `/opt/homebrew/bin/opencode`, `/opt/homebrew/bin/goose`, `~/.local/bin/claude`, and `~/.kimi-code/bin/kimi`
- **THEN** each resolved Mach-O executable path SHALL have an active `auth_value = 2` record in `/Library/Application Support/com.apple.TCC/TCC.db` across `kTCCServiceAccessibility` and `kTCCServiceScreenCapture`
- **AND** `ScreenCaptureApprovals.plist` in `group.com.apple.replayd` SHALL maintain far-future (`3026-01-01`) suppression dates

#### Scenario: Scheduled maintenance detects TCC path drift after upgrades
- **WHEN** the daily workstation maintenance workflow upgrades Homebrew formulae or standalone agent CLIs on macOS
- **THEN** a read-only post-upgrade TCC provenance check SHALL verify that all canonical Mach-O CLI realpaths remain authorized (`auth_value = 2`) in `TCC.db`

### Requirement: Hermes CUA driver environment variable SHALL point to the system-authorized application bundle

The workstation shell and Hermes runtime configuration SHALL persist `HERMES_CUA_DRIVER_CMD` pointing to `/Applications/CuaDriver.app/Contents/MacOS/cua-driver` so Hermes computer-use sessions invoke the TCC-authorized application bundle rather than legacy bundled tool paths.

#### Scenario: Hermes resolves the TCC-authorized CuaDriver binary
- **WHEN** `HERMES_CUA_DRIVER_CMD` is inspected in the workstation environment (`~/.zshenv` or `~/.hermes/.env`)
- **THEN** it SHALL resolve to `/Applications/CuaDriver.app/Contents/MacOS/cua-driver`
- **AND** `/Applications/CuaDriver.app` (`com.trycua.driver`) SHALL hold `auth_value = 2` in `TCC.db` for Accessibility and ScreenCapture
