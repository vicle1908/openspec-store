# Spec Delta

## ADDED Requirements

### Requirement: Workstation toolchain manifest and inventory classification for OMP

The workstation toolchain manifest, Homebrew bundle manifest, updater registry, and inventory scripts SHALL register `omp` under `profiles.ai-agents` with `brew-formula` authoritative ownership (`can1357/tap/omp`, `/opt/homebrew/bin/omp`), `brew` update authority, `omp --version` smoke verification, and active shadow-path and Cellar source verification.

#### Scenario: OMP registered as Homebrew-formula AI agent tool in manifest and Brewfile
- **WHEN** `config/workstation-toolchain-manifest.json`, `config/Brewfile`, and `python3 -m unittest tests/test_portable_workstation_slice_a.py` are inspected and executed
- **THEN** `tools.omp` SHALL specify `authoritative_owner: "brew-formula"`, `active_path_pattern: "{{HOMEBREW_PREFIX}}/bin/omp"`, `update_authority: "brew"`, `release_channel: "stable"`, `dispatch_classification: "none"`, `verification_smoke_command: "omp --version"`, `writer_binary: "brew"`, `supported_verb: "brew upgrade can1357/tap/omp"`, `delegating_to: null`, `package_name: "can1357/tap/omp"`, and `category: "ai-agent"`
- **AND** `omp` SHALL be listed in `profiles.ai-agents` and `config/Brewfile`, and `test_portable_workstation_slice_a.py` and `scripts/test-version-authority-governance.py` SHALL exit `0`

#### Scenario: Toolchain inventory classifies OMP under Homebrew formula authority and monitors shadow paths
- **WHEN** `python3 scripts/inventory-workstation-toolchain.py --json` evaluates installed tools
- **THEN** `.manifest_reconciliation.items.aligned` SHALL contain an entry with `name: "omp"` and `state: "aligned"`, and `.authority_reconciliation.items` SHALL contain an entry with `name: "omp"`, `authority: "brew-formula"`, and `drift_status: "clean"` verified via `derive_install_root_and_source`
- **AND** `inventory_tools()` SHALL map `omp` to `@oh-my-pi/pi-coding-agent` and inspect `known_shadow_paths` (`{{HOME}}/.bun/bin/omp` and `{{HOME}}/.npm-global/bin/omp`) so any non-Homebrew shadow binary is flagged as a duplicate and `target_misalignment`
