# portable-workstation-toolchain Specification Delta

## ADDED Requirements

### Requirement: Declarative Brewfile coverage for Orca IDE and active agent orchestrators

`config/Brewfile` in `platform/openspec-store` SHALL declare `cask "orca"` for the official Stably AI Orca IDE orchestrator (`stablyai/orca/orca` tap) alongside standard development applications, and operators SHALL verify its operational readiness via `orca status` following any install or upgrade.

#### Scenario: Brewfile declares Orca cask and bundle check passes
- **WHEN** `config/Brewfile` is evaluated via `HOMEBREW_NO_AUTO_UPDATE=1 brew bundle check --file config/Brewfile --no-upgrade`
- **THEN** `cask "orca"` SHALL be declared in `config/Brewfile`
- **AND** `brew bundle check` SHALL exit `0` confirming dependencies are satisfied

#### Scenario: Orca lifecycle and runtime health verification
- **WHEN** Orca is installed or updated on macOS
- **THEN** any hung, detached, or deadlocked background processes SHALL be terminated prior to bundle replacement
- **AND** `orca status` SHALL report `appRunning: true`, `runtimeState: ready`, `graphState: ready`, and `runtimeReachable: true` with an active desktop window
