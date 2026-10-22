# Delta Specification: portable-workstation-toolchain

## ADDED Requirements

### Requirement: Coding agent binaries SHALL maintain persistent code-signing requirements across updates

Automated daily maintenance and package manager upgrades (`workstation-daily-update.sh`) SHALL ensure that updated canonical coding agent binaries (`goose`, `omp`, `claude`) are re-signed using a persistent local signing authority (`Developer Agent Code Signing`). This ensures their Designated Requirements (`designated => identifier ... and certificate leaf = H"..."`) remain invariant across releases, preventing macOS TCC permission drift without requiring repeated manual approvals.

#### Scenario: Post-update re-signing maintains stable designated requirement
- **WHEN** an automated update replaces a coding agent binary on disk (e.g. via Homebrew or npm)
- **THEN** the maintenance pipeline SHALL re-sign the executable using the local `Developer Agent Code Signing` identity
- **AND** the resulting Designated Requirement SHALL match the previously granted authority anchor in `TCC.db`
- **AND** `tcc_provenance.py` SHALL verify the binary without reporting permission drift

#### Scenario: Clean workspace skill surface enforcement
- **WHEN** cross-agent skills are checked for parity across the workspace
- **THEN** unallowlisted skill parent directories such as `data/skills` SHALL NOT exist
- **AND** `sync-workspace-agent-skills.py --check` SHALL exit code 0
