# Spec Delta

## Purpose

Defines the sanctioned install locations for workstation tooling, the single declared npm global
prefix, the preferred package-manager source per tool, the authoritative-location rule, and how
duplication and name collisions are detected and reported before any copy is treated as
reclaimable.

## ADDED Requirements

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

Where a system package manager or a vendor package manager provides a tool, that source SHALL be
preferred over an unsigned external download or a manual placement, and the inventory SHALL
report an installation that bypasses an available preferred source.

#### Scenario: Homebrew ships the tool

- **WHEN** a tool is installed by means other than Homebrew while Homebrew provides it as a
  formula or cask, including a third-party tap or cask
- **THEN** the inventory SHALL report the available Homebrew asset and the current installation
  method
- **AND** the report SHALL identify the Homebrew-managed installation as the preferred source

#### Scenario: No package manager provides the tool

- **WHEN** no system or vendor package manager provides a tool, so it is available only through
  an ecosystem package manager or a vendor download
- **THEN** the inventory SHALL record that no preferred package-manager source exists
- **AND** the ecosystem package manager that owns it SHALL be recorded as its source of record

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
