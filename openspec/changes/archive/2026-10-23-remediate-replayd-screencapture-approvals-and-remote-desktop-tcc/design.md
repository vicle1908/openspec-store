# Design: Remediate `replayd` `ScreenCaptureApprovals.plist` `NSDate` Crash Loop and Verify Remote Desktop TCC Provenance

## Context

On macOS 27.0.1 (`26A434`), ScreenCaptureKit and legacy `CGDisplayStreamCreateWithDispatchQueue` calls proxy through `SLSDisplayStreamCreateProxying` over XPC to the per-user LaunchAgent `gui/502/com.apple.replayd` (`/usr/libexec/replayd`).

During a prior manual plist edit (`2026-10-15-workstation-tcc-permission-provisioning`), `kScreenCapturePrivacyHintDate` and `kScreenCaptureApprovalLastAlerted` in `~/Library/Group Containers/group.com.apple.replayd/ScreenCaptureApprovals.plist` were written as XML `<string>3026-01-01 00:00:00 +0000</string>` rather than `<date>3026-01-01T00:00:00Z</date>`.

Disassembly of `/usr/libexec/replayd` (`0x100005344` in `-[SCAlertStatsManager requirePrivacyHintWithCanonicalBundleID:auditToken:]`) shows:
1. `replayd` loads the client's dictionary from `ScreenCaptureApprovals.plist` and fetches `objectForKey:@"kScreenCapturePrivacyHintDate"` into `x20`.
2. It calls `+[NSDate date]` (`x21`) and invokes `-[NSDate timeIntervalSinceDate:x20]` (`0x1000053c8`).
3. `-[NSDate timeIntervalSinceDate:]` immediately sends `-timeIntervalSinceReferenceDate` to its argument (`x20`).
4. Because `x20` was deserialized from `<string>` as `__NSCFString`, Objective-C raises `NSInvalidArgumentException: -[__NSCFString timeIntervalSinceReferenceDate]: unrecognized selector sent to instance`, terminating `replayd` with `SIGABRT` (`Abort trap: 6`).

After repeated crashes (`runs = 61`, `successive crashes = 61`), `launchd` enforces `minimum runtime = 1200` seconds and holds `gui/502/com.apple.replayd` in `state = spawn scheduled`. While `replayd` is down:
- **AnyViewer (`com.aomei.mac.anyviewer`, PID `41429`)** calls `CGDisplayStreamCreateWithDispatchQueue` on the main thread (`0x1000a8554`) to check Screen Recording permission. `SLSDisplayStreamCreateProxying` blocks on `_dispatch_sema4_timedwait` for 5 seconds, freezing the main Cocoa run loop and Accessibility responsiveness, then times out and returns `NULL`, causing AnyViewer to display its modal "Privacy & Security Settings" window (`window 1179`) reporting missing Screen Recording permission.
- **RealVNC Server Agent (`com.realvnc.vncagent`)** crashes with `SIGSEGV` (`KERN_INVALID_ADDRESS at 0x30`) in its `SCShareableContent` completion handler when `replayd` aborts mid-XPC reply.

## Decisions

### Decision 1: Enforce Plist `<date>` (`NSDate`) Serialization in `ScreenCaptureApprovals.plist`
- **Action**: Parse any string-typed date values (`kScreenCapturePrivacyHintDate`, `kScreenCaptureApprovalLastAlerted`, `kScreenCaptureApprovalLastUsed`) in `~/Library/Group Containers/group.com.apple.replayd/ScreenCaptureApprovals.plist` into `datetime.datetime` objects and serialize via `plistlib.dumps(..., fmt=plistlib.FMT_XML)` so every timestamp is stored as `<date>...</date>` (`NSDate`).
- **Rationale**: Preserves the existing timestamps while satisfying `-[NSDate timeIntervalSinceDate:]`'s type contract in `/usr/libexec/replayd`. No background daemon or recurring plist-rewrite job is introduced.

### Decision 2: Exact Bundle-Path Resolution & Stale-Identifier Classification for Remote Desktop TCC Audits
- **Action**: Evaluate `SecStaticCodeCheckValidity` against the exact installed bundle or Mach-O path for each active remote desktop component:
  - `com.aomei.mac.anyviewer` (`client_type = 0`) $\rightarrow$ `/Applications/AnyViewer.app` (`Accessibility`, `ScreenCapture`, `SystemPolicyAllFiles`).
  - `com.teamviewer.TeamViewer` (`client_type = 0`) $\rightarrow$ `/Applications/TeamViewer.app` (`Accessibility`, `ScreenCapture`, `SystemPolicyAllFiles`, `RemoteDesktop`).
  - `com.realvnc.vncagent` (`client_type = 0`) & `/Library/vnc/vncagent` (`client_type = 1`) $\rightarrow$ `/Library/vnc/RealVNC Server Agent.app` (`Accessibility`, `ScreenCapture`, `SystemPolicyAllFiles`).
  - `com.realvnc.vncserver_service` (`client_type = 0`) $\rightarrow$ `/Applications/RealVNC/RealVNC Server.app` (`ScreenCapture`).
  - Explicitly classify `com.realvnc.vncconnect` and `com.realvnc.vncviewer` as **unverified legacy rows** because no installed bundle on disk carries those `CFBundleIdentifier` values (`/Library/vnc/RealVNC Server.app` is `com.realvnc.vncserverui`, and `/Applications/RealVNC Connect Viewer.app` is `com.realvnc.rvncconnect`).
- **Rationale**: Prevents false `check = 0` claims when an installed bundle has a different `CFBundleIdentifier` than a historical TCC row.
