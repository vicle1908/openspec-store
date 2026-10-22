# Delta Specification: portable-workstation-toolchain

## ADDED Requirements

### Requirement: Post-upgrade code signing and TCC provenance alignment across dual runners

Both `shb-schedule` (`workstation_update.py`) and `workstation-daily-update.sh` SHALL maintain code-signing and symlink invariants for TCC-governed binaries (`goose`, `omp`, `claude`, `python3`, `org.python.python`) using `Developer Agent Code Signing` (`H"65340d85afd298131c682d8463087891292a2b59"`), and `workstation-daily-update.sh` SHALL remain byte-synchronized with `config/script-provenance-manifest.tsv`.

#### Scenario: Post-upgrade re-signing and Homebrew link restoration
- **WHEN** automated maintenance updates coding agent CLIs or Python runtimes in `workstation_update.py` or `workstation-daily-update.sh`
- **THEN** `/opt/homebrew/bin/goose` SHALL resolve via symlink to the active Homebrew Cellar binary (`block-goose-cli`) rather than an unlinked standalone binary
- **AND** target bundles and executables enrolled under `Developer Agent Code Signing` SHALL be re-signed so their Designated Requirement matches `certificate leaf = H"65340d85afd298131c682d8463087891292a2b59"`
- **AND** `~/Developer/scripts/workstation-daily-update.sh` SHALL match `platform/openspec-store/scripts/workstation-daily-update.sh` and `config/script-provenance-manifest.tsv` with zero SHA-256 drift

#### Scenario: Path-keyed TCC drift vs non-FDA LaunchAgent execution
- **WHEN** `tcc_provenance.py --json` runs under a Full Disk Access-authorized supervisor
- **THEN** any `client_type = 1` resolved path missing from `TCC.db` or failing `csreq` validation SHALL be reported fail-closed as `status: "DRIFT"`
- **AND** when `tcc_provenance.py` runs under a non-FDA LaunchAgent (`/bin/bash`) and cannot open `TCC.db`, the runner SHALL record `SKIPPED` (`tcc_db_unreadable_without_fda_supervisor`) rather than failing the workflow with `ERROR`

### Requirement: Automated post-refresh skill surface pruning and snapshot manifest hygiene

The skill refresh pipeline (`sync-workspace-agent-skills.py`, `workstation_update.py:step_skills_refresh`, and `workstation-daily-update.sh`) SHALL prune unallowlisted `data/skills` and `agent/skills` directories created by `skills update -y` before surface validation and SHALL maintain schema-current `.skill-snapshots` manifests.

#### Scenario: Unallowlisted data/skills directory pruned after skills update
- **WHEN** `/opt/homebrew/bin/skills update -y` recreates `~/Developer/data/skills` because `~/Developer/data` exists for `data/updates/`
- **THEN** `step_skills_refresh()`, `workstation-daily-update.sh`, and `sync-workspace-agent-skills.py --accept-refresh` SHALL remove `~/Developer/data/skills` and `~/Developer/agent/skills` before running surface checks
- **AND** `python3 scripts/sync-workspace-agent-skills.py --check` SHALL exit `0` with zero `surface_violations`
- **AND** `.agents/.skill-snapshots/{current,previous}/manifest.json` SHALL omit `"description_raw_bytes"` and record `total_bytes` as `files + lock`
