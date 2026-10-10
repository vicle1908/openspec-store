# Tasks

## 1. AnyDesk Clean Reinstallation & Single-Version Verification

- [x] 1.1 Reinstall AnyDesk via Homebrew Cask (`brew reinstall --cask anydesk`) to fetch latest upstream release 9.8.1
- [x] 1.2 Verify exact single-version bundle integrity on filesystem (`/Applications/AnyDesk.app` 9.8.1, zero shadow bundles or obsolete casks)
- [x] 1.3 Verify AnyDesk background services (`com.philandro.anydesk.service` and privileged helper `com.philandro.anydesk.Helper`) under launchd

## 2. AnyDesk macOS TCC Permissions

- [x] 2.1 Grant and verify Accessibility permission (`kTCCServiceAccessibility`) in system TCC
- [x] 2.2 Grant and verify Full Disk Access permission (`kTCCServiceSystemPolicyAllFiles`) in system TCC
- [x] 2.3 Grant and verify Screen Recording permission (`kTCCServiceScreenCapture`) in system TCC
- [x] 2.4 Verify AnyDesk System Permissions Status reports all permissions active with no blocking dialogs

## 3. Workstation AI Coding Agents Permission Verification

- [x] 3.1 Verify Orca permissions (`com.stablyai.orca` & `com.stablyai.orca.computer-use`) across Accessibility, Screen Recording, and Full Disk Access
- [x] 3.2 Verify ChatGPT permissions (`com.openai.codex` / `com.openai.chat`) across Accessibility, Screen Recording, and Full Disk Access
- [x] 3.3 Verify Codex permissions (`com.openai.sky.CUAService`, `com.codexuse.desktop`, and CLI) across Accessibility and Screen Recording
- [x] 3.4 Verify OMP execution environment and computer-use agent capabilities (Quartz backend, input/ax/capture permissions granted)
