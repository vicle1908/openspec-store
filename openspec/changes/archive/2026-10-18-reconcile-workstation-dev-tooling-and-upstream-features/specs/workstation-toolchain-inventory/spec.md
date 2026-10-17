# workstation-toolchain-inventory Specification Delta

## ADDED Requirements

### Requirement: Manifest and registry single-owner alignment for dual-installed and standalone tools

`config/workstation-toolchain-manifest.json`, `config/npm-global-tools.json`, `config/uv-tools.json`, `config/Brewfile`, and `scripts/toolchain_updater_registry.py` SHALL declare consistent single-owner records for `codex`, `opencode`, `openspec`, `newman`, `hermes`, `qwen`, `ruff`, `pytest`, `prime-agent`, `cce`, `goose`, `droid`, and `copilot-cli`.

#### Scenario: Manifest and Brewfile agree on Homebrew Cask/Formula vs npm-global authority
- **WHEN** `inventory-workstation-toolchain.py --json` evaluates `codex`, `opencode`, `openspec`, `newman`, `ruff`, `pytest`, `qwen`, `prime-agent`, `cce`, and `hermes`
- **THEN** `codex` and `opencode` SHALL have a single declared authority matching `config/Brewfile` (`brew-cask` `codex` and `brew-formula` `anomalyco/tap/opencode`) once shadowed `~/.npm-global` duplicates are reclaimed
- **AND** `openspec` SHALL declare `npm-global` (`~/.npm-global/bin/openspec`, `@fission-ai/openspec`) as its sole authority once the undeclared `/opt/homebrew/bin/openspec` formula is removed
- **AND** `hermes` (`hermes-agent`) SHALL declare `standalone` (`~/.hermes/hermes-agent`, updated via `hermes update`) rather than an uninstalled `brew-formula`
- **AND** `qwen` (`qwen-code`), `newman`, `ruff`, and `pytest` SHALL declare `brew-formula` matching their `/opt/homebrew/bin/` installations

### Requirement: Sanitized reporter PATH and vendor-download recognition for Qoder and Kimi

`inventory-workstation-toolchain.py` SHALL include `~/.qoder` and `~/.kimi-code` in `sanctioned_roots`, include `~/.qoder/entry` and `~/.kimi-code/bin` in its inspection `PATH`, and classify `~/.qoder/bin/qodercli/qodercli-*` and `~/.kimi-code/bin/kimi` as sanctioned `vendor_download` installations rather than misaligned npm packages.

#### Scenario: Qoder, qodercli, and kimi resolve cleanly without false-positive target misalignment
- **WHEN** `inventory-workstation-toolchain.py --json` runs in standalone or scheduled check mode
- **THEN** `qoder` (`~/.qoder/entry/qoder`), `qodercli` (`~/.local/bin/qodercli` -> `~/.qoder/bin/qodercli/*`), and `kimi` (`~/.kimi-code/bin/kimi`) SHALL resolve as `INSTALLED` under `vendor_download` authority
- **AND** none of the three tools SHALL emit a false-positive `TARGET_MISALIGNMENT`, `NOT_INSTALLED`, or unsanctioned-location defect

### Requirement: Homebrew Cellar symlink integrity and Cask self-update reconciliation

The inventory and operator runbook SHALL detect unlinked regular binaries in `/opt/homebrew/bin/` that shadow newer Homebrew Cellar versions (such as `/opt/homebrew/bin/goose` `1.54.0` blocking `/opt/homebrew/Cellar/block-goose-cli/1.55.0`) and Cask binaries mutated in-place by internal self-updaters (`droid` `0.238.0` Caskroom receipt vs `0.242.0` binary vs `0.244.0` upstream).

#### Scenario: Unlinked Homebrew binary blocking Cellar symlink is reconciled
- **WHEN** `/opt/homebrew/bin/goose` is a regular file (`1.54.0`) while `/opt/homebrew/Cellar/block-goose-cli/1.55.0` is installed
- **THEN** operator-authorized `brew link --overwrite block-goose-cli` SHALL restore the symlink to Cellar `1.55.0`
- **AND** `goose --version` SHALL report `1.55.0`

#### Scenario: Cask receipt drift is reconciled via Homebrew Cask upgrade
- **WHEN** `droid` (`0.238.0` Cask receipt / `0.242.0` binary) and `copilot-cli` (`1.0.95` Cask) lag upstream (`0.244.0` and `1.0.98`)
- **THEN** upgrading via `brew upgrade --cask droid copilot-cli` SHALL align both the Caskroom receipt and active binary version with upstream

### Requirement: Multi-root duplicate reclamation gates for gitnexus, bun, newman, and buf

Before reclaiming duplicate installations of `gitnexus` (`~/.local/share/home-toolchain` and `~/.local/lib/node_modules/gitnexus`, ~1.21 GiB), `bun` (`~/.bun/bin/bun`), `newman`, and `~/go/bin/buf`, the inventory SHALL record each path and size (including `opencode-ai` in `node_modules`) and verify post-removal resolution from the sole authoritative path.

#### Scenario: Authoritative gitnexus and buf remain functional after duplicate cleanup
- **WHEN** duplicate non-authoritative copies of `gitnexus` and `~/go/bin/buf` (`1.72.0`) are removed under operator authorization
- **THEN** `which gitnexus` SHALL resolve to `~/.npm-global/bin/gitnexus` (`1.6.12`) and `which buf` SHALL resolve to `/opt/homebrew/bin/buf` (`1.74.0`) with exit status `0`
