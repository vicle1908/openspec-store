# Verification Evidence

## Workstation Remote Access & Agent Privacy Permissions

### 1. AnyDesk Reinstallation & Single-Version State

- **Homebrew Cask Reinstall**: `brew reinstall --cask anydesk` exited 0.
- **Installed Version**: AnyDesk 9.8.1 (`CFBundleShortVersionString` and `CFBundleVersion` = `9.8.1`).
- **Filesystem Search**:
  - `mdfind "kMDItemFSName == 'AnyDesk.app'"`: exactly `/Applications/AnyDesk.app`.
  - `mdfind "kMDItemCFBundleIdentifier == 'com.philandro.anydesk*'"`: exactly `/Applications/AnyDesk.app`.
- **Caskroom**: `/opt/homebrew/Caskroom/anydesk/9.8.0` (tracking directory).
- **Background Daemons & Helpers**:
  - `/Library/LaunchAgents/com.philandro.anydesk.Frontend.plist` (mode 0644, root:wheel)
  - `/Library/LaunchDaemons/com.philandro.anydesk.Helper.plist` (mode 0644, root:wheel)
  - `/Library/LaunchDaemons/com.philandro.anydesk.service.plist` (mode 0644, root:wheel)
  - `/Library/PrivilegedHelperTools/com.philandro.anydesk.Helper` (mode 0544, root:wheel)
  - `launchctl list | grep anydesk`: `com.philandro.anydesk.service` and `com.philandro.anydesk.Helper` active.

### 2. macOS TCC System Database Records (`/Library/Application Support/com.apple.TCC/TCC.db`)

Value-blind query output (`auth_value = 2` signifies `ALLOWED`):

```
kTCCServiceAccessibility|com.philandro.anydesk|2
kTCCServiceSystemPolicyAllFiles|com.philandro.anydesk|2
kTCCServiceScreenCapture|com.philandro.anydesk|2
kTCCServiceAccessibility|com.stablyai.orca|2
kTCCServiceScreenCapture|com.stablyai.orca|2
kTCCServiceSystemPolicyAllFiles|com.stablyai.orca|2
kTCCServiceAccessibility|com.stablyai.orca.computer-use|2
kTCCServiceScreenCapture|com.stablyai.orca.computer-use|2
kTCCServiceSystemPolicyAllFiles|com.stablyai.orca.computer-use|2
kTCCServiceAccessibility|com.openai.codex|2
kTCCServiceScreenCapture|com.openai.codex|2
kTCCServiceSystemPolicyAllFiles|com.openai.codex|2
kTCCServiceAccessibility|com.openai.chat|2
kTCCServiceAccessibility|com.openai.sky.CUAService|2
kTCCServiceScreenCapture|com.openai.sky.CUAService|2
kTCCServiceAccessibility|com.codexuse.desktop|2
```

### 3. Agent Execution Capabilities Verification

- **OMP Computer-Use Capability Probe**:
  - `backend`: `quartz`
  - `capturePermission`: `granted`
  - `inputPermission`: `granted`
  - `axPermission`: `granted`
- **UI State**: AnyDesk System Permissions Status window resolved and closed; zero pending modal permission prompts.
