# Delta Specification: portable-workstation-toolchain

## ADDED Requirements

### Requirement: Post-upgrade code signing and TCC provenance alignment across dual runners

Both `shb-schedule` (`workstation_update.py`) and `workstation-daily-update.sh` SHALL maintain code-signing and symlink invariants for TCC-governed binaries (`goose`, `python3`, `org.python.python`) using `Developer Agent Code Signing` (`H"65340d85afd298131c682d8463087891292a2b59"`), and `com.developer.workstation-daily-update.plist` SHALL execute under the FDA-authorized `Python.app` (`org.python.python`, `client_type = 0`) bundle so Darwin TCC verification remains strictly fail-closed.

#### Scenario: Post-upgrade re-signing and Homebrew link restoration
- **WHEN** automated maintenance updates coding agent CLIs or Python runtimes in `workstation_update.py` or `workstation-daily-update.sh`
- **THEN** any missing, broken, or unlinked `/opt/homebrew/bin/goose` path SHALL be restored via `brew link --overwrite block-goose-cli` to the active Homebrew Cellar binary
- **AND** `goose`, `Python.app` (`org.python.python`, `client_type = 0`), and `python3` SHALL be re-signed with `Developer Agent Code Signing` so their Designated Requirement matches `certificate leaf = H"65340d85afd298131c682d8463087891292a2b59"`
- **AND** `~/Developer/scripts/workstation-daily-update.sh` SHALL match `platform/openspec-store/scripts/workstation-daily-update.sh` and `config/script-provenance-manifest.tsv` with zero SHA-256 drift, using `has_unaligned_authority_drift()` / `Reconciled Authority Status` from `inventory-workstation-toolchain.py` in Stage 9 so aligned `updater_dispatch == "none"` `local-dev` entries (`prime-agent`) do not trigger false-positive `AUTHORITY_DRIFT_DETECTED=1`

#### Scenario: Scheduled LaunchAgent FDA supervision and fail-closed Darwin TCC verification
- **WHEN** `~/Library/LaunchAgents/com.developer.workstation-daily-update.plist` or an interactive operator executes `tcc_provenance.py --json` on Darwin
- **THEN** `com.developer.workstation-daily-update.plist` SHALL invoke `workstation-daily-update.sh` under `/opt/homebrew/opt/python@3.15/Frameworks/Python.framework/Versions/3.15/Resources/Python.app/Contents/MacOS/Python` (`CFBundleIdentifier = org.python.python`, `client_type = 0`) so `TCC.db` is readable with Full Disk Access across Python upgrades
- **AND** every target in the 9-identity workstation set (`omp`, `node`, `opencode`, `goose`, `claude`, `kimi`, `herdr`, `python3`, `org.python.python`) SHALL require a direct `auth_value = 2` record in `TCC.db` with `SecStaticCodeCheckValidity = 0`
- **AND** any unreadable/corrupt `TCC.db` or missing/mismatched target grant on Darwin SHALL be reported fail-closed as `ERROR` or `DRIFT` and SHALL NEVER be classified as `SKIPPED`

#### Scenario: Unattributed standalone or launchd CLI fails closed despite authorized Orca or Herdr in TCC.db
- **WHEN** `com.stablyai.orca` (`Orca.app`), `herdr`, and `org.python.python` hold valid `auth_value = 2` grants in `TCC.db`, but a CLI target (such as `claude` or `omp`) runs directly from `launchd` and lacks a direct `client_type = 1` grant in `TCC.db`
- **THEN** `verify_tcc_provenance()` SHALL NOT mark the CLI `CLEAN` from unrelated supervisor rows
- **AND** `verify_tcc_provenance()` SHALL return `status: "DRIFT"` with the target listed in `missing_binaries` and `<service>:missing_grant` (or `denied_or_pending`) in `failure_reasons`

### Requirement: Automated post-refresh skill surface pruning and snapshot manifest hygiene

The skill refresh pipeline (`sync-workspace-agent-skills.py`, `workstation_update.py:step_skills_refresh`, and `workstation-daily-update.sh`) SHALL prune unallowlisted `data/skills` and `agent/skills` directories created by `skills update -y` before surface validation and SHALL maintain schema-current `.skill-snapshots` manifests.

#### Scenario: Unallowlisted data/skills directory pruned after skills update
- **WHEN** `/opt/homebrew/bin/skills update -y` recreates `~/Developer/data/skills` because `~/Developer/data` exists for `data/updates/`
- **THEN** `step_skills_refresh()`, `workstation-daily-update.sh`, and `sync-workspace-agent-skills.py` (in default reconciliation mode, `--accept-refresh`, and `--bootstrap-snapshot`) SHALL remove `~/Developer/data/skills` and `~/Developer/agent/skills` before running surface checks
- **AND** `python3 scripts/sync-workspace-agent-skills.py --check` SHALL exit `0` with zero `surface_violations`
- **AND** `.agents/.skill-snapshots/{current,previous}/manifest.json` SHALL omit `"description_raw_bytes"` and record `total_bytes` as `files + lock`

### Requirement: Standardized uv Python runtime management and pyproject.toml lockfile hygiene

The workstation maintenance pipeline and Python repositories SHALL standardize on `uv`-managed Python (`>=3.14` without `<` upper bounds), automated `uv python upgrade` and `uv tool upgrade` execution, and fresh `uv.lock` files across all workspace projects while keeping `scripts/tcc_provenance.py` strictly read-only.

#### Scenario: Automated uv managed Python upgrade and legacy Python removal
- **WHEN** `workstation_update.py` (`step_uv_tools_update`) or `workstation-daily-update.sh` (Stage 4) executes
- **THEN** both runners SHALL execute `uv python upgrade` alongside `uv tool upgrade` (`--all` in bash, dynamic discovery in `shb-schedule`) while keeping `scripts/tcc_provenance.py` strictly read-only
- **AND** all installed `uv` tools (`browser-use`, `graphifyy`, `infinity-emb`, `tavily-cli`) SHALL resolve their virtualenv interpreter to `uv`-managed Python `3.14` (`~/.local/share/uv/python/cpython-3.14-macos-aarch64-none`)
- **AND** zero-dependent legacy Python installations (`uv` `3.11`/`3.12`, `~/.local/bin/python3.11`, and Homebrew `python@3.10`, `python@3.11`, `python@3.12`) SHALL be absent so `inventory-workstation-toolchain.py` reports `obsolete_candidate_count == 0`

#### Scenario: Workspace pyproject.toml clean-break requires-python and lockfile freshness
- **WHEN** `uv lock --check` is evaluated across `platform/openspec-store`, `shb/shb-schedule`, `tdt/tdt-core`, `ai-tooling/workspace-python-template`, and `ai-tooling/wiki-mcp-server` and `uv run pytest` is evaluated across `platform/openspec-store`, `shb/shb-schedule`, and `tdt/tdt-core`
- **THEN** each `pyproject.toml` SHALL declare `requires-python = ">=3.14"` without `<3.15` upper bounds and `[tool.uv]` with `python-preference = "only-managed"` (plus `package = false` for non-package repositories)
- **AND** `uv lock --check` SHALL exit `0` across all 35 workspace `pyproject.toml` repositories
