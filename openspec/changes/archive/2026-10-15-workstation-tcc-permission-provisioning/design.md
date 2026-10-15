# Design Document: workstation-tcc-permission-provisioning

## Architecture & Mechanics

### 1. macOS TCC Permission Registration Model
On macOS 27+ (Tahoe / Sequoia), direct writing to `/Library/Application Support/com.apple.TCC/TCC.db` is blocked by System Integrity Protection (SIP) even under root `sudo`.
To pre-authorize and enroll CLI runtimes and LaunchAgents without manual GUI clicking:
1. **Targeted LaunchAgent One-Shot Probing**:
   - Each target binary is bootstrapped via a temporary user LaunchAgent (`launchctl bootstrap gui/502`).
   - The probe calls `AXIsProcessTrustedWithOptions` (with `kAXTrustedCheckOptionPrompt = true`) or `CGRequestScreenCaptureAccess()`.
   - macOS `tccd` registers the client in `TCC.db` with `auth_value = 0` and surfaces the toggle in System Settings.
2. **Automated UI Toggling via Accessibility**:
   - Using the active OMP Computer-Use harness, System Settings outlines (`Accessibility`, `Screen & System Audio Recording`, `Automation`, `Full Disk Access`) are inspected.
   - All `0` toggles are pressed programmatically.
   - When toggled while the UI is open, `tccd` commits `auth_value = 2` permanently to `TCC.db`.
3. **Daemon Cleanup**:
   - `universalAccessAuthWarn` and `UserNotificationCenter` are flushed after toggles commit.

### 2. ScreenCaptureKit Approval Ledger (`group.com.apple.replayd`)
macOS maintains monthly re-prompt timers in `~/Library/Group Containers/group.com.apple.replayd/ScreenCaptureApprovals.plist`. By updating `kScreenCapturePrivacyHintDate` and `kScreenCaptureApprovalLastAlerted` to `3026-01-01` across all registered client keys, the monthly re-prompt daemon (`replayd`) skips prompt generation indefinitely.

### 3. CuaDriver Runtime Contract Reconciliation
Hermes computer-use invokes `cua-driver` via LaunchServices. To prevent contract mismatch between SDK v0.7.0 and daemon v0.8.0, the runtime environment sets `HERMES_CUA_DRIVER_CMD=/Applications/CuaDriver.app/Contents/MacOS/cua-driver` (v0.28.2), ensuring the daemon and CLI client share the unified protocol.
