# Proposal

## Why

Meta Muse Code CLI (`muse-aarch64-macos`) triggers stacked modal `SecurityAgent` macOS Keychain password prompts and 5-second read timeouts whenever `~/.config/muse/auth.json` uses `schema_version: 2` (`"storage": "keychain"`) or when `/usr/bin/security add-generic-password -A` writes an `apple:`-partitioned (`OSStatus -67050`) entry for `ai.meta.dev.credentials`.

Per Apple Technical Note TN3137 (*On Mac keychain APIs and implementations*), unbundled Mach-O command-line tools cannot use the entitlement-gated Data Protection Keychain and instead fall back to the legacy file-based keychain shim (`SecAccess` ACLs + `PartitionID`), where items created by `/usr/bin/security` carry `PartitionID = apple:` (`client is not Apple-signed`) and where `SecItemCopyMatching` traverses every keychain in the user search list (including locked secondary keychains such as `openvpn.keychain-db`). Because `Orca.app` periodically runs `/opt/homebrew/bin/muse usage --json` in the background without shell environment variables, relying on `schema_version: 2` (`"storage": "keychain"`) causes recurring modal `SecurityAgent` prompts across Homebrew Cask upgrades and background polls. Switching `~/.config/muse/auth.json` (`mode 0600`) to `schema_version: 1` (`TBH_CREDENTIAL_BACKEND=file`) and enforcing keychain search-list and `ai.meta.dev.credentials` hygiene in the workstation maintenance runners permanently eliminates these modal prompts.

## What Changes

- **Standardize Muse Code CLI on `schema_version: 1` File-Backed Credential Storage (`~/.config/muse/auth.json`, mode `0600`)**:
  - Replace the `schema_version: 2` (`"storage": "keychain"`) requirement in `omniroute-agent-cli-routing` with `schema_version: 1` (`TBH_CREDENTIAL_BACKEND=file`), removing any `schema_version: 2` file prior to seeding so `muse auth set` never fails with `FM-008` (`keychain unavailable and the meta slot is keychain-referenced`).
  - Purge legacy `svce="ai.meta.dev.credentials"` entries from `~/Library/Keychains/login.keychain-db` and prohibit `/usr/bin/security add-generic-password -A` workarounds that stamp `PartitionID = apple:` (`OSStatus -67050`) and raw non-JSON payloads.
- **Normalize User Keychain Search List & Enforce Automated Post-Upgrade Hygiene (`ensure_muse_credential_hygiene`)**:
  - Remove locked secondary keychains (`openvpn.keychain-db`) from `security list-keychains -d user` so `SecItemCopyMatching` traverses only the unlocked `login.keychain-db` and `System.keychain`.
  - Add `TBH_CREDENTIAL_BACKEND=file` and `ensure_muse_credential_hygiene()` to both `/Users/androidteam/Developer/platform/openspec-store/scripts/workstation-daily-update.sh` (mirrored to `/Users/androidteam/Developer/scripts/workstation-daily-update.sh`) and `/Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py`, plus unit tests in `shb/shb-schedule/tests/test_workstation_update_workflow.py`.

## Non-Goals

- Modifying OmniRoute container runtime patches, model routing combos, or `muse-spark-1.3` upstream provider definitions.
- Altering macOS TCC database (`TCC.db`) grants, `tcc_provenance.py` verification logic, or `sign_agent_binaries()` code-signing targets (`Python.app`, `python3`, `goose`).
- Adding non-secret configuration variables to `~/.zshenv` (which remains minimal for secrets and Qoder PATH only).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `omniroute-agent-cli-routing`: Update Muse Code CLI credential requirements and scenarios to mandate `schema_version: 1` (`TBH_CREDENTIAL_BACKEND=file`) in `~/.config/muse/auth.json` (`mode 0600`), absence of `ai.meta.dev.credentials` in `login.keychain-db`, and zero `SecurityAgent` prompts during GUI-spawned `muse usage --json` polls.
- `workstation-remote-and-agent-permissions`: Add requirement and scenarios for macOS file-based Keychain search-list hygiene (`login.keychain-db` only in user domain) and unbundled Cask CLI file-backed credential healing (`ensure_muse_credential_hygiene`) during workstation maintenance.

## Impact

- **Ownership Boundaries**:
  - `~/Developer/platform/openspec-store` (`openspec/specs/omniroute-agent-cli-routing/spec.md`, `openspec/specs/workstation-remote-and-agent-permissions/spec.md`, `scripts/workstation-daily-update.sh`, `docs/mac-development-setup.md`)
  - `~/Developer/scripts/workstation-daily-update.sh` (executed mirror tracked in `config/script-provenance-manifest.tsv`)
  - `~/Developer/shb/shb-schedule` (`src/shb_schedule/workflows/workstation_update.py`, `tests/test_workstation_update_workflow.py`)
  - Host user configuration (`~/.config/muse/auth.json`, macOS user keychain search list, `~/.omp/agent/managed-skills/muse-code-omniroute-setup/SKILL.md`)
