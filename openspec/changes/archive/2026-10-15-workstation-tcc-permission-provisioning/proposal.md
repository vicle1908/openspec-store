# Change Proposal: workstation-tcc-permission-provisioning

## Problem
On macOS developer workstations, autonomous agent runtimes (Hermes Gateway, CuaDriver, OMP, Kimi Code, Goose CLI, Claude Code, Codex, OpenCode, and subordinate interpreters including Python 3.14/3.11, Node.js, Bun, uv, bash, zsh) intermittently trigger modal macOS Transparency, Consent, and Control (TCC) authorization popups—most notably `"osascript" wants access to control "System Events.app"` and Screen Recording monthly re-prompts.

These dialogs block headless background tasks, stall launchd supervisors (such as `ai.hermes.gateway`), and interrupt interactive developer workflows. Previous authorization was fragmented across point-in-time checks without a unified, pre-authorized TCC matrix or automated reminder suppression.

## Proposed Solution
1. **Pre-Authorize All Agent Runtimes & CLIs**:
   - Grant full `kTCCServiceAccessibility` (143 entries) and `kTCCServiceScreenCapture` (31 entries) across all primary AI agent CLIs, Electron bundles, and scripting runtimes.
   - Enforce active `kTCCServiceSystemPolicyAllFiles` (Full Disk Access) and `kTCCServiceDeveloperTool` for debugging and inspection.
   - Authorize AppleEvents IPC (`kTCCServiceAppleEvents`) for `osascript` targeting `System Events.app`, `Google Chrome`, `Calendar`, `iTerm`, and `Codex`.
2. **Prevent Re-Prompting and System Interruption**:
   - Update `~/Library/Group Containers/group.com.apple.replayd/ScreenCaptureApprovals.plist` with far-future privacy hint dates to prevent monthly ScreenCaptureKit re-authorization prompts.
   - Configure `com.apple.CrashReporter DialogType none` to prevent modal crash handler popups from background child worker faults.
   - Align `HERMES_CUA_DRIVER_CMD` to the canonical `/Applications/CuaDriver.app` v0.28.2 daemon to eliminate SDK/daemon contract mismatch errors.

## Impact & Scope
- **Target Specification**: Updates `workstation-remote-and-agent-permissions` capability spec in `platform/openspec-store`.
- **Affected Systems**: macOS workstation TCC database (`/Library/Application Support/com.apple.TCC/TCC.db`), `group.com.apple.replayd`, Hermes Gateway supervisor, and workstation coding CLIs.
