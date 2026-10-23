## ADDED Requirements

### Requirement: ScreenCaptureApprovals.plist date keys SHALL be serialized as native plist Date objects

All timestamp fields in `~/Library/Group Containers/group.com.apple.replayd/ScreenCaptureApprovals.plist` SHALL be serialized as native plist `<date>` (`NSDate`) objects rather than `<string>` values so `/usr/libexec/replayd` never aborts with `NSInvalidArgumentException`, and remote desktop TCC provenance audits SHALL distinguish verified installed identities from stale uninstalled bundle identifiers.

#### Scenario: ScreenCaptureApprovals.plist contains zero string-typed date values and replayd remains running
- **WHEN** `~/Library/Group Containers/group.com.apple.replayd/ScreenCaptureApprovals.plist` is inspected and `gui/502/com.apple.replayd` is queried
- **THEN** `plutil -lint` SHALL return `OK` and every `kScreenCapturePrivacyHintDate`, `kScreenCaptureApprovalLastAlerted`, and `kScreenCaptureApprovalLastUsed` entry SHALL deserialize as a native `NSDate` (`datetime.datetime`) object with `0` string-typed date fields
- **AND** `gui/502/com.apple.replayd` SHALL remain in `state = running` without `-[__NSCFString timeIntervalSinceReferenceDate]` `SIGABRT` crashes
- **AND** AnyViewer (`com.aomei.mac.anyviewer`) main-thread `CGDisplayStreamCreateWithDispatchQueue` checks SHALL complete without `SLSDisplayStreamCreateProxying` semaphore timeouts

#### Scenario: Remote desktop TCC provenance audit distinguishes verified installed binaries from stale legacy bundle IDs
- **WHEN** macOS TCC grants in `/Library/Application Support/com.apple.TCC/TCC.db` are audited for AnyViewer, TeamViewer, and RealVNC using `SecStaticCodeCheckValidity`
- **THEN** active installed identities (`com.aomei.mac.anyviewer` at `/Applications/AnyViewer.app`, `com.teamviewer.TeamViewer` at `/Applications/TeamViewer.app`, `com.realvnc.vncagent` and `/Library/vnc/vncagent` at `/Library/vnc/RealVNC Server Agent.app`, and `com.realvnc.vncserver_service` at `/Applications/RealVNC/RealVNC Server.app`) SHALL evaluate to `auth_value = 2` and `SecStaticCodeCheckValidity = 0`
- **AND** legacy TCC rows whose bundle identifiers match no installed bundle on disk (`com.realvnc.vncconnect` and `com.realvnc.vncviewer`) SHALL be reported as unverified stale rows rather than claimed as verified against mismatched bundles (`/Library/vnc/RealVNC Server.app` with `com.realvnc.vncserverui` or `/Applications/RealVNC Connect Viewer.app` with `com.realvnc.rvncconnect`)
