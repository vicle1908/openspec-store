# Spec Delta

## ADDED Requirements

### Requirement: Workstation diagnostics SHALL verify login.keychain-db writability via SecKeychainCopySettings rather than SecKeychainGetStatus alone

Workstation Keychain diagnostics on macOS SHALL treat `security show-keychain-info ~/Library/Keychains/login.keychain-db` (`SecKeychainCopySettings`) as the authoritative non-mutating check for `login.keychain-db` unlock usability, because `SecKeychainGetStatus` can report unlocked bits (`0x7`) while `securityd` fails decryption (`-25337` / `CSSMERR_CSP_INVALID_DATA`) and rejects reads/writes with `errSecAuthFailed` (`-25293`).

#### Scenario: Authoritative probe detects desynced securityd unlock state masked by SecKeychainGetStatus
- **WHEN** macOS `securityd` has restarted mid-session or lost its in-memory unlock key for `~/Library/Keychains/login.keychain-db` while `SecKeychainGetStatus` reports `0x7`
- **THEN** `security show-keychain-info ~/Library/Keychains/login.keychain-db` SHALL fail with `SecKeychainCopySettings ...: The user name or passphrase you entered is not correct` (`errSecAuthFailed`, `-25293`)
- **AND** operators SHALL NOT conclude the keychain is writable from `SecKeychainGetStatus` alone, and SHALL re-lock and unlock `~/Library/Keychains/login.keychain-db` (`security lock-keychain` then `security unlock-keychain`) before retrying GUI or CLI credential writes.

#### Scenario: Cockpit Tools Antigravity 2.0 credential write succeeds after login.keychain-db unlock recovery
- **WHEN** `security show-keychain-info ~/Library/Keychains/login.keychain-db` returns `no-timeout` and Cockpit Tools switches an account for Antigravity 2.0 (`v2.34.0`)
- **THEN** `security add-generic-password -U` SHALL update `service="gemini"`, `account="antigravity"` in `~/Library/Keychains/login.keychain-db` without `SecKeychainItemModifyContent` or `SecKeychainItemCreateFromContent` `-25293` errors
- **AND** Antigravity Desktop SHALL launch cleanly with the switched account marked `Current`.
