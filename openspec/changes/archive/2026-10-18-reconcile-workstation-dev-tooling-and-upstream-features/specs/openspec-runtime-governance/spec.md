# openspec-runtime-governance Specification Delta

## MODIFIED Requirements

### Requirement: Existing nearest-root topology remains authoritative

The workstation SHALL use the registered standalone OpenSpec store `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`) and machine-global `defaultStore: "openspec-store"` as the authoritative central planning root across multi-repository workflows, without relying on a workspace-root `~/Developer/openspec` compatibility symlink.

#### Scenario: Repository lacks a local OpenSpec symlink
- **WHEN** a command runs from a TDT or workspace repository without its own local `openspec/` root
- **THEN** it SHALL resolve `/Users/androidteam/Developer/platform/openspec-store` with `source: "store"` and `store_id: "openspec-store"`
- **AND** `openspec doctor --store openspec-store --json` SHALL report `"healthy": true`

#### Scenario: Default store is considered
- **WHEN** `openspec config list --json` is inspected on the workstation
- **THEN** `defaultStore` SHALL equal `"openspec-store"`

## ADDED Requirements

### Requirement: Single-owner OpenSpec CLI executable resolution

The `openspec` CLI SHALL resolve from a single authoritative installation (`~/.npm-global/bin/openspec` `@fission-ai/openspec@1.14.3+`) without a duplicate shadowed Homebrew `openspec` formula binary on `PATH`.

#### Scenario: Only one openspec binary exists on PATH
- **WHEN** `which -a openspec` and `openspec --version` are executed
- **THEN** `which -a openspec` SHALL return a single authoritative executable path reporting version `1.14.3` or newer
