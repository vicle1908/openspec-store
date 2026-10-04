# Proposal: Integrate Two-Tier Coding Agent Management and Homebrew-First Alignment

## Why
The workstation hosts multiple AI coding agent engines (`goose`, `grok`, `prime-agent`, `claude`, `codex`, `opencode`, `kilo`, `auggie`, `qoder`, `pi`), but management channels were fragmented between Homebrew packages and standalone scripts. The workstation maintenance policy establishes a clear operational hierarchy: **Homebrew first for global package and cask management, followed by official native update commands for standalone binaries**. 

Currently, Grok operates on an outdated standalone binary (`1.0.34` in `~/.grok/bin/grok`) despite an official Homebrew cask (`grok-build@1.0.46`) existing in `homebrew/cask`. Goose is installed via Homebrew (`block-goose-cli` and `block-goose`), but the daily maintenance script omitted cask upgrades in apply mode. Prime Agent lacks a Homebrew tap upstream and relies on an official R2 binary updater (`prime-agent update`), but was omitted from the daily maintenance covered set.

## What Changes
- **Homebrew-First Cask Migration for Grok**:
  - Install official Homebrew cask `grok-build` (version `1.0.46`), linking `/opt/homebrew/bin/grok` and `/opt/homebrew/bin/agent` directly into `$PATH`.
  - Retire legacy standalone binary symlinks in `~/.grok/bin/` so system execution seamlessly uses the Homebrew-managed cask.
- **Homebrew Cask Coverage in Daily Maintenance (`workstation-daily-update.sh`)**:
  - Update Stage 1 in `workstation-daily-update.sh` to execute `brew upgrade --cask` in apply mode, ensuring `grok-build` and `block-goose` (Goose GUI) update automatically alongside Homebrew formulae.
- **Official Native Updater Integration for Prime Agent**:
  - Integrate `prime-agent:Prime Agent:update` into `AGENT_CLI_COVERED` in Stage 5 of `workstation-daily-update.sh`.
  - In check mode, report `installed: prime-agent (0.9.8)`.
  - In apply mode, execute `prime-agent update` bounded by `AGENT_UPDATE_TIMEOUT`.
- **Zero-Drift Script Parity**:
  - Synchronously apply maintenance script changes to both `~/Developer/scripts/workstation-daily-update.sh` and `platform/openspec-store/scripts/workstation-daily-update.sh` to maintain zero-drift content hash parity.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `ecosystem-tooling-and-skills-upgrade`: Extend requirements to define the two-tier coding agent management standard (Homebrew-first global channel, official native CLI updater channel) and require Homebrew cask upgrade automation in daily workstation maintenance.

## Non-Goals
- Attempting to author an unofficial Homebrew tap for `prime-agent` (upstream `PrimeIntellect-ai` maintains official R2 binary channels).
- Overriding Goose configuration or running `goose update` (Goose remains strictly managed under Homebrew `block-goose-cli` and `block-goose`).

## Affected Ownership Boundaries
- Workstation Maintenance: `~/Developer/scripts/workstation-daily-update.sh`
- OpenSpec Store: `platform/openspec-store/scripts/workstation-daily-update.sh`
- Homebrew Casks: `grok-build`, `block-goose`
