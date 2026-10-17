# workstation-toolchain-inventory Specification Delta

## ADDED Requirements

### Requirement: Workstation toolchain manifest registration and non-standard installation auditing

`config/workstation-toolchain-manifest.json` SHALL register `tools.orca` under `profiles.ai-agents` with `brew-cask` authoritative ownership, `orca --version` verification command, and `brew upgrade --cask stablyai/orca/orca` supported verb. Furthermore, workstation health inspections SHALL audit and report non-standard installations including corrupted Caskroom metadata receipts, orphaned or deprecated Homebrew formulae, shadowed duplicate binaries, and subshell PATH precedence inversions.

#### Scenario: Orca registered as first-class AI agent tool
- **WHEN** `config/workstation-toolchain-manifest.json` is validated by `python3 scripts/test-version-authority-governance.py`
- **THEN** `tools.orca` SHALL specify `authoritative_owner: "brew-cask"` and `update_authority: "brew"`
- **AND** `orca` SHALL be listed in `profiles.ai-agents`
- **AND** the test suite SHALL pass with exit code `0`

#### Scenario: Non-standard package installation and metadata audit reporting
- **WHEN** system-wide toolchain and package audits are performed
- **THEN** package managers SHALL report any corrupted Caskroom metadata (such as missing receipts in `/opt/homebrew/Caskroom/`), orphaned formulae with no upstream taps, deprecated versions, and shadowed duplicates in `~/.local/share/home-toolchain`
- **AND** the findings SHALL be recorded for operator remediation rather than silently discarded or destructively purged
