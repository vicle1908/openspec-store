# Spec Delta: portable-workstation-toolchain

## MODIFIED Requirements

### Requirement: Post-upgrade code signing and TCC provenance alignment across dual runners

Both `shb-schedule` (`workstation_update.py`) and `workstation-daily-update.sh` SHALL maintain code-signing and bundle invariants for TCC-governed identities (`Python.app` `org.python.python`, `goose`, `python3`, and agent bundle wrappers) using `Developer Agent Code Signing` (`H"65340d85afd298131c682d8463087891292a2b59"`), standardize workstation execution on `client_type = 0` (`CFBundleIdentifier`) bundle attribution, and execute `com.developer.workstation-daily-update.plist` under the FDA-authorized `Python.app` (`org.python.python`, `client_type = 0`) bundle so Darwin TCC verification remains strictly fail-closed and immune to versioned directory upgrade drift.

#### Scenario: Post-upgrade re-signing and Homebrew link restoration
- **WHEN** automated maintenance updates coding agent CLIs or Python runtimes in `workstation_update.py` or `workstation-daily-update.sh`
- **THEN** any missing, broken, or unlinked `/opt/homebrew/bin/goose` path SHALL be restored via `brew link --overwrite block-goose-cli` to the active Homebrew Cellar binary
- **AND** `goose`, `Python.app` (`org.python.python`, `client_type = 0`), and `python3` SHALL be re-signed with `Developer Agent Code Signing` so their Designated Requirement matches `certificate leaf = H"65340d85afd298131c682d8463087891292a2b59"`
- **AND** `~/Developer/scripts/workstation-daily-update.sh` SHALL match `platform/openspec-store/scripts/workstation-daily-update.sh` and `config/script-provenance-manifest.tsv` with zero SHA-256 drift, using `has_unaligned_authority_drift()` / `Reconciled Authority Status` from `inventory-workstation-toolchain.py` in Stage 9 so aligned `updater_dispatch == "none"` `local-dev` entries (`prime-agent`) do not trigger false-positive `AUTHORITY_DRIFT_DETECTED=1`

#### Scenario: Scheduled LaunchAgent FDA supervision and fail-closed Darwin TCC verification
- **WHEN** `~/Library/LaunchAgents/com.developer.workstation-daily-update.plist` or an interactive operator executes `tcc_provenance.py --json` on Darwin
- **THEN** `com.developer.workstation-daily-update.plist` SHALL invoke `workstation-daily-update.sh` under `/opt/homebrew/opt/python@3.15/Frameworks/Python.framework/Versions/3.15/Resources/Python.app/Contents/MacOS/Python` (`CFBundleIdentifier = org.python.python`, `client_type = 0`) so `TCC.db` is readable with Full Disk Access across Python upgrades
- **AND** TCC provenance verification SHALL evaluate verified `client_type = 0` bundle records with active `auth_value = 2` grants and valid `SecStaticCodeCheckValidity = 0` signatures
- **AND** any unreadable/corrupt `TCC.db` or missing/mismatched target grant on Darwin SHALL be reported fail-closed as `ERROR` or `DRIFT` and SHALL NEVER be classified as `SKIPPED`

#### Scenario: Unattributed standalone or launchd CLI fails closed despite authorized Orca or Herdr in TCC.db
- **WHEN** `com.stablyai.orca` (`Orca.app`), `herdr`, and `org.python.python` hold valid `auth_value = 2` grants in `TCC.db`, but a CLI target runs directly from `launchd` without an authorized responsible parent bundle
- **THEN** `verify_tcc_provenance()` SHALL NOT mark the CLI `CLEAN` from unrelated supervisor rows
- **AND** `verify_tcc_provenance()` SHALL return `status: "DRIFT"` with the target listed in `missing_binaries` and `<service>:missing_grant` (or `denied_or_pending`) in `failure_reasons`
