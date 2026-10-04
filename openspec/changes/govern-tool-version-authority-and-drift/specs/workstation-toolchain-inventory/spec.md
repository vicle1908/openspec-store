# Spec Delta

## MODIFIED Requirements

### Requirement: Preferred package-manager source is used where one exists

Where a system package manager or a vendor package manager provides a tool and that tool's
official documentation names it as an installation channel, that source SHALL be preferred over
an unsigned external download or a manual placement, and the inventory SHALL report an
installation that bypasses an available documented source. Where official documentation names
more than one channel, the inventory SHALL record every documented channel rather than selecting
one on preference, and the choice SHALL be resolved by the version-authority rule.

#### Scenario: Homebrew ships the tool

- **WHEN** a tool is installed by means other than Homebrew while Homebrew provides it as a
  formula or cask, including a third-party tap or cask
- **THEN** the inventory SHALL report the available Homebrew asset and the current installation
  method
- **AND** the report SHALL identify the Homebrew-managed installation as a documented preferred
  source where the tool's documentation names Homebrew as an installation channel

#### Scenario: No package manager provides the tool

- **WHEN** no system or vendor package manager provides a tool, so it is available only through
  an ecosystem package manager or a vendor download
- **THEN** the inventory SHALL record that no preferred package-manager source exists
- **AND** the ecosystem package manager that owns it SHALL be recorded as its source of record

#### Scenario: Vendor documentation names multiple channels

- **WHEN** a tool's official documentation names both an ecosystem package manager and Homebrew
  as installation channels, as `codex` documents both `npm install -g @openai/codex` and
  `brew install --cask codex`
- **THEN** the inventory SHALL record both channels as documented
- **AND** the selection SHALL be resolved by the version-authority rule rather than by
  preference alone

## ADDED Requirements

### Requirement: Exactly one version authority per tool

Each tool SHALL have exactly one version authority: the mechanism permitted to determine the
version installed. Where a tool can update itself, its self-updater SHALL be recorded as its
version authority, and a package manager SHALL own that tool's version only when the package
manager's asset explicitly defers version control to the tool. The inventory SHALL report a tool
whose version is claimed by both a self-updater and a pinning package manager as a
version-authority drift defect.

#### Scenario: Self-updating tool installed through a deferring package asset

- **WHEN** a tool can update itself and its package-manager asset declares that the tool updates
  itself, as a cask carrying `auto_updates`
- **THEN** the tool's self-updater SHALL be recorded as the version authority
- **AND** the package manager SHALL be recorded as the installation channel only
- **AND** no drift defect SHALL be reported

#### Scenario: Self-updating tool installed through a pinning package asset

- **WHEN** a tool can update itself but its package-manager asset does not declare that the tool
  updates itself, as a cask or formula lacking `auto_updates`
- **THEN** the inventory SHALL report a version-authority drift defect naming both the
  self-updater and the pinning package manager
- **AND** it SHALL record the consequence that a package-manager upgrade reverts the version the
  tool installed for itself

#### Scenario: Tool does not self-update

- **WHEN** a tool provides no self-update mechanism and is installed through a package manager
- **THEN** the package manager SHALL be recorded as the version authority
- **AND** no drift defect SHALL be reported

#### Scenario: Version authority cannot be determined

- **WHEN** it cannot be determined whether a tool self-updates, or which asset owns its version
- **THEN** the inventory SHALL record the version authority as unknown together with the evidence
  gaps
- **AND** it MUST NOT report the tool as reconciled
