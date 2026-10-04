# Design: Integrate Two-Tier Coding Agent Management and Homebrew-First Alignment

## Context
See `proposal.md`. The workstation hosts 10+ AI coding agent tools across varying distribution mechanisms. A strict preference for Homebrew global management avoids fragmented ad-hoc binary downloads, while maintaining official native CLI updaters for tools without Homebrew distribution channels.

## Goals / Non-Goals

**Goals:**
- Migrate Grok from `~/.grok/bin/grok` (1.0.34) to official Homebrew cask `grok-build` (1.0.46).
- Confirm Goose under Homebrew management (`block-goose-cli` and `block-goose`).
- Add `brew upgrade --cask` to `workstation-daily-update.sh` Stage 1.
- Add `prime-agent:Prime Agent:update` to `AGENT_CLI_COVERED` in `workstation-daily-update.sh` Stage 5.
- Maintain exact content hash parity between `~/Developer/scripts/workstation-daily-update.sh` and `platform/openspec-store/scripts/workstation-daily-update.sh`.

**Non-Goals:**
- Modifying `pi-coding-agent` or `claude`/`codex` update pathways.
- Running `goose update` directly (delegated to Homebrew Stage 1).

## Decisions

### Decision 1: Homebrew Cask `grok-build` over internal updater
- **Rationale**: `grok-build` is the official Homebrew cask maintained in `homebrew/cask`, delivering version `1.0.46`. Installing via brew places binaries in `/opt/homebrew/bin/` (higher priority in `$PATH` than `~/.grok/bin`), ensuring automated management in Stage 1 without manual intervention.

### Decision 2: Add `brew upgrade --cask` to Stage 1
- **Rationale**: Stage 1 previously only ran `brew upgrade --formula` in apply mode. Running both formula and cask upgrades ensures `grok-build` and `block-goose` update automatically without running standalone CLI updaters that could unlink Cellar paths.

### Decision 3: Declare `prime-agent:Prime Agent:update` in `AGENT_CLI_COVERED`
- **Rationale**: `prime-agent update` connects to Prime Intellect's official R2 channel. When up to date, it exits 0 in <2 seconds. Adding it to `AGENT_CLI_COVERED` provides timeout protection and check-mode version reporting (`0.9.8`).
