# portable-workstation-toolchain Specification Delta

## ADDED Requirements

### Requirement: Declarative Brewfile coverage for workstation CLIs and local embedding services

`config/Brewfile` in `platform/openspec-store` SHALL declare `tap "anomalyco/tap"`, `brew "anomalyco/tap/opencode"`, `brew "block-goose-cli"`, `brew "googleworkspace-cli"`, `brew "newman"`, `brew "ollama"`, `brew "qwen-code"`, `brew "ruff"`, `cask "copilot-cli"`, `cask "droid"`, `cask "grok-build"`, and `cask "muse-code"` alongside the core workstation formulae and casks so `brew bundle check` verifies the complete Homebrew-governed tool surface.

#### Scenario: Brewfile declares all Homebrew-governed agent CLIs, utilities, and embedding services
- **WHEN** `config/Brewfile` is inspected or validated via `HOMEBREW_NO_AUTO_UPDATE=1 brew bundle check --file config/Brewfile --no-upgrade`
- **THEN** `tap "anomalyco/tap"`, `brew "anomalyco/tap/opencode"`, `brew "block-goose-cli"`, `brew "googleworkspace-cli"`, `brew "newman"`, `brew "ollama"`, `brew "qwen-code"`, `brew "ruff"`, `cask "copilot-cli"`, `cask "droid"`, `cask "grok-build"`, and `cask "muse-code"` SHALL be present in `config/Brewfile`
- **AND** `brew bundle check` SHALL exit `0` without missing dependency findings

### Requirement: Deterministic Zsh PATH deduplication and Homebrew-first precedence

Interactive and login Zsh initialization (`~/.zshenv`, `~/.zprofile`, `~/.zshrc`) SHALL enforce unique `PATH` entries via `typeset -U path PATH`, maintain `/opt/homebrew/bin` ahead of `~/.npm-global/bin` as documented in `docs/mac-development-setup.md`, expose `/opt/homebrew/opt/libpq/bin` for `psql`, explicitly filter out inherited `~/.orbstack/bin` entries via `path=(${path:#"$HOME/.orbstack/bin"})`, and guard `~/.iterm2_shell_integration.zsh` behind `[[ -t 0 && -t 1 ]]`.

#### Scenario: Interactive and inherited shells preserve Homebrew precedence, deduplicate PATH, and strip OrbStack
- **WHEN** a fresh login shell (`zsh -ilc 'print -l $path'`) or a subshell inheriting `PATH="$HOME/.orbstack/bin:$PATH"` (`PATH="$HOME/.orbstack/bin:$PATH" zsh -ic 'print -l $path'`) is evaluated
- **THEN** `/opt/homebrew/bin` SHALL appear before `/Users/androidteam/.npm-global/bin`
- **AND** `/opt/homebrew/opt/libpq/bin` SHALL be present on `PATH` so `which psql` resolves to `/opt/homebrew/opt/libpq/bin/psql`
- **AND** `/Users/androidteam/.orbstack/bin` SHALL be absent from `$path`
- **AND** no directory entry (including `/Users/androidteam/.kimi-code/bin`) SHALL appear more than once in `$path`

#### Scenario: Non-TTY interactive subshells do not emit iTerm2 OSC escape sequences
- **WHEN** a non-TTY interactive subshell (`zsh -ic 'echo READY' </dev/null`) is executed by an automation or diagnostic runner
- **THEN** `~/.iterm2_shell_integration.zsh` SHALL be skipped when standard input or output is not a TTY
- **AND** stdout SHALL begin cleanly with `READY` without leading `\e]1337;` escape sequences

### Requirement: Primary DBOS daily workflow executes health, snapshot, and inventory reporters

The primary scheduled maintenance workflow (`shb-schedule` `workstation_update.py`) and its fallback wrapper (`workstation-daily-update.sh`) SHALL execute `measure-snapshot-growth.py`, `inventory-workstation-toolchain.py`, and `reconcile-agent-cli-coverage.py` on every `apply` run before recording final run telemetry, and SHALL include `ntn update` in the standalone CLI update stage.

#### Scenario: Apply mode executes Stages 8-10 health reporters before completion
- **WHEN** `workstation-daily-update.sh` runs in `apply` mode via `shb-schedule run-now workstation-daily-update`
- **THEN** the workflow SHALL execute snapshot growth measurement, toolchain inventory drift inspection, and agent CLI coverage reconciliation before writing `~/Developer/data/updates/YYYY-MM-DD.json`
- **AND** any exceeded snapshot ceiling or authority conflict SHALL mark the run status degraded rather than silently exiting `0`

#### Scenario: Standalone Notion CLI update included in daily maintenance
- **WHEN** the standalone CLI update stage runs in `workstation_update.py` or `workstation-daily-update.sh`
- **THEN** `ntn` (`~/.local/bin/ntn`) SHALL be probed via `ntn --version` and updated via `ntn update`

### Requirement: LaunchAgent directory hygiene and script provenance completeness

`~/Library/LaunchAgents/` SHALL contain only active `.plist` definitions without backup `.bak*` files sharing active `Label` identifiers, and all active workstation helper scripts invoked by LaunchAgents (including `~/Developer/scripts/omniroute-watchdog.sh`) SHALL be tracked in `config/script-provenance-manifest.tsv` and documented in `~/Developer/scripts/README.md`.

#### Scenario: No duplicate-label backup plists in LaunchAgents directory
- **WHEN** `~/Library/LaunchAgents/` is scanned for plist and backup files
- **THEN** backup files such as `ai.hermes.gateway.plist.bak-*` SHALL reside outside `~/Library/LaunchAgents/`
- **AND** every active LaunchAgent script under `~/Developer/scripts/` SHALL have a matching SHA-256 entry in `config/script-provenance-manifest.tsv`

#### Scenario: Failing LaunchAgents are remediated against SIGPIPE and stale paths
- **WHEN** `launchctl list` is inspected for `com.omniroute.update-check`, `com.victory1908.hermes-webui`, and `Antigravity Tools`
- **THEN** `~/Omniroute/scripts/check-upstream.sh` SHALL guard `REMOTE_DIGEST` against `awk` early-exit `SIGPIPE` (`awk '/^Digest:/ && !found {print $2; found=1}' || true`) with `HOME` and `/opt/homebrew/bin` exported so `com.omniroute.update-check` exits `0` instead of `255`
- **AND** `com.victory1908.hermes-webui.plist` SHALL reference `/Users/androidteam/Developer/platform/hermes-webui` and `Antigravity Tools.plist` SHALL reference `/Applications/Antigravity Tools.app/Contents/MacOS/antigravity-tools` so neither exits with `EX_CONFIG` (`78`)
