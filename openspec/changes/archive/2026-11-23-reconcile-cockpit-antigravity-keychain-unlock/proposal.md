# Proposal

## Why

Cockpit Tools (`v1.4.2`) failed to switch Antigravity 2.0 (`v2.34.0`) accounts on `iosteam-mac-mini` because macOS `login.keychain-db` rejected all secret reads and writes with `errSecAuthFailed` (`-25293`) while `SecKeychainGetStatus` still reported unlocked status `0x7`.

When `securityd` (`PID 15590`) restarted mid-session after `loginwindow` (`PID 205`, Oct 22), `securityd` retained an apparent unlocked DB handle (`is unlocked; decoding for makeUnlocked()`) that failed decryption with `MacOS error: -25337` / `CSSMERR_CSP_INVALID_DATA (-2147415994)` and `CSSMERR_CSP_OPERATION_AUTH_DENIED (-2147416032)`. As a result, `security add-generic-password -U` inside Cockpit Tools failed at both `SecKeychainItemModifyContent` and `SecKeychainItemCreateFromContent (<default>)` with *"The user name or passphrase you entered is not correct"*, and `SecKeychainGetStatus` alone masked the failure.

## What Changes

- **Diagnose & Recover `login.keychain-db` / `securityd` Keychain Unlock State**:
  - Identified `security show-keychain-info ~/Library/Keychains/login.keychain-db` (`SecKeychainCopySettings`) as the authoritative non-mutating health probe that exposes `-25293` (`errSecAuthFailed`) when `SecKeychainGetStatus` misleadingly returns `0x7`.
  - Re-locked and unlocked `~/Library/Keychains/login.keychain-db` (`security lock-keychain` + `security unlock-keychain`) until `security show-keychain-info` reported `no-timeout`.
  - Verified Cockpit Tools (`v1.4.2`) **Switch only** and **Switch and launch** flows with **Antigravity 2.0 (`v2.34.0`)** (`baohiendung326@gmail.com`), confirming `service="gemini"`, `account="antigravity"` updated in `login.keychain-db` and Antigravity Desktop (`PID 75977`) launched cleanly.
- **Extend OpenSpec Governance & Workstation Runbook**:
  - Extend `workstation-remote-and-agent-permissions` with a requirement and scenarios governing authoritative `SecKeychainCopySettings` (`security show-keychain-info`) Keychain health probing and Antigravity 2.0 / Cockpit Tools Keychain write verification.
  - Document the diagnostic signature (`SecKeychainGetStatus == 0x7` vs `SecKeychainCopySettings == -25293` / `securityd -25337`) and recovery sequence in `platform/openspec-store/docs/mac-development-setup.md` and `~/Developer/wiki/concepts/workstation-terminal-and-storage-resilience.md`.

### Non-Goals

- Modifying Cockpit Tools (`Cockpit Tools.app`) or Antigravity (`Antigravity.app`) application binaries.
- Modifying `scripts/workstation-daily-update.sh` (which has concurrent external edits in the shared workspace).
- Replacing Antigravity 2.0's native macOS Keychain storage (`service="gemini"`, `account="antigravity"`) with file-backed credentials.
- Resetting or deleting `~/Library/Keychains/login.keychain-db`.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `workstation-remote-and-agent-permissions`: Require authoritative `SecKeychainCopySettings` (`security show-keychain-info`) verification rather than `SecKeychainGetStatus` alone when diagnosing macOS Keychain write failures (`errSecAuthFailed -25293` / `securityd -25337`), and codify recovery + Cockpit Tools / Antigravity 2.0 credential write verification.

## Impact

- **Affected Ownership Boundaries**:
  - `platform/openspec-store` (`openspec/specs/workstation-remote-and-agent-permissions/spec.md`, `openspec/changes/...`, `docs/mac-development-setup.md`)
  - `~/Developer/wiki` (`concepts/workstation-terminal-and-storage-resilience.md`, `log.md`, `index.md`)
  - Host macOS user keychain (`~/Library/Keychains/login.keychain-db`: `service="gemini"`, `account="antigravity"`) and Cockpit Tools / Antigravity 2.0 runtime state
  - Cross-store knowledge mirrors: Notion Knowledge Hub (`scripts/knowledge-refresh/sync-notion-knowledge.sh`), AgentMemory (`:3111`), and OMP long-term memory (`learn`).
