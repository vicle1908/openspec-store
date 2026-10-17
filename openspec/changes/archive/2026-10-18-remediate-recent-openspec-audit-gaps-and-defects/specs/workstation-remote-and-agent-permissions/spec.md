# workstation-remote-and-agent-permissions Specification Delta

## ADDED Requirements

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
