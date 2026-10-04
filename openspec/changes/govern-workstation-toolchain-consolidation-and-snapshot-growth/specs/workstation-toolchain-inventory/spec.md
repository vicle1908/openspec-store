# Spec Delta

## Purpose

Defines the sanctioned install locations for workstation tooling, which location is
authoritative for a given tool, and how duplication across locations is detected and reported
before any copy is treated as reclaimable.

## ADDED Requirements

### Requirement: Sanctioned install locations

Workstation tooling SHALL be installed into one of the sanctioned locations only: the global npm
prefix `~/.npm-global`, the relocated toolbelt `~/.local/share/home-toolchain`, the system
package manager prefix, or a language-specific tool manager under `~/.local/share`. A tool
SHALL NOT be installed into an unscoped ad-hoc directory under `$HOME`.

#### Scenario: Tool installed into an unsanctioned location

- **WHEN** a node package is installed directly into `$HOME/node_modules` or another directory
  that is not a sanctioned location
- **THEN** the inventory SHALL report it as an unsanctioned installation
- **AND** the report SHALL identify the sanctioned location that would own it instead

#### Scenario: All installations are sanctioned

- **WHEN** every installed copy of every inventoried tool resolves into one of the sanctioned
  locations
- **THEN** the inventory SHALL report no unsanctioned installations

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

- **WHEN** a tool is present in more than one sanctioned location, as with a global command and
  a toolbelt dependency of the same name
- **THEN** the inventory SHALL report each location, its measured size, and which copy is
  authoritative
- **AND** it MUST NOT delete or relocate any copy without a separate operator authorization

### Requirement: Duplication is reported before it is reclaimable

Duplicated tool installations SHALL be reported with measured sizes and the identifiers of the
owning tools, and SHALL remain non-reclaimable until the owning tool is confirmed to resolve
correctly from the intended location alone.

#### Scenario: Duplicate is reported with its owner

- **WHEN** the inventory detects a tool installed in multiple locations
- **THEN** it SHALL record the tool name, each installation path, each measured size, and the
  owning package manager or tool manager for each
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
