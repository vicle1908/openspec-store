# Proposal: Remediate `replayd` `ScreenCaptureApprovals.plist` `NSDate` Crash Loop and Verify Remote Desktop TCC Provenance

## Why

AnyViewer (`com.aomei.mac.anyviewer`, v3.6.0) froze on its main thread (`_dispatch_sema4_timedwait` inside `SLSDisplayStreamCreateProxying`) and popped up a false "Privacy & Security Settings" dialog claiming Screen Recording permission was missing, even though `/Library/Application Support/com.apple.TCC/TCC.db` already held `auth_value = 2` across `kTCCServiceAccessibility`, `kTCCServiceScreenCapture`, and `kTCCServiceSystemPolicyAllFiles`. Simultaneously, RealVNC Server Agent (`com.realvnc.vncagent`) crashed with `SIGSEGV` inside `+[SCShareableContent createShareableContentWithWindows:displays:applications:withCompletionHandler:]` (`vncagent-2026-10-23-063619.ips`).

Root-cause investigation showed that 30 date fields (`kScreenCapturePrivacyHintDate` and `kScreenCaptureApprovalLastAlerted` across 15 client entries) in `~/Library/Group Containers/group.com.apple.replayd/ScreenCaptureApprovals.plist` had been written as `<string>` (`__NSCFString`, `"3026-01-01 00:00:00 +0000"`) instead of plist `<date>` (`NSDate`). Whenever `/usr/libexec/replayd` (`gui/502/com.apple.replayd`) evaluated `-[SCAlertStatsManager requirePrivacyHintWithCanonicalBundleID:auditToken:]`, it invoked `[[NSDate date] timeIntervalSinceDate:hintDate]`, which sent `timeIntervalSinceReferenceDate` to `__NSCFString` and aborted `replayd` with `NSInvalidArgumentException` (`SIGABRT`, 61 successive crashes). `launchd` throttled `com.apple.replayd` into `state = spawn scheduled` (`minimum runtime = 1200`), causing every synchronous `CGDisplayStreamCreateWithDispatchQueue` / `SLSDisplayStreamCreateProxying` request to block until timeout.

## What Changes

1. **`ScreenCaptureApprovals.plist` Type Normalization & `replayd` Recovery**:
   - Convert all 30 string-typed date entries (`kScreenCapturePrivacyHintDate`, `kScreenCaptureApprovalLastAlerted`, `kScreenCaptureApprovalLastUsed`) in `~/Library/Group Containers/group.com.apple.replayd/ScreenCaptureApprovals.plist` from `<string>` (`__NSCFString`) to native plist `<date>` (`NSDate` / `datetime.datetime`).
   - Flush `cfprefsd`, verify `gui/502/com.apple.replayd` transitions to `state = running`, and dismiss the stale AnyViewer permission sheet.
2. **Remote Desktop Suite (`AnyViewer`, `TeamViewer`, `RealVNC`) TCC & Runtime Provenance Audit**:
   - Verify active `auth_value = 2` TCC records and native `Security.framework` `SecStaticCodeCheckValidity` (`csreq`) compliance across AnyViewer (`com.aomei.mac.anyviewer`), TeamViewer (`com.teamviewer.TeamViewer`), and RealVNC (`com.realvnc.vncagent`, `/Library/vnc/vncagent`, `com.realvnc.vncserver_service`), while explicitly classifying legacy uninstalled bundle identifiers (`com.realvnc.vncconnect`, `com.realvnc.vncviewer`) as unverified stale rows.
3. **Specification, Documentation, and Knowledge Base Updates**:
   - Add a normative requirement in `openspec/specs/workstation-remote-and-agent-permissions/spec.md` requiring any date fields in `ScreenCaptureApprovals.plist` to be valid plist `<date>` (`NSDate`) objects so `replayd` never crashes with `NSInvalidArgumentException`, and requiring remote desktop TCC audits to distinguish verified installed bundle/path identities from stale uninstalled bundle IDs.
   - Document the `replayd` `NSDate` invariant and remote desktop suite verification in `docs/mac-development-setup.md` and `wiki/concepts/workstation-terminal-and-storage-resilience.md`.

## Impact

- **Affected Specs**: `workstation-remote-and-agent-permissions`
- **Affected Files**:
  - `~/Library/Group Containers/group.com.apple.replayd/ScreenCaptureApprovals.plist` (external workstation state)
  - `docs/mac-development-setup.md`
  - `~/Developer/wiki/concepts/workstation-terminal-and-storage-resilience.md`
