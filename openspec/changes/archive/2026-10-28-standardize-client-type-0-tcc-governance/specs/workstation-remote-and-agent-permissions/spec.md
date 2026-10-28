# Spec Delta: workstation-remote-and-agent-permissions

## MODIFIED Requirements

### Requirement: Post-upgrade TCC provenance reconciliation SHALL keep active CLI binaries authorized

Workstation TCC governance SHALL enforce `client_type = 0` (`CFBundleIdentifier`) bundle attribution and responsible-supervisor delegation as the authoritative authorization model in `/Library/Application Support/com.apple.TCC/TCC.db` across `kTCCServiceAccessibility`, `kTCCServiceScreenCapture`, and `kTCCServiceSystemPolicyAllFiles`, eliminating permissions drift caused by versioned directory rotation of `client_type = 1` Mach-O realpaths during automated toolchain upgrades.

#### Scenario: Active upgraded CLI realpaths are enrolled in TCC.db
- **WHEN** `realpath` is resolved for `/opt/homebrew/bin/omp`, `/opt/homebrew/bin/node` (backing `~/.pi/agent/bin/pi`), `/opt/homebrew/bin/opencode`, `/opt/homebrew/bin/goose`, `~/.local/bin/claude`, and `~/.kimi-code/bin/kimi`
- **THEN** each target identity SHALL be attributed to a verified `client_type = 0` bundle or registered Mach-O path with an active `auth_value = 2` record in `/Library/Application Support/com.apple.TCC/TCC.db` across `kTCCServiceAccessibility` and `kTCCServiceScreenCapture`
- **AND** `ScreenCaptureApprovals.plist` in `group.com.apple.replayd` SHALL maintain far-future (`3026-01-01`) suppression dates

#### Scenario: Scheduled maintenance detects TCC path drift after upgrades
- **WHEN** the daily workstation maintenance workflow upgrades Homebrew formulae or standalone agent CLIs on macOS
- **THEN** a read-only post-upgrade TCC provenance check SHALL verify that authoritative `client_type = 0` bundle identities and canonical agent paths retain verified `auth_value = 2` status in `TCC.db` without failing closed on expected package directory rotations
