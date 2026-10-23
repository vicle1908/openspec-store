# Evidence: Remediate `replayd` `ScreenCaptureApprovals.plist` `NSDate` Crash Loop and Verify Remote Desktop TCC Provenance

## 1. `replayd` Crash Loop Diagnosis & `ScreenCaptureApprovals.plist` Remediation

- **AnyViewer Main-Thread Stack Sample (`sample 41429 1` before fix)**:
  - `AnyViewer` (`PID 41429`, `/Applications/AnyViewer.app/Contents/MacOS/AnyViewer`, `com.aomei.mac.anyviewer` v3.6.0) was blocked on the main thread at `0x1009f05a8` $\rightarrow$ `SLDisplayStreamCreateWithDispatchQueue` $\rightarrow$ `SLDisplayStreamCreate` $\rightarrow$ `SLSDisplayStreamCreateProxying` $\rightarrow$ `_dispatch_sema4_timedwait`.
  - Unified log showed `AnyViewer[41429:1b968b] (ScreenCaptureKit) [ERROR] SLSDisplayStreamCreateProxying:63 unable to complete due to timeout` followed by `-[RPDaemonProxy proxyCoreGraphicsWithMethodType:config:machPort:completionHandler:]:1336`.
- **`replayd` Crash Report (`~/Library/Logs/DiagnosticReports/replayd-2026-10-22-155159.ips`) & Disassembly (`/usr/libexec/replayd` `0x100005344`)**:
  - `launchctl print gui/502/com.apple.replayd` reported `state = spawn scheduled`, `runs = 61`, `successive crashes = 61`, `last terminating signal = Abort trap: 6`.
  - Exception reason: `NSInvalidArgumentException: -[__NSCFString timeIntervalSinceReferenceDate]: unrecognized selector sent to instance` inside `-[NSDate timeIntervalSinceDate:]` called from `-[SCAlertStatsManager requirePrivacyHintWithCanonicalBundleID:auditToken:]`.
- **Remediation & Post-Fix Verification**:
  - Converted 30 string-typed date fields (`"3026-01-01 00:00:00 +0000"`) across 15 app entries in `~/Library/Group Containers/group.com.apple.replayd/ScreenCaptureApprovals.plist` to native plist `<date>` (`NSDate` / `datetime.datetime(3026, 1, 1, 0, 0)`).
  - Verified `plutil -lint ~/Library/Group\ Containers/group.com.apple.replayd/ScreenCaptureApprovals.plist` returned `OK` and `Non-NSDate date fields remaining: 0 []`.
  - Verified `launchctl print gui/502/com.apple.replayd` transitioned to `state = running` (`pid = 58241`, `runs = 62`) and updated `com.aomei.mac.anyviewer` `kScreenCaptureAlertableUsageCount` from `8202` to `8257` (`kScreenCaptureApprovalLastUsed = 2026-10-22 23:56:42 +0000`).
  - Captured screenshot and AX tree of AnyViewer window `1179` confirming **Accessibility: Enabled**, **Screen Recording: Enabled**, and **Full Disk Access: Enabled**, dismissed window `1179`, and confirmed main window `1171` and main thread (`sample 41429 1`) are idle in `mach_msg2_trap`.

## 2. Remote Desktop TCC Provenance & Runtime Audit (`AnyViewer`, `TeamViewer`, `RealVNC`)

- **Native `Security.framework` `SecStaticCodeCheckValidity` Results**:
  - `com.aomei.mac.anyviewer` (`type=0`, `/Applications/AnyViewer.app`): `kTCCServiceAccessibility`, `kTCCServiceScreenCapture`, `kTCCServiceSystemPolicyAllFiles` $\rightarrow$ `auth_value = 2`, `check = 0`.
  - `com.teamviewer.TeamViewer` (`type=0`, `/Applications/TeamViewer.app`): `kTCCServiceAccessibility`, `kTCCServiceScreenCapture`, `kTCCServiceSystemPolicyAllFiles`, `kTCCServiceRemoteDesktop` $\rightarrow$ `auth_value = 2`, `check = 0`. Active processes: `PID 315` (`TeamViewer_Service -Module Full`, `ESTABLISHED` to `217.146.12.134:5938`) and `PID 3380` (`TeamViewer -RunAsAgent YES`, main thread idle in `mach_msg2_trap`).
  - `com.realvnc.vncagent` (`type=0`) and `/Library/vnc/vncagent` (`type=1`, `/Library/vnc/RealVNC Server Agent.app`): `kTCCServiceAccessibility`, `kTCCServiceScreenCapture`, `kTCCServiceSystemPolicyAllFiles` $\rightarrow$ `auth_value = 2`, `check = 0`.
  - `com.realvnc.vncserver_service` (`type=0`, `/Applications/RealVNC/RealVNC Server.app`): `kTCCServiceScreenCapture` $\rightarrow$ `auth_value = 2`, `check = 0`.
  - Active RealVNC processes: `PID 379` (`/Library/vnc/vncserver -service`, `ESTABLISHED` to `212.119.29.135:443`), `PID 39451` (`vncagent service`), and `PID 39461` (`vncserverui service`), all idle in `mach_msg2_trap`.
  - Legacy unmatched rows in `TCC.db`: `com.realvnc.vncconnect` (`kTCCServiceSystemPolicyAllFiles`) and `com.realvnc.vncviewer` (`kTCCServiceAccessibility`) are classified as `UNINSTALLED_LEGACY_ID` (no installed bundle carries those IDs; `/Library/vnc/RealVNC Server.app` is `com.realvnc.vncserverui` and `/Applications/RealVNC Connect Viewer.app` is `com.realvnc.rvncconnect`).
