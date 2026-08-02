## Purpose

Defines machine-level resolution of OpenSpec commands to the registered shared
store in a workspace whose code repositories have no local planning roots.

## ADDED Requirements

### Requirement: The workspace SHALL have a machine-level default store

The OpenSpec global config SHALL declare `defaultStore openspec-store` so a
command outside a local planning root can resolve the registered shared store.

#### Scenario: Default store resolves when no local root exists

- **GIVEN** a code repo with no `openspec/` directory
- **WHEN** an OpenSpec command runs without `--store`
- **THEN** the command SHALL resolve to `openspec-store` and identify its
  registered root path in the root banner

#### Scenario: Explicit store selection overrides the default

- **GIVEN** the global default store is `openspec-store`
- **WHEN** a command runs with `--store other-store`
- **THEN** the command SHALL target `other-store`, not the default
