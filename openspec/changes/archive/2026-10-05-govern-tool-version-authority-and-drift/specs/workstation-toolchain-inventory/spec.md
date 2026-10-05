# Spec Delta

## MODIFIED Requirements

### Requirement: Preferred package-manager source is used where one exists

Where a system package manager or a vendor package manager provides a tool and that tool's
official documentation names it as an installation channel, that source SHALL be preferred over
an unsigned external download or a manual placement, and the inventory SHALL report an
installation that bypasses an available documented source. Where official documentation names
more than one channel, the inventory SHALL record every documented channel, and the version
authority SHALL be resolved by the active installation rather than by preference alone.

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
- **AND** the inventory SHALL record the installed copy's verified ecosystem manager or vendor
  release channel as its source of record, or record unknown ownership with evidence gaps

#### Scenario: Vendor documentation names multiple channels

- **WHEN** a tool's official documentation names both an ecosystem package manager and Homebrew
  as installation channels, as `codex` documents both `npm install -g @openai/codex` and
  `brew install --cask codex`
- **THEN** the inventory SHALL record both channels as documented
- **AND** the selection SHALL be resolved by the version-authority rule rather than by
  preference alone

#### Scenario: Active installation resolves channel tie

- **WHEN** a tool's documentation names multiple channels and the tool is installed via an
  authorized documented channel
- **THEN** the inventory SHALL recognize the active installation's channel as the authoritative
  source
- **AND** it MUST NOT report an uninstalled documented channel as bypassing a preferred source

## ADDED Requirements

### Requirement: Exactly one version authority per tool

Each installed tool SHALL have exactly one version authority: the single mechanism permitted to determine the version installed. The inventory SHALL record the active executable entrypoint, installing asset, update command, actual version writer, target scope, and release channel as distinct facts. Delegated commands SHALL NOT be recorded as separate writers. Where configured or scheduled independent writers target the same tool, the inventory SHALL report an authority conflict.

#### Scenario: Tool-native updater with compatible manager delegation

- **WHEN** a tool provides a native update command that inspects its installation context and delegates
  to its installing package manager, as `opencode upgrade` delegates to `brew upgrade`
- **THEN** the inventory SHALL record the installing manager as the actual version writer and the native
  command as a compatible update entrypoint
- **AND** no authority conflict SHALL be reported between that entrypoint and manager for that verified
  installation scope
- **AND** this determination SHALL NOT suppress any independently detected target, channel, or location
  findings

#### Scenario: Configured or scheduled independent writers produce authority conflict

- **WHEN** an installed tool has an active update mechanism and a configured or scheduled independent
  writer capable of modifying its installation without coordination
- **THEN** the inventory SHALL report a version-authority conflict finding naming both mechanisms and
  their write paths
- **AND** it SHALL record the consequence that uncoordinated updates risk version divergence or unintended
  reversion

#### Scenario: Update path presents target-misalignment risk

- **WHEN** an update action's effective write target (evaluated across environment variables, package
  receipts, and updater configuration) targets a directory or prefix different from the active
  installation root on `$PATH`
- **THEN** the inventory SHALL report a target-misalignment risk identifying the active installation root
  and the divergent write target
- **AND** this risk SHALL be reported distinctly from an authority conflict or measured version drift

#### Scenario: Tool without compatible native update path uses supported manager authority

- **WHEN** an installed tool has no compatible supported native update path for its active installation
  and is managed by a system or ecosystem package manager
- **THEN** the package manager SHALL be recorded as the actual version writer and authority
- **AND** no authority conflict SHALL be reported for that installation path

#### Scenario: Version authority or source version cannot be determined

- **WHEN** available evidence is insufficient to determine a tool's active executable provenance,
  actual version writer, or owning asset
- **THEN** the inventory SHALL record the version authority as unknown with explicit evidence gaps
- **AND** automated update actions for that tool SHALL be gated until resolved

### Requirement: Elected version authority governs tool updates and pipeline backstops

The elected version authority SHALL govern tool update handling across all pipeline mutation stages. Standalone local authority audits SHALL execute offline without mutations. Full check mode SHALL execute no update verbs and mutate no installations, configurations, or manager metadata. In apply mode, the pipeline SHALL invoke authorized update paths, verifying active entrypoint resolution on `$PATH` and active install root currency while respecting user background settings as-is.

#### Scenario: Local authority audit executes non-mutating check

- **WHEN** local inventory and coverage reporters execute during an authority audit or check run
- **THEN** they SHALL run locally without executing update verbs or mutating installations,
  configuration, or package-manager metadata
- **AND** standalone local reporter executions SHALL require no network access

#### Scenario: Pipeline apply mode invokes backstop via elected authority

- **WHEN** the maintenance pipeline runs in apply mode
- **THEN** it SHALL invoke the authorized update command for each eligible covered tool according to
  its elected version authority, permitting compatible native delegators or verified manager commands
- **AND** it MUST NOT execute unauthorized or misaligned write actions against that tool

#### Scenario: Backstop invocation is idempotent and verifies outcome

- **WHEN** the pipeline invokes an authorized update command for a tool that is already current
- **THEN** the invocation SHALL complete with an observable successful outcome without unintended
  version alteration
- **AND** the runner SHALL verify that the active executable entrypoint on `$PATH` resolves to the
  current version within the active installation root

#### Scenario: Native background auto-update status is audited as-is

- **WHEN** an installed tool provides native background auto-update configuration
- **THEN** the inventory SHALL audit and report the observed configuration settings as-is
- **AND** the pipeline MUST NOT mutate or overwrite the user's update configuration

#### Scenario: All mutation stages respect elected version authority

- **WHEN** the maintenance pipeline executes package-manager upgrade stages, including Homebrew, Bun,
  and npm
- **THEN** the pipeline SHALL guard package upgrades to exclude tools whose version authority is elected
  as native and lacks manager delegation
- **AND** it MUST NOT permit earlier stages to execute unauthorized writes against tools governed by
  later stages
