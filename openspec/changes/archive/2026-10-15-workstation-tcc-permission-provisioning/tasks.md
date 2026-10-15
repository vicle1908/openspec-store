# Implementation Tasks: workstation-tcc-permission-provisioning

## 1. Audit and TCC Enrollment

- [x] 1.1 Audit current TCC database and LaunchAgent supervisor wrappers for osascript, Hermes, and workstation CLIs.
- [x] 1.2 Programmatically register missing Accessibility (`kTCCServiceAccessibility`) entries for Hermes, runtimes, and CLIs.
- [x] 1.3 Toggle and commit Accessibility entries in System Settings to `auth_value = 2`.

## 2. Screen Recording and Privacy Alert Suppression

- [x] 2.1 Register and commit Screen Recording (`kTCCServiceScreenCapture`) authorizations for all agents and CLIs.
- [x] 2.2 Update `ScreenCaptureApprovals.plist` in `group.com.apple.replayd` with far-future privacy hint timestamps.
- [x] 2.3 Configure `com.apple.CrashReporter DialogType none` to suppress modal crash windows.

## 3. Automation and Service Verification

- [x] 3.1 Verify AppleEvents IPC authorizations (`kTCCServiceAppleEvents`) for `osascript` targeting System Events and browsers.
- [x] 3.2 Align CuaDriver execution path to `/Applications/CuaDriver.app` v0.28.2 and verify direct capture readiness.
- [x] 3.3 Execute non-interactive verification across OMP, Hermes, Kimi, Goose, Claude, Codex, OpenCode, and Pi.
