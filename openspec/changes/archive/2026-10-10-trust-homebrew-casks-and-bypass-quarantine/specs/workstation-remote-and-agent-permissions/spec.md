# Spec Delta

## Purpose

Extends workstation remote and agent permissions to enforce automated trust for Homebrew Cask applications, preventing Gatekeeper quarantine prompts from blocking developer tools and automation agents.

## ADDED Requirements

### Requirement: Homebrew Cask applications SHALL bypass Gatekeeper quarantine attributes

Developer workstations SHALL configure Homebrew Cask options to prevent the attachment of `com.apple.quarantine` extended attributes on installed bundles, and existing application bundles SHALL maintain zero quarantine metadata.

#### Scenario: Persistent Cask options configuration
- **WHEN** user and system shell sessions initialize (`~/.zshrc`, `~/.zprofile`)
- **THEN** `HOMEBREW_CASK_OPTS="--no-quarantine"` SHALL be exported
- **AND** `brew config` SHALL report `HOMEBREW_CASK_OPTS: ["--no-quarantine"]`

#### Scenario: Application bundle quarantine attribute elimination
- **WHEN** installed bundles in `/Applications` and `/opt/homebrew/Caskroom` are inspected via `xattr`
- **THEN** no `com.apple.quarantine` attribute SHALL be present
- **AND** launching applications SHALL execute directly without Gatekeeper download confirmation dialogs
