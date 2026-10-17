# portable-workstation-toolchain Specification Delta

## ADDED Requirements

### Requirement: Interactive zsh startup SHALL defer synchronous provider helpers and maintain sub-200ms latency

The workstation `~/.zshrc` configuration SHALL lazy-load or defer synchronous `cce` provider initialization (`__cce_apply_current_provider`) until first invocation so interactive shell startup does not fork external helper processes, keeping `zsh -i -c exit` latency under 200ms.

#### Scenario: Deferred cce initialization during interactive shell startup
- **WHEN** a new interactive zsh session starts (`zsh -i -c exit`)
- **THEN** `~/.zshrc` SHALL define the `cce` shell wrapper without synchronously executing `$_cce_binary use` during shell initialization
- **AND** median interactive shell startup latency SHALL remain below 200ms

#### Scenario: Runaway AddressBookSourceSync background CPU loop is suppressed
- **WHEN** workstation process health is audited
- **THEN** `AddressBookSourceSync` SHALL NOT consume sustained runaway CPU (`>50%`) in the background

### Requirement: Fallback shell updater and toolchain inventory SHALL cover Kimi Code standalone binary

Both the fallback shell maintenance runner (`workstation-daily-update.sh` and its store mirror) and `inventory-workstation-toolchain.py` SHALL include `kimi` (`~/.kimi-code/bin/kimi`) in their sanctioned PATH, known root, and agent coverage lists.

#### Scenario: Fallback shell script and inventory recognize Kimi Code
- **WHEN** `workstation-daily-update.sh` and `inventory-workstation-toolchain.py` evaluate installed AI agent CLIs
- **THEN** `workstation-daily-update.sh` SHALL include `~/.kimi-code/bin` in `PATH`, `~/.kimi-code` in `known_root`, and `kimi` in `AGENT_CLI_COVERED`
- **AND** `inventory-workstation-toolchain.py` SHALL classify `~/.kimi-code/bin/kimi` as `[CLEAN]` under `vendor_download` authority with `0` unknown manifest tools

### Requirement: Script provenance verification and telemetry alert suppression SHALL match live manifest structure

Script drift validation between `~/Developer/scripts/workstation-daily-update.sh` and `platform/openspec-store/scripts/workstation-daily-update.sh` SHALL compute and compare live SHA-256 digests across the path pairs declared in `config/script-provenance-manifest.tsv`, and telemetry notifications SHALL suppress failure alerts when workflow status is `"SUCCESS"`, `"completed"`, or `"paused"`.

#### Scenario: Dynamic paired-file SHA-256 comparison via script-provenance-manifest.tsv
- **WHEN** `step_integrity_and_store_validation` or `detect_script_drift` reads `config/script-provenance-manifest.tsv`
- **THEN** it SHALL parse the 3-column TSV (`<executed_path>`, `<recorded_path>`, `<authority>`) and verify that both files have identical SHA-256 digests

#### Scenario: Paused workflow status suppresses failure alert notifications
- **WHEN** `workstation-daily-update` finishes with status `"SUCCESS"`, `"completed"`, or `"paused"`
- **THEN** `step_record_telemetry_and_notify` SHALL record the JSON report without firing a macOS failure alert notification
