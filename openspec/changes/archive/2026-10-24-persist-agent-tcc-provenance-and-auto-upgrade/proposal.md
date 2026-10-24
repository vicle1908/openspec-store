# Proposal: Persist Agent TCC Provenance and Skill Surface Hygiene Across Automated Toolchain Upgrades

## Why

Automated daily toolchain upgrades (`workstation-daily-update.sh` and `shb-schedule`'s `workstation_update.py`) cause recurring macOS TCC provenance drift and recreate unallowlisted `~/Developer/data/skills` symlinks whenever coding agent CLIs (`claude`, `omp`, `node`, `opencode`, `python@3.15`) rotate versioned directories.

Live verification and `tccd` (`TCCDAccessIdentity`) disassembly on `2026-10-24` established five interacting root causes:
1. **Bundle-Keyed (`client_type = 0`) vs. Path-Keyed (`client_type = 1`) & Responsible-Process Attribution**:
   - In macOS `tccd` (`-[TCCDAccessIdentity initWithAttributionChain:]`, `0x10002736c`–`0x100028290`), application bundles with `NSURLIsApplicationKey = YES` and a `CFBundleIdentifier` (such as `Orca.app` / `Orca Terminal Host.app` `com.stablyai.orca`, `Orca Computer Use.app` `com.stablyai.orca.computer-use`, and Homebrew's framework `Python.app` `org.python.python`) are stored as `client_type = 0` (Bundle ID). When signed with a stable certificate (`TeamIdentifier = 6CX3WHS9HZ` for Orca; `Developer Agent Code Signing` `H"65340d85afd298131c682d8463087891292a2b59"` for `Python.app`), their TCC grants (`Accessibility`, `ScreenCapture`, `SystemPolicyAllFiles`) persist across all versioned directory updates automatically.
   - Conversely, bare Mach-O CLI binaries (`claude/versions/<ver>`, `Cellar/omp/<ver>/bin/omp`, `Cellar/node/<ver>/bin/node`, `Cellar/opencode/<ver>/bin/opencode`, `Cellar/python@3.15/<ver>/bin/python3.15`) have `NSURLIsApplicationKey = NO`, so `tccd` classifies them as `client_type = 1` (resolved `proc_pidpath`). When launched directly from `launchd` without an authorized responsible parent, `tccd` evaluates the CLI's own `client_type = 1` resolved path — meaning unrelated `Orca` or `Herdr` grants in `TCC.db` do **not** authorize a standalone `launchd`-spawned CLI.
2. **`NSOpenPanel` Dot-Extension UTType Rejection for Versioned Binaries (`2.1.310`, `python3.15`)**:
   - In macOS `System Settings > Privacy & Security > Screen & System Audio Recording`, the `+` (`NSOpenPanel`) file picker filters selectable items by UTType (`public.unix-executable` / `com.apple.application-bundle`). Because `2.1.310` and `python3.15` contain dots (`.310`, `.15`), `LaunchServices` classifies them as dynamic document UTTypes (`dyn.ah62d4rv4ge8xgqmu` / `dyn.ah62d4rv4ge8xcrk`) rather than `public.unix-executable`, leaving the `Open` button disabled unless selected via a temporary dotless executable name (`claude_2_1_310` / `python315`).
3. **Dual-Runner Delegation Bypass**: In `MODE=apply`, `~/Developer/scripts/workstation-daily-update.sh` delegates immediately to `shb-schedule run-now workstation-daily-update` (`src/shb_schedule/workflows/workstation_update.py`) and exits `0`, bypassing bash-only post-upgrade hooks unless implemented in both runners and synchronized via `config/script-provenance-manifest.tsv`.
4. **LaunchAgent Responsible-Process FDA Gap**: `~/Library/LaunchAgents/com.developer.workstation-daily-update.plist` sets `ProgramArguments[0] = "/bin/bash"`, which lacks `kTCCServiceSystemPolicyAllFiles` (Full Disk Access) in `TCC.db`, causing scheduled `08:00` runs (`data/updates/2026-10-22.json`, `2026-10-24.json`) to fail with `tcc_provenance: "ERROR" (TCC.db not readable)`.
5. **Recurring `data/skills` Surface Violation**: Because `/Users/androidteam/Developer/data` exists (for `data/updates/`), `/opt/homebrew/bin/skills update -y` (`cli.mjs:7958`) detects `existsSync(join(cwd, "data"))` and recreates `/Users/androidteam/Developer/data/skills`, causing `sync-workspace-agent-skills.py --check` to exit `1` (`surface_violations=data/skills`).

## What Changes

1. **Persistent Code Signing & Complete 9-Identity Direct TCC Enrollment**:
   - Maintain the trusted local Code Signing Certificate (`CN=Developer Agent Code Signing`, leaf SHA-1 `H"65340d85afd298131c682d8463087891292a2b59"`) in the login keychain and re-sign `goose` (`1.56.0`), `Python.app` (`org.python.python`, `client_type = 0`), and `python3` after Homebrew upgrades so `org.python.python` retains its 3-service (`Accessibility`, `ScreenCapture`, `SystemPolicyAllFiles`) TCC grant across all future `python@3.15` revisions.
   - Restore `/opt/homebrew/bin/goose` as the canonical Homebrew Cellar symlink (`brew link --overwrite block-goose-cli`) and enroll all 9 canonical workstation targets (`omp`, `node`, `opencode`, `goose`, `claude`, `kimi`, `herdr`, `python3`, `org.python.python`) in `TCC.db` so `scripts/tcc_provenance.py --json` returns `status: "CLEAN"` (`9/9` verified) without adding unused fallback parameters or weakening direct-row verification.
2. **Dual-Runner Post-Upgrade Hook, Stage 9 Manifest Reconciliation & `Python.app` (`org.python.python`) LaunchAgent Supervision**:
   - Wire unconditional post-upgrade binary signing (`Python.app`, `python3`, `goose`) and broken/missing/unlinked `block-goose-cli` symlink enforcement (`not is_symlink() or not exists()` / `! -L || ! -e`) into **both** `platform/openspec-store/scripts/workstation-daily-update.sh` (mirrored byte-for-byte to `~/Developer/scripts/workstation-daily-update.sh` and `config/script-provenance-manifest.tsv`) **and** `shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py`, and expose `has_unaligned_authority_drift()` / `Reconciled Authority Status` in `scripts/inventory-workstation-toolchain.py` so Stage 9 of `workstation-daily-update.sh` reconciles `authority_reconciliation` against `manifest_reconciliation` in a single pass (matching `workstation_update.py:1028-1105`) without spawning a redundant subprocess or triggering false-positive `AUTHORITY_DRIFT_DETECTED=1` on `prime-agent` (`local-dev`).
   - Update `~/Library/LaunchAgents/com.developer.workstation-daily-update.plist` `ProgramArguments` to invoke `workstation-daily-update.sh` via `/opt/homebrew/opt/python@3.15/Frameworks/Python.framework/Versions/3.15/Resources/Python.app/Contents/MacOS/Python` (`CFBundleIdentifier = org.python.python`, `client_type = 0`, verified `TCC_READABLE = True`) so scheduled `08:00` runs inherit Full Disk Access across all future Python upgrades while keeping Darwin `TCC.db` verification strictly fail-closed (`ERROR`/`DRIFT` never masked as `SKIPPED`).
3. **Automated `data/skills` Surface Pruning & Snapshot Refresh**:
   - Update `step_skills_refresh()` in `workstation_update.py`, `workstation-daily-update.sh`, and `sync-workspace-agent-skills.py` (in default reconciliation mode `not args.check` as well as `--accept-refresh` and `--bootstrap-snapshot`) to prune unallowlisted `~/Developer/data/skills` and `~/Developer/agent/skills` directories recreated by `skills update -y`, then refresh `.agents/.skill-snapshots/{current,previous}/manifest.json` via `--bootstrap-snapshot`.

4. **Workstation `uv` & Python Runtime Standardization & Dependency Upgrades**:
   - Keep `platform/openspec-store/scripts/tcc_provenance.py` strictly read-only (`mode=ro`, zero system mutations) and retain `sign_agent_binaries()` in `workstation-daily-update.sh` and `workstation_update.py` signing only the 3 TCC-enrolled targets (`Python.app`, Homebrew `python3`, and `goose`).
   - Upgrade `uv` managed Python (`cpython-3.14.5` -> `3.14.9`) via `uv python upgrade`, wire `uv python upgrade` into `step_uv_tools_update()` (`workstation_update.py`) and Stage 4 (`workstation-daily-update.sh` alongside `uv tool upgrade --all`), reinstall `tavily-cli` onto `uv`-managed Python `3.14`, uninstall unused `uv` Python `3.11`/`3.12` (`~/.local/bin/python3.11`), and uninstall zero-dependent Homebrew legacy Python formulae (`python@3.10`, `python@3.11`, `python@3.12`) so `obsolete_candidate_count == 0`.
   - Standardize `pyproject.toml` (`requires-python = ">=3.14"`, `[tool.uv]` with `package = false` on non-package repos, `pytest` config) and upgrade locked dependencies (`uv lock --upgrade && uv sync`) across `platform/openspec-store`, `shb/shb-schedule`, `tdt/tdt-core`, `ai-tooling/workspace-python-template`, and `ai-tooling/wiki-mcp-server`.
## Non-Goals

- Bypassing macOS System Integrity Protection (SIP) to write directly to `/Library/Application Support/com.apple.TCC/TCC.db` via SQLite.
- Injecting synthetic GUI click events (`AXPress`, `CGEventPost`) into `SecurityAgent` TCC consent dialogs (confirmed dropped by macOS `SecurityAgent`).
- Classifying Darwin `TCC.db` read errors as `SKIPPED` or marking a standalone, unattributed CLI `CLEAN` merely because unrelated `Orca`, `Herdr`, or `Python.app` identities hold grants in `TCC.db`.
- Modifying `tcc_provenance.py`'s strictly read-only (`mode=ro`) verification contract or mutating binaries inside `tcc_provenance.py`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `portable-workstation-toolchain`: Codify post-upgrade `Developer Agent Code Signing` re-signing, `Python.app` (`org.python.python`, `client_type = 0`) LaunchAgent supervision for `com.developer.workstation-daily-update.plist`, fail-closed direct TCC verification, dual-runner (`workstation_update.py` + `workstation-daily-update.sh`) synchronization (including Stage 9 `authority_reconciliation` + `manifest_reconciliation` parity and `uv python upgrade` + `uv tool upgrade --all`), post-`skills update` pruning of `~/Developer/data/skills`, and `uv` Python `3.14.9` + `pyproject.toml` / `uv.lock` standardization.

## Impact

- **Ownership Boundaries**:
  - **Central OpenSpec Store (`/Users/androidteam/Developer/platform/openspec-store`)**: Owns `pyproject.toml`, `uv.lock`, `scripts/tcc_provenance.py` (strictly read-only), `scripts/inventory-workstation-toolchain.py`, `scripts/sync-workspace-agent-skills.py`, `scripts/workstation-daily-update.sh`, `config/script-provenance-manifest.tsv`, and governance unit tests (`scripts/test-version-authority-governance.py`).
  - **SHB Scheduler & Workspace Python Repositories (`shb/shb-schedule`, `tdt/tdt-core`, `ai-tooling/workspace-python-template`, `ai-tooling/wiki-mcp-server`)**: Own their respective `pyproject.toml`, `uv.lock`, and `workstation_update.py` (`step_homebrew_update`, `step_uv_tools_update`, `step_agent_cli_update`, `step_skills_refresh`).
  - **Host Workstation Environment (`/Users/androidteam`)**: Owns login keychain identity `Developer Agent Code Signing`, `/opt/homebrew/bin/goose` Cellar link state, `uv` managed Python `3.14.9` (`~/.local/share/uv/python/`), `~/Library/LaunchAgents/com.developer.workstation-daily-update.plist`, `~/Developer/scripts/workstation-daily-update.sh`, `~/Developer/.agents/.skill-snapshots/`, and `TCC.db` enrollments.
