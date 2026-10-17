# Spec Delta: portable-workstation-toolchain

## ADDED Requirements

### Requirement: Meta Muse Code CLI SHALL be governed under Homebrew cask `muse-code` with explicit collision disambiguation

Meta Muse Code (`muse`) SHALL be installed and updated exclusively through the official Homebrew cask `muse-code` (`/opt/homebrew/bin/muse`), registered in the workstation toolchain authority, manifest, and coverage registries as a Homebrew-managed cask, and explicitly disambiguated from the unrelated disabled desktop cask `muse`.

#### Scenario: Official Homebrew cask installation and single-owner PATH resolution
- **WHEN** Meta Muse Code CLI is provisioned or audited on macOS `arm64`
- **THEN** it SHALL be installed via `brew install --cask muse-code` into `/opt/homebrew/Caskroom/muse-code/` with its canonical executable symlinked at `/opt/homebrew/bin/muse`
- **AND** `which -a muse` across login and interactive shells SHALL resolve exclusively to `/opt/homebrew/bin/muse` without unmanaged duplicate binaries in `~/.local/bin` or `~/.npm-global/bin`

#### Scenario: Toolchain updater registry, manifest, and inventory disambiguation from disabled cask `muse`
- **WHEN** `toolchain_updater_registry.py`, `inventory-workstation-toolchain.py`, `config/workstation-toolchain-manifest.json`, and `reconcile-agent-cli-coverage.py` evaluate `muse`
- **THEN** `toolchain_updater_registry.py` SHALL declare `("muse", "brew-cask")` (and alias `("muse-code", "brew-cask")`) with `source_type="brew-cask"`, `supported_verb=None`, `updater_dispatch="none"`, `delegating_to="brew"`, and `status="uncovered_declared"`
- **AND** `inventory-workstation-toolchain.py` and `config/workstation-toolchain-manifest.json` SHALL classify executable `muse` under `authority="brew-cask"`, `writer="brew"`, `updater_dispatch="none"`, `preferred_source="cask muse-code"`, and `drift_status="clean"` with `0` unknown tools
- **AND** the inventory collision map SHALL record that Homebrew cask `muse` is an unrelated disabled desktop productivity app (`muse.ai`) and MUST NOT be substituted for `cask "muse-code"`

#### Scenario: Running Muse Code session exclusion during scheduled Homebrew cask upgrades
- **WHEN** the scheduled maintenance workflow (`workstation_update.py`) evaluates `muse-code` for a Homebrew cask upgrade while an active Muse Code CLI process is running
- **THEN** the process guard in `step_homebrew_update` SHALL check `pgrep -x` across `"muse-code"`, `"muse"`, and the resolved Mach-O binary name `"muse-aarch64-macos"`
- **AND** if any matching process is actively running, the upgrade of `muse-code` SHALL be skipped and recorded in `casks_skipped_running` without terminating or disrupting the active coding session
