# workstation-toolchain-inventory Specification Delta

## MODIFIED Requirements

### Requirement: Sanctioned install locations

Workstation tooling SHALL be installed only into sanctioned roots (`~/.npm-global`, `~/.bun`, `~/.local/share/home-toolchain`, `/opt/homebrew`, `~/.local/share`, `~/.local/bin`, `~/.kimi-code`, `~/.qoder`, `~/.pi`, `~/.hermes`, `~/.grok`) and SHALL NOT be installed into unscoped `$HOME` directories (`~/node_modules` or `~/.local/lib/node_modules`).

#### Scenario: Tool installed into an unsanctioned location
- **WHEN** a node package is installed into a directory that is not a sanctioned location, such as `~/.local/lib/node_modules` or `~/node_modules`
- **THEN** the inventory SHALL report it as an unsanctioned installation
- **AND** the report SHALL identify the sanctioned location that would own it instead

#### Scenario: All installations are sanctioned
- **WHEN** every installed copy of every inventoried tool resolves into one of the sanctioned locations and no `~/node_modules` or `~/.local/lib/node_modules` exists
- **THEN** the inventory SHALL report no unsanctioned installations

### Requirement: Workstation toolchain manifest and inventory classification for OMP

The workstation toolchain manifest, Homebrew bundle manifest, updater registry, and inventory scripts SHALL register `omp` under `profiles.ai-agents` with `brew-formula` authoritative ownership (`can1357/tap/omp`, `/opt/homebrew/bin/omp`), `brew` update authority, `omp --version` smoke verification, and symlink-aware shadow-path (`os.path.lexists`) and Cellar source verification.

#### Scenario: OMP registered as Homebrew-formula AI agent tool in manifest and Brewfile
- **WHEN** `config/workstation-toolchain-manifest.json`, `config/Brewfile`, and `python3 -m unittest tests/test_portable_workstation_slice_a.py` are inspected and executed
- **THEN** `tools.omp` SHALL specify `authoritative_owner: "brew-formula"`, `active_path_pattern: "{{HOMEBREW_PREFIX}}/bin/omp"`, `update_authority: "brew"`, `release_channel: "stable"`, `dispatch_classification: "none"`, `verification_smoke_command: "omp --version"`, `writer_binary: "brew"`, `supported_verb: "brew upgrade can1357/tap/omp"`, `delegating_to: null`, `package_name: "can1357/tap/omp"`, and `category: "ai-agent"`
- **AND** `omp` SHALL be listed in `profiles.ai-agents` and `config/Brewfile`, and `test_portable_workstation_slice_a.py` and `scripts/test-version-authority-governance.py` SHALL exit `0`

#### Scenario: Toolchain inventory classifies OMP under Homebrew formula authority and monitors shadow paths
- **WHEN** `python3 scripts/inventory-workstation-toolchain.py --json` evaluates installed tools
- **THEN** `.manifest_reconciliation.items.aligned` SHALL contain an entry with `name: "omp"` and `state: "aligned"`, and `.authority_reconciliation.items` SHALL contain an entry with `name: "omp"`, `authority: "brew-formula"`, and `drift_status: "clean"` verified via `derive_install_root_and_source`
- **AND** `inventory_tools()` SHALL map `omp` to `@oh-my-pi/pi-coding-agent` and inspect `known_shadow_paths` (`{{HOME}}/.bun/bin/omp` and `{{HOME}}/.npm-global/bin/omp`) using symlink-aware existence checks (`sh_path.is_symlink() or sh_path.exists()`) so any non-Homebrew shadow binary or dangling symlink is flagged as a duplicate and `target_misalignment`

## ADDED Requirements

### Requirement: Core JavaScript runtime and package-manager manifest and global roster parity

`config/workstation-toolchain-manifest.json`, `scripts/toolchain_updater_registry.py`, `scripts/inventory-workstation-toolchain.py`, and `config/npm-global-tools.json` SHALL declare complete, non-overlapping ownership records for the core JavaScript/TypeScript runtimes and package managers (`node`, `npm`, `pnpm`, `bun`) and for all sanctioned CLI packages installed under `~/.npm-global`.

#### Scenario: Core JavaScript runtimes and package managers registered in manifest and updater registry
- **WHEN** `config/workstation-toolchain-manifest.json`, `scripts/toolchain_updater_registry.py`, and `scripts/inventory-workstation-toolchain.py` are validated by `tests/test_portable_workstation_slice_a.py` and `scripts/test-version-authority-governance.py`
- **THEN** `tools.node`, `tools.npm`, `tools.pnpm`, and `tools.bun` SHALL be declared in `config/workstation-toolchain-manifest.json` under `profiles.core` with `authoritative_owner: "brew-formula"`, `update_authority: "brew"`, `writer_binary: "brew"`, and `active_path_pattern` under `{{HOMEBREW_PREFIX}}/bin/`
- **AND** `derive_install_root_and_source()` in `scripts/inventory-workstation-toolchain.py` SHALL classify Homebrew's bundled `/opt/homebrew/lib/node_modules/npm` (and `/usr/local/lib/node_modules/npm`) under `brew-formula`
- **AND** `tools.bun` SHALL list `{{HOME}}/.bun/bin/bun` in `known_shadow_paths` and `tools.pnpm` SHALL list `{{HOME}}/Library/pnpm/pnpm` and `{{HOME}}/.npm-global/bin/pnpm` in `known_shadow_paths`
- **AND** `sanctioned_roots` in `config/workstation-toolchain-manifest.json` and `is_path_sanctioned()` in `scripts/inventory-workstation-toolchain.py` SHALL include `~/.bun`

#### Scenario: Sanctioned npm-global-tools.json matches installed global CLI packages without profile overlap
- **WHEN** `config/npm-global-tools.json` is compared against `npm list -g --depth=0 --prefix ~/.npm-global` and validated by `TestLayeredProfiles`
- **THEN** `config/npm-global-tools.json` SHALL declare all 15 sanctioned global CLI packages (`openspec`, `gitnexus`, `kilo`, `auggie`, `happy`, `agentmemory`, `agentmemory-mcp`, `brightdata`, `anydoc`, `grepai`, `mcpr`, `deepwiki`, `codexuse`, `exa`, `node-gyp`)
- **AND** the declared tool names in `config/npm-global-tools.json` SHALL remain strictly disjoint from `config/Brewfile` and `config/uv-tools.json`
