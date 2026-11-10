# Spec Delta

## ADDED Requirements

### Requirement: Workstation maintenance SHALL enforce macOS user Keychain search-list hygiene and non-interactive CLI file credential stores

Workstation maintenance runners (`workstation-daily-update.sh` and `shb_schedule.workflows.workstation_update`) SHALL restrict the macOS user file-based Keychain search list to the unlocked `login.keychain-db` and SHALL enforce mode-`0600` file-backed credentials (`schema_version: 1` via `TBH_CREDENTIAL_BACKEND=file`) for `muse-aarch64-macos` without retaining `ai.meta.dev.credentials` items in `login.keychain-db`.

#### Scenario: Locked secondary keychains are removed from the user keychain search list
- **WHEN** `ensure_muse_credential_hygiene` inspects `security list-keychains -d user` on macOS
- **THEN** any secondary user keychain file outside `~/Library/Keychains/login.keychain-db` (such as a locked `openvpn.keychain-db`) SHALL be removed from the user search list via `security list-keychains -d user -s ~/Library/Keychains/login.keychain-db`
- **AND** `security list-keychains -d user` SHALL list only `~/Library/Keychains/login.keychain-db`

#### Scenario: Stale ai.meta.dev.credentials keychain entries and schema_version 2 pointers are healed post-upgrade
- **WHEN** `ensure_muse_credential_hygiene` runs during workstation maintenance or when `~/.config/muse/auth.json` is missing or contains `schema_version: 2` (`"storage": "keychain"`)
- **THEN** any `ai.meta.dev.credentials` generic password item in `login.keychain-db` SHALL be deleted via `security delete-generic-password -s "ai.meta.dev.credentials"` without invoking `security add-generic-password -A` (`PartitionID = apple:`, `OSStatus -67050`)
- **AND** `~/.config/muse/auth.json` SHALL be unlinked prior to running `TBH_CREDENTIAL_BACKEND=file /opt/homebrew/bin/muse auth set --provider meta --api-key-stdin` so `FM-008` slot-reference errors cannot occur
- **AND** `~/.config/muse` (`mode 0700`) and `~/.config/muse/auth.json` (`mode 0600`, `schema_version: 1`) SHALL be verified with zero `SecurityAgent` windows spawned
