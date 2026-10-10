# Tasks

## 1. Python Automation Runtime Permission Verification

- [x] 1.1 Verify Python Accessibility permission via `ApplicationServices.AXIsProcessTrusted()` evaluating to true
- [x] 1.2 Verify Python Full Disk Access via directory read against protected `/Library/Application Support/com.apple.TCC`
- [x] 1.3 Verify Python Screen Recording / Quartz display bounds access via `CoreGraphics.framework`

## 2. Ruby Automation Runtime Permission Verification

- [x] 2.1 Verify Ruby Accessibility permission via `ApplicationServices.AXIsProcessTrusted()` evaluating to true
- [x] 2.2 Verify Ruby Full Disk Access via directory read against protected `/Library/Application Support/com.apple.TCC`
- [x] 2.3 Verify Ruby CoreGraphics display ID and bounds queries via dynamic library bindings

## 3. OMP Computer-Use Harness Verification

- [x] 3.1 Verify OMP computer capabilities report (`capturePermission: granted`, `inputPermission: granted`, `axPermission: granted`)
- [x] 3.2 Verify live window enumeration and accessibility tree inspection via `computer.windows()` and `win.ax()`
- [x] 3.3 Verify synthetic input posting and screen buffer capture via `computer.screenshot()` and `computer.click()`

## 4. OpenSpec Spec Synchronization & Archive

- [x] 4.1 Synchronize delta spec to canonical `workstation-remote-and-agent-permissions` main spec
- [x] 4.2 Record verification evidence ledger in `evidence.md`
- [x] 4.3 Validate and archive change in `openspec-store`
