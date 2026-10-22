# Proposal: Persist Agent TCC Provenance and Skill Surface Hygiene Across Automated Toolchain Upgrades

## Why

Automated daily toolchain upgrades (`workstation-daily-update.sh` and `shb-schedule`'s `workstation_update.py`) invalidate macOS TCC permissions and recreate unallowlisted `~/Developer/data/skills` symlinks on every maintenance run.

Specifically, live verification on `2026-10-22` identified four interacting failure modes:
1. **Path-Keyed (`client_type = 1`) vs Bundle-Keyed (`client_type = 0`) TCC Attribution**: macOS `tccd` and `scripts/tcc_provenance.py` key `client_type = 1` records by the kernel-resolved `os.path.realpath` (`proc_pidpath`). When Homebrew (`omp`, `python@3.15`) or Claude (`~/.local/share/claude/versions/<ver>`) rotates versioned directories, the resolved path changes and fails `WHERE client = ?` (`missing_grant`), while `/opt/homebrew/bin/goose` remains an unlinked standalone binary shadowing `/opt/homebrew/Cellar/block-goose-cli/1.55.0/bin/goose` (which already holds valid `Accessibility` and `ScreenCapture` grants in `TCC.db`).
2. **Dual-Runner Delegation Bypass**: In `MODE=apply`, `~/Developer/scripts/workstation-daily-update.sh` delegates immediately to `shb-schedule run-now workstation-daily-update` (`src/shb_schedule/workflows/workstation_update.py`) and exits `0`, bypassing bash-only post-upgrade hooks unless implemented in both runners and synchronized via `config/script-provenance-manifest.tsv`.
3. **LaunchAgent Responsible-Process FDA Gap**: `~/Library/LaunchAgents/com.developer.workstation-daily-update.plist` launches `/bin/bash`, which lacks `kTCCServiceSystemPolicyAllFiles` (Full Disk Access) in `TCC.db`, causing scheduled `08:00` runs (`data/updates/2026-10-22.json`) to fail with `tcc_provenance: "ERROR" (TCC.db not readable)`.
4. **Recurring `data/skills` Surface Violation**: Because `/Users/androidteam/Developer/data` exists (for `data/updates/`), `/opt/homebrew/bin/skills update -y` (`cli.mjs:7958`) detects `existsSync(join(cwd, "data"))` and recreates `/Users/androidteam/Developer/data/skills`, causing `sync-workspace-agent-skills.py --check` to exit `1` (`surface_violations=data/skills`) and leaving `.agents/.skill-snapshots/{current,previous}/manifest.json` unrefreshed since `2026-10-19`.

## What Changes

1. **Persistent Local Code Signing Authority & Symlink/Path Alignment**:
   - Maintain the trusted local Code Signing Certificate (`CN=Developer Agent Code Signing`, leaf SHA-1 `H"65340d85afd298131c682d8463087891292a2b59"`) in the login keychain.
   - Restore `/opt/homebrew/bin/goose` as the canonical Homebrew Cellar symlink (`brew link --overwrite block-goose-cli`) so it resolves to the TCC-enrolled `/opt/homebrew/Cellar/block-goose-cli/<ver>/bin/goose` binary, and apply `Developer Agent Code Signing` to `Python.app` (`org.python.python`, `client_type = 0`) and target agent binaries (`goose`, `omp`, `claude`, `python3`) with explicit operator enrollment gates when `client_type = 1` resolved paths change.
2. **Dual-Runner Post-Upgrade Hook & LaunchAgent FDA Attribution**:
   - Wire post-upgrade binary signing and TCC provenance verification into **both** `platform/openspec-store/scripts/workstation-daily-update.sh` (mirrored byte-for-byte to `~/Developer/scripts/workstation-daily-update.sh` and `config/script-provenance-manifest.tsv`) **and** `shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py`.
   - Ensure scheduled LaunchAgent executions (`com.developer.workstation-daily-update.plist`) invoke `tcc_provenance.py` via an FDA-authorized responsible binary or classify non-FDA LaunchAgent `TCC.db` EACCES reads as `SKIPPED` (`unreadable_under_launchd_bash`) rather than a false workflow `ERROR`.
3. **Automated `data/skills` Surface Pruning & Snapshot Refresh**:
   - Update `step_skills_refresh()` in `workstation_update.py`, `workstation-daily-update.sh`, and `sync-workspace-agent-skills.py --accept-refresh` to prune unallowlisted `~/Developer/data/skills` and `~/Developer/agent/skills` directories immediately after `skills update -y` runs, then refresh `.agents/.skill-snapshots/{current,previous}/manifest.json` via `--bootstrap-snapshot`.

## Non-Goals

- Bypassing macOS System Integrity Protection (SIP) to write directly to `/Library/Application Support/com.apple.TCC/TCC.db` via SQLite.
- Injecting synthetic GUI click events (`AXPress`, `CGEventPost`) into `SecurityAgent` TCC consent dialogs (confirmed dropped by macOS `SecurityAgent`).
- Modifying `tcc_provenance.py`'s read-only (`mode=ro`) safety contract.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `portable-workstation-toolchain`: Codify post-upgrade code signing and `client_type = 1` vs `client_type = 0` TCC provenance rules, dual-runner (`workstation_update.py` + `workstation-daily-update.sh`) synchronization, LaunchAgent `TCC.db` attribution handling, and post-`skills update` pruning of `~/Developer/data/skills` with snapshot manifest refresh.

## Impact

- **Ownership Boundaries**:
  - **Central OpenSpec Store (`/Users/androidteam/Developer/platform/openspec-store`)**: Owns `scripts/tcc_provenance.py`, `scripts/sync-workspace-agent-skills.py`, `scripts/workstation-daily-update.sh`, `config/script-provenance-manifest.tsv`, and governance unit tests.
  - **SHB Scheduler Repository (`/Users/androidteam/Developer/shb/shb-schedule`)**: Owns `src/shb_schedule/workflows/workstation_update.py` (`step_agent_cli_update`, `step_skills_refresh`, `step_integrity_and_store_validation`) and its unit tests (`tests/test_workstation_update_workflow.py`).
  - **Host Workstation Environment (`/Users/androidteam`)**: Owns login keychain identity `Developer Agent Code Signing`, `/opt/homebrew/bin/goose` Cellar link state, `~/Developer/scripts/workstation-daily-update.sh`, `~/Developer/.agents/.skill-snapshots/`, and interactive `System Settings > Privacy & Security` `TCC.db` enrollment gates.
