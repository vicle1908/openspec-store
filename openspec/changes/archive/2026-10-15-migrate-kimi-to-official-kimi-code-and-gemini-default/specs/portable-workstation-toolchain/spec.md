# Spec Delta: portable-workstation-toolchain

## ADDED Requirements

### Requirement: Kimi Code CLI SHALL maintain official vendor standalone installation and single-owner PATH resolution

The Kimi coding agent SHALL be installed exclusively through Moonshot AI's official standalone native installer, isolated in `~/.kimi-code/bin`, eliminating outdated Homebrew shims, and resolving consistently across login and interactive shells.

#### Scenario: Vendor-supported standalone native installation
- **WHEN** Kimi Code CLI is provisioned or upgraded
- **THEN** it SHALL be installed using Moonshot AI's official installer into `~/.kimi-code/bin/kimi`
- **AND** outdated Homebrew formulae (`kimi-code`) SHALL be uninstalled to avoid path shadowing and version drift

#### Scenario: Single-owner PATH resolution
- **WHEN** user and system login and interactive shells initialize (`~/.zprofile`, `~/.zshrc`)
- **THEN** `export PATH="$HOME/.kimi-code/bin:$PATH"` SHALL be declared
- **AND** `which kimi` SHALL resolve strictly to `/Users/androidteam/.kimi-code/bin/kimi`

#### Scenario: Legacy data migration to kimi-code
- **WHEN** legacy Kimi data exists in `~/.kimi`
- **THEN** `kimi migrate --run` SHALL migrate configurations, MCP servers, history, and sessions into `~/.kimi-code`
- **AND** a completion marker SHALL be recorded to prevent repeated interactive migration prompts
