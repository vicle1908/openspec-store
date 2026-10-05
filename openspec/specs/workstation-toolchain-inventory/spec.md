# workstation-toolchain-inventory Specification

## Purpose
Defines the sanctioned install locations for workstation tooling, the single declared npm global
prefix, the preferred package-manager source per tool, the authoritative-location rule, and how
duplication and name collisions are detected and reported before any copy is treated as
reclaimable.

## Requirements

### Requirement: Sanctioned install locations

Workstation tooling SHALL be installed into one of the sanctioned locations only: the declared
npm global prefix, the relocated toolbelt `~/.local/share/home-toolchain`, the system
package-manager prefix, or a language-specific tool manager under `~/.local/share`. A tool
SHALL NOT be installed into an unscoped ad-hoc directory under `$HOME`.

#### Scenario: Tool installed into an unsanctioned location

- **WHEN** a node package is installed into a directory that is not a sanctioned location, such
  as `~/.local/lib/node_modules`
- **THEN** the inventory SHALL report it as an unsanctioned installation
- **AND** the report SHALL identify the sanctioned location that would own it instead

#### Scenario: All installations are sanctioned

- **WHEN** every installed copy of every inventoried tool resolves into one of the sanctioned
  locations
- **THEN** the inventory SHALL report no unsanctioned installations

### Requirement: The declared npm global prefix is authoritative and singular

The workstation SHALL declare exactly one npm global prefix, and the prefix npm reports for
`npm prefix` SHALL equal the prefix the maintenance pipeline installs globals into. Where these
disagree, the inventory SHALL report the disagreement as an unsanctioned split rather than
treating either location as correct.

#### Scenario: npm's effective prefix disagrees with the intended prefix

- **WHEN** npm's reported global prefix differs from the prefix the maintenance pipeline passes
  to `npm install -g`, as when `node` is installed by the system package manager and sets npm's
  default prefix while the pipeline targets a user prefix
- **THEN** the inventory SHALL report both prefixes, identify which one `npm install -g` without
  `--prefix` would use, and identify which one the pipeline uses
- **AND** it SHALL classify the split as a defect to be reconciled by declaration

#### Scenario: Prefixes agree

- **WHEN** npm's reported global prefix equals the prefix the maintenance pipeline installs into
  and equals the declared prefix
- **THEN** the inventory SHALL report the prefix as reconciled
- **AND** no prefix defect SHALL be raised

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

### Requirement: Homebrew-adjacent installations are not misattributed

An installation whose executable is a symbolic link placed inside the system package manager's
binary directory, but which resolves into an ecosystem package manager's module directory, SHALL
be recorded as owned by the ecosystem package manager and SHALL NOT be reported as
package-manager-managed.

#### Scenario: Ecosystem install symlinked into the package manager's bin directory

- **WHEN** an executable under the system package manager's `bin` directory resolves, through a
  symbolic link, into another package manager's global module directory
- **THEN** the inventory SHALL report the resolved target's owning package manager as the owner
- **AND** it SHALL report the package manager as not owning that installation

#### Scenario: Genuinely package-manager-managed installation

- **WHEN** an executable under the package manager's `bin` directory resolves into the package
  manager's own versioned cellar or caskroom
- **THEN** the inventory SHALL report the package manager as the owner

### Requirement: Name collisions are recorded before a migration is proposed

Where a preferred source provides a similarly named but different tool, the collision SHALL be
recorded and the tools SHALL be distinguished, so that a migration to the preferred source cannot
silently replace one tool with another.

#### Scenario: Preferred source provides a different tool of the same name

- **WHEN** a package manager provides an asset whose name matches an installed tool but whose
  purpose differs, or which originates from a different upstream
- **THEN** the inventory SHALL record both the installed tool's identity and the available
  asset's identity
- **AND** it MUST NOT propose replacing the installed tool with that asset

#### Scenario: Preferred source shadows another package

- **WHEN** a package manager's available asset for a tool originates from a third-party tap and
  shadows a package of the same name in the primary tap
- **THEN** the inventory SHALL record the originating tap
- **AND** the shadowing relationship SHALL be reported alongside the preferred-source result

### Requirement: Authoritative location per tool

Each tool SHALL have exactly one authoritative installation, defined as the copy the shell
resolves when the tool is invoked by name. Every other installed copy of the same tool SHALL be
classified as a duplicate and marked non-authoritative.

#### Scenario: Tool resolves to a determined copy

- **WHEN** a tool is invoked by name
- **THEN** the inventory SHALL record the resolved executable path as that tool's authoritative
  installation
- **AND** it SHALL record every other copy of the same tool as a duplicate

#### Scenario: Duplicate copies exist

- **WHEN** a tool is present in more than one sanctioned location, as with a global command and a
  toolbelt dependency of the same name
- **THEN** the inventory SHALL report each location, its measured size, and which copy is
  authoritative
- **AND** it MUST NOT delete or relocate any copy without separate operator authorization

### Requirement: Duplication is reported before it is reclaimable

Duplicated tool installations SHALL be reported with measured sizes and the identifiers of the
owning tools, and SHALL remain non-reclaimable until the owning tool is confirmed to resolve
correctly from the intended location alone.

#### Scenario: Duplicate is reported with its owner

- **WHEN** the inventory detects a tool installed in multiple locations
- **THEN** it SHALL record the tool name, each installation path, each measured size, and the
  owning package manager for each
- **AND** the total reclaimable estimate SHALL be labelled an estimate, not a guarantee

#### Scenario: Removal is not implied by duplication

- **WHEN** a duplicate installation is identified
- **THEN** the inventory MUST NOT remove it
- **AND** it SHALL state the verification required before the duplicate can be reclaimed

