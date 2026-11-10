# Design

## Context

See `proposal.md` for motivation. On macOS Darwin 27.0.0 (`arm64`), `Orca.app` periodically executes `/opt/homebrew/bin/muse usage --json` (`/opt/homebrew/Caskroom/muse-code/<version>/muse-aarch64-macos`) in the background to populate its status-bar usage indicator. Two interacting mechanisms caused stacked `SecurityAgent` modal password dialogs (`"muse-aarch64-macos wants to use your confidential information stored in 'ai.meta.dev.credentials' in your keychain"`) and 5-second timeouts:

1. **Apple TN3137 File-Based Keychain Shim & `PartitionID` Enforcement (`OSStatus -67050`)**:
   - Per Apple Technical Note TN3137 (*On Mac keychain APIs and implementations*, revised 2026-09-24), the Data Protection Keychain requires an application bundle with an embedded provisioning profile (`keychain-access-groups` entitlement), which unbundled CLI binaries (`muse-aarch64-macos`, `Info.plist=not bound`) cannot use.
   - `muse` calls `SecItemAdd`, `SecItemCopyMatching`, `SecItemUpdate`, and `SecItemDelete` (`kSecClassGenericPassword`, `kSecAttrService="ai.meta.dev.credentials"`, `kSecAttrAccount="meta"`), which route through macOS's legacy file-based keychain shim (`~/Library/Keychains/login.keychain-db`).
   - When `/usr/bin/security add-generic-password -A` is used to seed `ai.meta.dev.credentials`, `/usr/bin/security` (an Apple platform binary, `anchor apple`) stamps `PartitionID = apple:` on the item's `CSSM_ACL_AUTHORIZATION_PARTITION_ID` ACL. When `muse-aarch64-macos` (signed by Meta Platforms `TeamIdentifier=V9WTTPBFK9`, `Identifier=muse-arm64`) reads the item, `securityd` rejects the code requirement (`[com.apple.securityd:clientid] code requirement check failed (-67050), client is not Apple-signed`) and spawns `SecurityAgent`. Furthermore, `security add-generic-password -w "$OMNIROUTE_API_KEY"` writes a raw string rather than `muse`'s JSON `SecretPayload`.
2. **Secondary Locked Keychain in User Search List & `FM-008` Slot Lock**:
   - `security list-keychains -d user` contained `/Users/androidteam/Library/Keychains/openvpn.keychain-db` (an empty 20 KB locked keychain) ahead of `/Users/androidteam/Library/Keychains/login.keychain-db`. Per TN3137, `SecItemCopyMatching` queries all keychains in the search list, triggering `SecurityAgent` unlock prompts or 5-second timeouts when `securityd` derives protected entropy (`/var/db/SystemKeys`, `dp_login` `slow down ~500ms`).
   - In `muse`, `TBH_CREDENTIAL_BACKEND=file` writes `schema_version: 1` (`{"schema_version": 1, "providers": {"meta": {"api_key": "..."}}}`) to `~/.config/muse/auth.json` (`mode 0600`). Once `auth.json` is on `schema_version: 1`, `muse` (`muse usage --json` and `muse exec`) reads `auth.json` directly in ~20ms without calling `SecItemCopyMatching`, even when spawned by GUI processes (`Orca.app`) that do not set `TBH_CREDENTIAL_BACKEND`. However, if `auth.json` already exists on `schema_version: 2` (`"storage": "keychain"`), running `TBH_CREDENTIAL_BACKEND=file muse auth set` fails closed with `FM-008` (`keychain unavailable and the meta slot is keychain-referenced`) unless `auth.json` is unlinked first.

## Goals / Non-Goals

**Goals:**
- Enforce `schema_version: 1` (`TBH_CREDENTIAL_BACKEND=file`) in `~/.config/muse/auth.json` (`mode 0600` inside `0700` `~/.config/muse`) and purge `ai.meta.dev.credentials` from `login.keychain-db`.
- Normalize `security list-keychains -d user` to retain only `~/Library/Keychains/login.keychain-db`.
- Automate post-upgrade healing via `ensure_muse_credential_hygiene()` in both `shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py` and `platform/openspec-store/scripts/workstation-daily-update.sh` (mirrored to `~/Developer/scripts/workstation-daily-update.sh`) while keeping `sign_agent_binaries()` scoped strictly to its 3 TCC code-signing targets.

**Non-Goals:**
- Modifying `sign_agent_binaries()` return values or TCC signing targets (`Python.app`, `python3`, `goose`).
- Modifying `~/.zshenv` (which remains minimal for secrets and Qoder PATH only).

## Decisions

1. **Dedicated `ensure_muse_credential_hygiene()` Helper Separate from `sign_agent_binaries()`**:
   - *Rationale*: Existing unit tests in `shb/shb-schedule/tests/test_workstation_update_workflow.py` assert exact `subprocess.run` calls inside `sign_agent_binaries()`. Defining `ensure_muse_credential_hygiene()` as a separate function invoked after `sign_agent_binaries()` in `step_homebrew_update()` and `workstation-daily-update.sh` preserves the existing `sign_agent_binaries()` contract while isolating keychain search-list normalization, `ai.meta.dev.credentials` deletion, and `auth.json` `schema_version: 1` healing.
2. **Unlink-Before-Seed Transaction Boundary for `auth.json` (`FM-008` Avoidance)**:
   - *Rationale*: `muse auth set` refuses to transition an existing `schema_version: 2` (`"storage": "keychain"`) slot to `file` storage in place (`FM-008`). `ensure_muse_credential_hygiene()` inspects `~/.config/muse/auth.json`; only when `auth.json` is missing or not on `schema_version: 1` with a non-empty `providers.meta.api_key` does it unlink `auth.json`, invoke `TBH_CREDENTIAL_BACKEND=file /opt/homebrew/bin/muse auth set --provider meta --api-key-stdin` with `OMNIROUTE_API_KEY` (resolved from environment or `~/.zshenv`), and enforce `chmod 600 ~/.config/muse/auth.json`. If `auth.json` is already valid `schema_version: 1`, it only enforces `0700`/`0600` permissions without unnecessary writes.

## Risks / Trade-offs

- **[Risk]** `OMNIROUTE_API_KEY` may not be present in the environment of a non-login `launchd` job if `auth.json` needs re-seeding.
  - **Mitigation**: `ensure_muse_credential_hygiene()` preserves an existing valid `schema_version: 1` `auth.json` in place without needing `OMNIROUTE_API_KEY`; if re-seeding is required and `OMNIROUTE_API_KEY` is absent from `env`, it extracts `OMNIROUTE_API_KEY` value-blind from `~/.zshenv` in memory and passes it via `stdin` to `muse auth set --provider meta --api-key-stdin`.
