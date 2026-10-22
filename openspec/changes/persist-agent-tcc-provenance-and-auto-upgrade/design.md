# Design: Persist Agent TCC Provenance and Skill Surface Hygiene Across Automated Toolchain Upgrades

## Overview

This design specifies the cross-repository and host architecture to maintain macOS TCC provenance (`Accessibility`, `ScreenCapture`, `SystemPolicyAllFiles`) and clean workspace skill surfaces (`sync-workspace-agent-skills.py --check`) across automated daily maintenance runs.

## Problem Statement & Verified Invariants

1. **SIP & `SecurityAgent` Hardware/Kernel Invariants**:
   - `SecurityAgent` drops synthetic accessibility and Quartz events (`AXPress`, `CGEventPost`) to prevent programmatic privilege escalation.
   - macOS System Integrity Protection (SIP) protects `/Library/Application Support/com.apple.TCC/TCC.db` (`SF_RESTRICTED`), blocking direct SQLite writes even under `root`.
2. **`TCC.db` `client_type = 1` (Resolved Path) vs `client_type = 0` (Bundle ID) Attribution**:
   - Existing verifier `platform/openspec-store/scripts/tcc_provenance.py:440,559` resolves each CLI via `os.path.realpath()` (matching the Darwin kernel's `proc_pidpath` after `execve` symlink resolution) and queries `SELECT service, client_type, auth_value, csreq FROM access WHERE client = ?`.
   - For **`client_type = 0` (`org.python.python`)**: `TCC.db` keys the record by bundle identifier `"org.python.python"`, independent of the Homebrew Cellar version directory (`3.15.0` vs `3.15.0_1`). Re-signing `Python.app` with a persistent certificate (`Developer Agent Code Signing`, `H"65340d85afd298131c682d8463087891292a2b59"`) preserves the `csreq` across Cellar upgrades once enrolled.
   - For **`client_type = 1` (`omp`, `claude`, `goose`, `python3`, `node`, `opencode`, `kimi`, `herdr`)**: `TCC.db` keys the record by the **resolved filesystem path (`os.path.realpath`)** AND validates `csreq`.
     - **Unlinked `goose` shadow binary**: `/opt/homebrew/bin/goose` is currently a standalone ad-hoc binary (`Oct 16`, `cdhash H"a0fcad02..."`) shadowing `/opt/homebrew/Cellar/block-goose-cli/1.55.0/bin/goose` (`cdhash H"7d58ed9a..."`), which already holds valid `Accessibility` and `ScreenCapture` grants in `TCC.db`. Restoring the Homebrew symlink (`brew link --overwrite block-goose-cli`) immediately restores `goose` provenance when version `1.55.0` is active.
     - **Versioned paths (`Cellar/omp/<ver>/bin/omp`, `~/.local/share/claude/versions/<ver>`, `Cellar/python@3.15/<ver>/...`)**: Re-signing a newly created versioned path with `Developer Agent Code Signing` stabilizes its Designated Requirement (`designated => identifier "<id>" and certificate leaf = H"65340d85afd298131c682d8463087891292a2b59"`), **but** if `/opt/homebrew/bin/omp` or `~/.local/bin/claude` remains a symlink to a new versioned path, `os.path.realpath` changes and `TCC.db` lacks a row for the new `client` string unless either (a) the binary at the enrolled path is updated in-place / hardlinked at a stable enrolled path, or (b) the new path is enrolled in `TCC.db`.
3. **Dual-Runner Execution & Script Provenance Contract**:
   - In `MODE=apply`, `~/Developer/scripts/workstation-daily-update.sh:494-502` invokes `uv run --directory ~/Developer/shb/shb-schedule shb-schedule run-now workstation-daily-update` (`shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py`) and returns `0`.
   - Furthermore, `step_integrity_and_store_validation()` verifies that `~/Developer/scripts/workstation-daily-update.sh` matches `platform/openspec-store/scripts/workstation-daily-update.sh` and `config/script-provenance-manifest.tsv`.
4. **LaunchAgent Responsible-Process FDA Attribution**:
   - `~/Library/LaunchAgents/com.developer.workstation-daily-update.plist` sets `ProgramArguments[0] = "/bin/bash"`. Because `/bin/bash` lacks `kTCCServiceSystemPolicyAllFiles` (Full Disk Access), `tcc_provenance.py` cannot open `TCC.db` during `08:00` scheduled runs (`data/updates/2026-10-22.json`: `tcc_provenance: "ERROR"`).
5. **`skills update -y` Recreating `~/Developer/data/skills`**:
   - `/opt/homebrew/Cellar/skills/1.7.2/libexec/lib/node_modules/skills/dist/cli.mjs:7958` checks `existsSync(join(cwd, "data"))`. Because `~/Developer/data` exists (storing `data/updates/*.json`), `skills update -y` recreates `~/Developer/data/skills` (`AstrBot` surface) on every run, causing `sync-workspace-agent-skills.py --check` to exit `1` (`surface_violations=data/skills`) and blocking `.agents/.skill-snapshots/{current,previous}/manifest.json` from refreshing (`accepted_at` stuck at `2026-10-19T05:53:25Z`).

## Architectural Decisions

### 1. Local Code-Signing Authority & Target Path Stabilization
- **Certificate**: `CN=Developer Agent Code Signing`, SHA-1 leaf anchor `H"65340d85afd298131c682d8463087891292a2b59"`, trusted for Code Signing in `~/Library/Keychains/login.keychain-db`.
- **Target Handling**:
  - **`goose`**: Enforce `brew link --overwrite block-goose-cli` so `/opt/homebrew/bin/goose` is a symlink to the Homebrew Cellar binary (`1.55.0`), or sign with `com.block.goose` when the enrolled `TCC.db` row specifies `certificate leaf = H"65340d85..."`.
  - **`org.python.python` (`client_type = 0`)**: Sign `/opt/homebrew/opt/python@3.15/Frameworks/Python.framework/Versions/3.15/Resources/Python.app` with `Developer Agent Code Signing` (`--identifier org.python.python --deep`) so the bundle-ID grant in `TCC.db` remains valid across Homebrew patch revisions (`3.15.0_1`+).
  - **`omp`, `claude`, `python3` (`client_type = 1`)**: Provide `sign_agent_binaries()` in both maintenance runners to sign updated binaries with `Developer Agent Code Signing` (`com.developer.omp`, `com.anthropic.claude-code`, `org.python.python3`), and surface a clear operator enrollment notice when a newly created Cellar/versioned realpath has no matching `client` row in `TCC.db`.

### 2. Dual-Runner Hook Synchronization & LaunchAgent FDA Handling
- Implement `sign_agent_binaries()` and post-`skills update` surface pruning in **both**:
  1. `/Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py` (`step_agent_cli_update` and `step_skills_refresh`), and
  2. `/Users/androidteam/Developer/platform/openspec-store/scripts/workstation-daily-update.sh` (mirrored to `/Users/androidteam/Developer/scripts/workstation-daily-update.sh` with updated SHA-256 in `config/script-provenance-manifest.tsv`).
- In `workstation_update.py` (`step_integrity_and_store_validation`) and `workstation-daily-update.sh` (`verify_tcc_provenance`), when `tcc_provenance.py` returns `TCC.db not readable` (`PermissionError` / `unable to open database file`) under non-FDA `/bin/bash` LaunchAgent attribution, classify the check as `SKIPPED` (`tcc_db_unreadable_without_fda_supervisor`) with a warning rather than failing the run as `ERROR`/`PARTIAL`, while keeping interactive/FDA-supervised runs strictly fail-closed on `DRIFT`.

### 3. Automated `data/skills` Pruning & Snapshot Manifest Refresh
- Update `sync-workspace-agent-skills.py` (during `--accept-refresh` and `--bootstrap-snapshot`), `workstation_update.py:step_skills_refresh()`, and `workstation-daily-update.sh` to automatically remove unallowlisted `~/Developer/data/skills` and `~/Developer/agent/skills` symlink trees created by `skills update -y` before running surface parity validation.
- Execute `python3 scripts/sync-workspace-agent-skills.py --bootstrap-snapshot` so `/Users/androidteam/Developer/.agents/.skill-snapshots/{current,previous}/manifest.json` is rewritten without legacy `"description_raw_bytes"` fields and with accurate `files + lock` `total_bytes`.

## Transaction Boundaries

- **Central OpenSpec Store (`/Users/androidteam/Developer/platform/openspec-store`)**: `scripts/workstation-daily-update.sh`, `scripts/sync-workspace-agent-skills.py`, `config/script-provenance-manifest.tsv`, and unit tests are committed atomically in `openspec-store`.
- **SHB Scheduler Repository (`/Users/androidteam/Developer/shb/shb-schedule`)**: `src/shb_schedule/workflows/workstation_update.py` and `tests/test_workstation_update_workflow.py` are committed in `shb/shb-schedule`.
- **Host Environment (`/Users/androidteam`)**: Keychain signing, `brew link --overwrite block-goose-cli`, `~/Developer/scripts/workstation-daily-update.sh` sync, `~/Developer/data/skills` removal, `.skill-snapshots` bootstrap, and interactive `TCC.db` GUI approvals are verified on the live host and recorded with SHA-256 digests in `evidence.md`.
