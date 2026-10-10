# Proposal

## Why

Workstation remote access and AI agent automation tools require strict single-version package management and verified macOS Transparency, Consent, and Control (TCC) permissions to function reliably without orphaned background processes, conflicting binaries, or blocked screen/input capture. AnyDesk required reinstallation to the latest upstream release via Homebrew Cask, single-version verification, and full permission grants, alongside auditing and ensuring complete permissions for core coding agents (Orca, OMP, ChatGPT, and Codex).

## What Changes

- Reinstall AnyDesk via Homebrew Cask (`anydesk`) to the latest upstream release (`9.8.1`), ensuring exact single-version installation on the host filesystem.
- Establish running background services for AnyDesk (`com.philandro.anydesk.service` and privileged helper `com.philandro.anydesk.Helper`).
- Grant and verify complete macOS TCC permissions for AnyDesk: Accessibility (`kTCCServiceAccessibility`), Screen Recording (`kTCCServiceScreenCapture`), and Full Disk Access (`kTCCServiceSystemPolicyAllFiles`).
- Audit and grant all required macOS TCC privacy permissions for primary AI coding assistants and automation harnesses: Orca (`com.stablyai.orca`), OMP (`omp-darwin-arm64`), ChatGPT (`com.openai.codex`), and Codex (`com.openai.sky.CUAService`, `com.codexuse.desktop`, and CLI).
- Provide verifiable runtime evidence confirming `auth_value = 2` (Allowed) in system TCC and zero remaining conflicting versions or pending permission sheets.

## Capabilities

### New Capabilities
- `workstation-remote-and-agent-permissions`: Governs installation single-version invariants, official package manager authority, and macOS TCC permission state for remote desktop tooling and AI coding assistant execution environments.

### Modified Capabilities
<!-- None -->

## Impact

- Affected systems: Host macOS workstation (`/Applications`, `/Library/Application Support/com.apple.TCC/TCC.db`, `/Library/LaunchDaemons`, `/Library/PrivilegedHelperTools`).
- Dependencies: Homebrew Caskroom, macOS Quartz WindowServer, Apple TCC daemon.
- Non-goals: Modifying SIP status, altering enterprise MDM profiles, or managing unrelated third-party screen sharing tools.
