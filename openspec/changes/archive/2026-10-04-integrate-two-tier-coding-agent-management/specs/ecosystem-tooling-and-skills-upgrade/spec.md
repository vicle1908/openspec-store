# Spec Delta: ecosystem-tooling-and-skills-upgrade

## ADDED Requirements

### Requirement: Two-Tier Coding Agent Management and Homebrew-First Alignment
The workstation coding agent maintenance lifecycle SHALL adhere to a two-tier operational hierarchy:
1. **Tier 1 (Homebrew-First Preferred Channel)**: Coding agents distributed as Homebrew formulae or casks (`block-goose-cli`, `block-goose`, `grok-build`, `pi-coding-agent`) SHALL be managed and upgraded through Homebrew automation (`brew upgrade --formula` and `brew upgrade --cask`).
2. **Tier 2 (Official Native Command Channel)**: Coding agents distributed outside Homebrew (`prime-agent`, `claude`, `codex`, `opencode`, `kilo`, `auggie`, `qoder`) SHALL be declared in `AGENT_CLI_COVERED` and upgraded via their official CLI subcommands under timeout fences.

#### Scenario: Grok managed via official Homebrew cask
- **WHEN** `grok --version` or `which grok` is executed
- **THEN** the command resolves to `/opt/homebrew/bin/grok` provided by `grok-build` cask (v1.0.46+)
- **AND** `brew list --cask grok-build` confirms successful Homebrew cask tracking

#### Scenario: Daily maintenance executes both formula and cask upgrades
- **WHEN** `workstation-daily-update.sh` executes Stage 1 in apply mode
- **THEN** both `brew upgrade --formula` and `brew upgrade --cask` SHALL execute
- **AND** Homebrew-managed agent casks (`grok-build`, `block-goose`) receive automated upgrades

#### Scenario: Prime Agent native updater integration
- **WHEN** `workstation-daily-update.sh` executes Stage 5
- **THEN** `prime-agent` SHALL be included in the covered agent set
- **AND** in check mode it SHALL report its active version (`installed: prime-agent (0.9.8)`)
- **AND** in apply mode it SHALL invoke `prime-agent update` bounded by `AGENT_UPDATE_TIMEOUT`
