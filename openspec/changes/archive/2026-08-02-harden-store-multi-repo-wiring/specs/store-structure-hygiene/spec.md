## Purpose

Ensures the shared store contains no accidental nested copy of the official
OpenSpec directory structure.

## ADDED Requirements

### Requirement: The store SHALL NOT contain spurious nested directories

The store SHALL not contain a directory that duplicates the official structure,
such as `openspec/openspec/`.

#### Scenario: No nested openspec directory exists

- **GIVEN** the store's `openspec/` directory
- **WHEN** scanning for subdirectories named `openspec`
- **THEN** none SHALL exist at any depth within `openspec/`