### Requirement: Path resolution correctness is verifiable

The inventory SHALL verify that each tool still resolves and executes from its authoritative
location after any consolidation, so that removing a duplicate cannot silently break the tool.

#### Scenario: Authoritative tool still executes after consolidation

- **WHEN** a duplicate installation is reclaimed
- **THEN** the authoritative installation's entry point SHALL execute and report a version with
  exit status zero

#### Scenario: Tool fails to resolve after consolidation

- **WHEN** a tool no longer resolves or executes after a duplicate is reclaimed
- **THEN** the consolidation SHALL be treated as failed and the duplicate restored
- **AND** the inventory SHALL record the failing resolution path

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

### Requirement: Supported updater declarations are conservative and installation-aware

The inventory and coverage reports SHALL recognize an update command only when the command is verified for the tool and active installation source in the supported-updater registry. An absent, ambiguous, or unverified command MUST be reported as having no supported automated update path and MUST be excluded from automated mutation.

#### Scenario: Unverified command is rejected
- **WHEN** a declaration contains a nonempty command that is not registered for the tool and active source
- **THEN** the report SHALL classify the updater as unsupported or unknown
- **AND** the maintenance runner MUST NOT execute that command

#### Scenario: Kilo uses its supported command
- **WHEN** Kilo is installed through the active npm channel and its supported CLI command is inspected
- **THEN** the recorded command SHALL be `kilo upgrade`
- **AND** the report MUST NOT advertise `kilo update`

### Requirement: Wrapper entrypoints inherit resolved target authority

A wrapper or symlink entrypoint SHALL inherit the resolved target's installation source, actual writer, target scope, drift status, and update eligibility. Surface wrapper location or display name MUST NOT create a separate authority or bypass a target gate.

#### Scenario: Qoder wrapper targets a misaligned npm package
- **WHEN** `qoder` resolves through its wrapper to an npm package whose active target is prefix-misaligned
- **THEN** the inventory SHALL report the wrapper with the target's misalignment
- **AND** the pipeline SHALL deny the wrapper without a tool-name-specific exception

#### Scenario: Wrapper target cannot be resolved
- **WHEN** a wrapper target or its ownership evidence cannot be resolved
- **THEN** the report SHALL classify authority as unknown with an evidence gap
- **AND** automated mutation for the wrapper MUST be gated

### Requirement: Homebrew Node-backed formulas remain Homebrew-owned

A resolved path under a Homebrew Cellar or Caskroom SHALL remain package-manager-owned even when the path contains `node_modules` or a scoped package segment. Inventory duplication output SHALL include both the authoritative copy and every discovered duplicate.

#### Scenario: Cellar formula embeds node_modules
- **WHEN** a Homebrew formula executable resolves through `Cellar/.../libexec/.../node_modules/...`
- **THEN** the source SHALL be reported as Homebrew formula ownership
- **AND** it MUST NOT be reported as an ecosystem package symlink solely because `node_modules` appears in the path

#### Scenario: Authoritative copy coexists with a duplicate
- **WHEN** the active copy and another sanctioned copy of the same tool are discovered
- **THEN** the duplication report SHALL include both copies with authority labels and measured metadata
- **AND** it MUST NOT report a clean single-copy state

### Requirement: Remediation targets preserve the declared npm prefix

When an ecosystem-managed installation is outside the declared npm prefix, remediation guidance SHALL identify the declared sanctioned prefix as the migration target and SHALL distinguish that recommendation from the currently active root. It MUST NOT recommend writing to an inferred system prefix merely because the active package resides there.

#### Scenario: Scoped package is active under Homebrew
- **WHEN** a scoped npm package is active under `/opt/homebrew` while the declared global prefix is the user npm prefix
- **THEN** the report SHALL identify the active root as misaligned
- **AND** any migration command SHALL target the declared user prefix

### Requirement: Pause state is normalized and applied consistently

The reporters SHALL normalize boolean, numeric, and string representations of update-pause settings, including `DISABLE_UPDATES` and `DISABLE_AUTOUPDATER`, and SHALL apply a global pause policy to every covered tool without changing the user's configuration.

#### Scenario: Boolean pause setting is enabled
- **WHEN** a supported configuration contains `DISABLE_UPDATES=true`, `1`, or boolean `true`
- **THEN** the report SHALL mark automated updates paused
- **AND** the pipeline MUST skip eligible update mutations while retaining audit output

#### Scenario: Pause setting is absent
- **WHEN** no recognized pause setting is enabled
- **THEN** the report SHALL not mark tools paused solely from an unrelated configuration key
- **AND** normal authority gating SHALL still apply

### Requirement: Scheduled writer discovery is value-blind and bounded

The inventory SHALL inspect accessible user LaunchAgents, accessible system LaunchAgents, and the user's crontab for candidate update writers, recording only structural metadata and environment-variable keys. It SHALL state that root-owned LaunchDaemons, inaccessible system jobs, container engines, and arbitrary script indirection are outside the scan boundary.

#### Scenario: Scheduled updater is visible
- **WHEN** an accessible launchd plist or user crontab entry invokes a recognized package-manager or tool updater
- **THEN** the report SHALL identify its label or schedule, executable baseline, source path, and relevant environment-key names
- **AND** it MUST NOT emit environment values, tokens, passwords, or raw command secrets

#### Scenario: Scheduled writer is outside scope
- **WHEN** a possible writer is hidden behind inaccessible system ownership or arbitrary script indirection
- **THEN** the report SHALL record the bounded unknown or limitation
- **AND** it MUST NOT claim that no competing writer exists
