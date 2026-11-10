# Tasks

## 1. Host Muse Code Credential & Keychain Search-List Hygiene

- [x] 1.1 Normalize macOS user Keychain search list (`security list-keychains -d user -s ~/Library/Keychains/login.keychain-db`) to remove locked `openvpn.keychain-db` and delete any `ai.meta.dev.credentials` generic password entries from `login.keychain-db`.
- [x] 1.2 Unlink `~/.config/muse/auth.json` and re-seed `schema_version: 1` file-backed credentials (`TBH_CREDENTIAL_BACKEND=file /opt/homebrew/bin/muse auth set --provider meta --api-key-stdin`) with mode `0600` on `~/.config/muse/auth.json` and mode `0700` on `~/.config/muse`.
- [x] 1.3 Update managed skill `muse-code-omniroute-setup` (`~/.omp/agent/managed-skills/muse-code-omniroute-setup/SKILL.md`) and `platform/openspec-store/docs/mac-development-setup.md` to document Apple TN3137 file-based keychain constraints, prohibit `security add-generic-password -A` (`PartitionID = apple:`, `OSStatus -67050`), and standardize `TBH_CREDENTIAL_BACKEND=file` (`schema_version: 1`).

## 2. Workstation Maintenance Pipeline Automation & Unit Tests

- [x] 2.1 Add `TBH_CREDENTIAL_BACKEND="file"` and `ensure_muse_credential_hygiene()` to `/Users/androidteam/Developer/platform/openspec-store/scripts/workstation-daily-update.sh`, synchronize `/Users/androidteam/Developer/scripts/workstation-daily-update.sh`, and verify zero SHA-256 drift in `config/script-provenance-manifest.tsv`.
- [x] 2.2 Add `TBH_CREDENTIAL_BACKEND="file"` in `_get_env()` and `ensure_muse_credential_hygiene()` in `/Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py` (invoked in `step_homebrew_update()`), plus unit tests in `/Users/androidteam/Developer/shb/shb-schedule/tests/test_workstation_update_workflow.py`.

## 3. End-to-End Verification

- [x] 3.1 Verify `/opt/homebrew/bin/muse usage --json` (without `TBH_CREDENTIAL_BACKEND` in environment), `/opt/homebrew/bin/muse exec --disable-approval --no-session-log "Reply with exactly: OMNIROUTE_MUSE_OK"`, `bash ~/Developer/scripts/workstation-daily-update.sh --check`, `uv run --directory ~/Developer/shb/shb-schedule pytest -p no:cacheprovider tests/test_workstation_update_workflow.py`, and zero `SecurityAgent` windows on screen.
