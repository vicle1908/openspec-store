# workstation-remote-and-agent-permissions Delta Specification

## ADDED Requirements

### Requirement: Application termination routines for maintenance SHALL use POSIX signals and avoid AppleEvents

Workstation automation harnesses and maintenance pipelines SHALL terminate GUI and daemon processes exclusively using POSIX termination signals (`SIGTERM` followed by bounded timeout and `SIGKILL`) rather than AppleEvents automation (`osascript -e 'quit app ...'`), avoiding `kTCCServiceAppleEvents` permission prompts in macOS TCC.

#### Scenario: Graceful application shutdown via POSIX termination signals
- **WHEN** an automated pipeline or operator script requires quitting an application prior to cask upgrade
- **THEN** it SHALL issue `pkill -TERM -x "<binary>"` (or process-specific PID termination)
- **AND** it SHALL poll for process exit using non-blocking signals within a defined timeout (e.g., 5 seconds)
- **AND** it SHALL NOT execute AppleScript or `osascript` quit commands that require `com.apple.security.automation.apple-events` entitlements or trigger user dialogs

#### Scenario: Non-interactive vendor uninstaller execution
- **WHEN** a Homebrew cask upgrade invokes a vendor-provided uninstallation script containing interactive confirmation prompts
- **THEN** the pipeline SHALL supply explicit non-interactive flags or configure non-interactive bypass variables
- **AND** the uninstallation SHALL complete without blocking on standard input or timing out

### Requirement: Application bundle upgrades SHALL preserve permanent bundle attribution under client_type 0

When macOS application bundles subject to TCC controls (such as `ChatGPT.app`, `Orca.app`, `Goose.app`, `Hermes.app`) are updated or replaced through Homebrew Casks or manual staging, they SHALL preserve their canonical bundle identifiers and code signing requirements registered under `client_type = 0` in `TCC.db`.

#### Scenario: Post-upgrade TCC bundle verification
- **WHEN** an application cask upgrade completes in `/Applications`
- **THEN** `tcc_provenance.py --bundles` SHALL verify that the application's executable path exists, its code signature matches the stored requirement, and its entry in `TCC.db` evaluates to `client_type = 0`
- **AND** the verifier SHALL report status `CLEAN` with zero missing binaries or permission drift
