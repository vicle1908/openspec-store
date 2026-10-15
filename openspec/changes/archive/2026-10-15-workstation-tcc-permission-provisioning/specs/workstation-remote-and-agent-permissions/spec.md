# Delta Specification: workstation-remote-and-agent-permissions

## ADDED Requirements

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
