# Design

## Context

See `proposal.md` (`Why`) for the incident summary. Prior work in `2026-11-10-harden-muse-credential-backend-and-keychain-hygiene` normalized `security list-keychains -d user` to `~/Library/Keychains/login.keychain-db` and documented `securityd` 100-thread exhaustion prevention in `workstation-remote-and-agent-permissions` and `wiki/concepts/workstation-terminal-and-storage-resilience.md`. Unlike `muse` (which moved to file-backed `schema_version: 1` credentials), Antigravity 2.0 (`v2.34.0`) and Cockpit Tools (`v1.4.2`) require macOS Keychain (`service="gemini"`, `account="antigravity"`).

## Goals / Non-Goals

**Goals:**
- Establish a deterministic, read-only Keychain probe (`security show-keychain-info ~/Library/Keychains/login.keychain-db` / `SecKeychainCopySettings`) that detects `securityd` unlock-key desync (`-25293` / `-25337`) even when `SecKeychainGetStatus` returns `0x7`.
- Document the exact recovery sequence (`security lock-keychain` + `security unlock-keychain`, or logout/reboot / `set-keychain-password` fallback) and verify Cockpit Tools + Antigravity 2.0 end-to-end.
- Persist the verified state across OpenSpec, `docs/mac-development-setup.md`, `wiki/`, Notion, AgentMemory, and OMP long-term memory.

**Non-Goals:**
- Modifying `scripts/workstation-daily-update.sh` (concurrent external changes present in shared worktree).
- Automating non-interactive keychain unlocking with stored passphrases (unsafe and unnecessary).
- Changing Cockpit Tools or Antigravity binaries.

## Decisions

1. **Use `security show-keychain-info` (`SecKeychainCopySettings`) as the authoritative probe**
   - *Rationale*: Read-only (`dump-keychain` without `-d` or `SecKeychainGetStatus`) succeeds even when `securityd` cannot decrypt secrets (`CSSMERR_CSP_INVALID_DATA`, `-25337`). `SecKeychainCopySettings` exercises `securityd` `makeUnlocked()` and fails immediately with `-25293` when broken, with zero Keychain mutations and zero `SecurityAgent` prompts.
   - *Alternative considered*: Probing via `security add-generic-password` test writes. Rejected as primary check because it mutates `login.keychain-db` on success.

2. **Re-lock before unlocking (`security lock-keychain` → `security unlock-keychain`)**
   - *Rationale*: When `securityd` caches stale `is unlocked` state (`0x7`), explicitly locking clears the stale in-memory state before `unlock-keychain` prompts the operator for their macOS login passphrase and re-hydrates `securityd`'s unlock key without losing existing Keychain items.

3. **Selective commit via `commit.draft()` in shared worktree**
   - *Rationale*: `platform/openspec-store` `main` holds unrelated uncommitted changes from other sessions; `commit.draft()` isolates only the files and lines authored for this change.

## Risks / Trade-offs

- **Risk: Stale `securityd` state can recur after long uptime (`32+` days) or daemon crash/restart.**
  - *Mitigation*: Existing `ensure_muse_credential_hygiene()` terminates orphaned `security find-generic-password -s gemini` probers to avoid 100-thread exhaustion; if `SecKeychainCopySettings` still fails, the documented `lock-keychain` / `unlock-keychain` runbook recovers without resetting the keychain.
