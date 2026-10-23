# Tasks: Remediate `replayd` `ScreenCaptureApprovals.plist` `NSDate` Crash Loop and Verify Remote Desktop TCC Provenance

- [x] 1. Diagnose AnyViewer main-thread hang and `com.apple.replayd` crash loop <!-- id: 1 -->
  - [x] 1.1 Sample AnyViewer (`PID 41429`) and inspect unified logs + `replayd` crash reports (`replayd-2026-10-22-155159.ips`), identifying `SLSDisplayStreamCreateProxying` timeouts caused by `-[__NSCFString timeIntervalSinceReferenceDate]` `SIGABRT` in `/usr/libexec/replayd` <!-- id: 1.1 -->
  - [x] 1.2 Convert all 30 string-typed date fields in `~/Library/Group Containers/group.com.apple.replayd/ScreenCaptureApprovals.plist` to native plist `<date>` (`NSDate`) values, validate with `plutil -lint`, flush `cfprefsd`, and verify `gui/502/com.apple.replayd` runs (`PID 58241`) without crashes <!-- id: 1.2 -->
  - [x] 1.3 Dismiss AnyViewer's stale "Privacy & Security Settings" sheet (`window 1179`) after confirming all 3 indicators show `Enabled`, and verify `window 1171` responsiveness and main-thread idle state (`sample 41429 1`) <!-- id: 1.3 -->
- [x] 2. Audit TeamViewer and RealVNC TCC provenance and runtime health <!-- id: 2 -->
  - [x] 2.1 Verify TeamViewer (`PID 315` `TeamViewer_Service`, `PID 3380` `TeamViewer`) and RealVNC (`PID 379` `vncserver`, `PID 39451` `vncagent`, `PID 39461` `vncserverui`) process health, network sockets, and main-thread samples <!-- id: 2.1 -->
  - [x] 2.2 Validate `TCC.db` `csreq` blobs via `SecStaticCodeCheckValidity` across `com.aomei.mac.anyviewer`, `com.teamviewer.TeamViewer`, `com.realvnc.vncagent`, `/Library/vnc/vncagent`, and `com.realvnc.vncserver_service`, and classify `com.realvnc.vncconnect` / `com.realvnc.vncviewer` as unverified legacy rows <!-- id: 2.2 -->
- [x] 3. Update OpenSpec specs, workstation documentation, and wiki <!-- id: 3 -->
  - [x] 3.1 Author delta spec for `workstation-remote-and-agent-permissions` and update `docs/mac-development-setup.md` and `wiki/concepts/workstation-terminal-and-storage-resilience.md` <!-- id: 3.1 -->
  - [x] 3.2 Validate change with `openspec validate remediate-replayd-screencapture-approvals-and-remote-desktop-tcc --strict --json --store openspec-store`, archive change, and verify archive readiness <!-- id: 3.2 -->
