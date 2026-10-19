# workstation-toolchain-inventory Spec Delta

## ADDED Requirements

### Requirement: Workstation toolchain manifest and inventory classification for Herdr

The workstation toolchain manifest and inventory scripts SHALL register `herdr` under `profiles.ai-agents` with `brew-formula` authoritative ownership, `brew` update authority, and `herdr --version` smoke verification.

#### Scenario: Herdr registered as Homebrew-formula AI agent tool in manifest
- **WHEN** the actual manifest and read-only inventory report are inspected
- **THEN** `tools.herdr` SHALL specify `authoritative_owner: "brew-formula"`, `active_path_pattern: "{{HOMEBREW_PREFIX}}/bin/herdr"`, `update_authority: "brew"`, `supported_verb: "brew upgrade herdr"`, and `verification_smoke_command: "herdr --version"`
- **AND** `herdr` SHALL be listed in `profiles.ai-agents` without containing literal user home paths

#### Scenario: Toolchain inventory classifies Herdr under Homebrew formula authority
- **WHEN** the read-only inventory evaluates Herdr's active executable
- **THEN** `herdr` SHALL resolve under its declared Homebrew formula authority without a Herdr-specific unknown-source or target-misalignment finding
- **AND** unrelated installed-tool findings SHALL remain visible rather than be suppressed to make this change pass

#### Scenario: Shadowed ~/.local/bin/herdr duplicate is flagged if present
- **WHEN** a standalone installer copy exists at `{{HOME}}/.local/bin/herdr` alongside `/opt/homebrew/bin/herdr`
- **THEN** the inventory SHALL report `{{HOME}}/.local/bin/herdr` as a shadow path under `known_shadow_paths`
