# agent-docs-sync Delta Specification

## MODIFIED Requirements

### Requirement: CLI JSON output mode

The CLI SHALL emit one valid JSON document on stdout when the global
`--json` flag is supplied before a command.

#### Scenario: Global JSON flag

- **WHEN** `docs-sync --json check --repo <repo>` is invoked
- **THEN** the command SHALL exit according to the command result
- **AND** stdout SHALL contain one valid JSON document
- **AND** stdout SHALL NOT contain the human-readable report header

#### Scenario: Per-command JSON option

- **WHEN** `docs-sync check --repo <repo> --output json` is invoked
- **THEN** behavior SHALL remain valid JSON output

#### Scenario: Default text output

- **WHEN** no JSON option is supplied
- **THEN** the command SHALL preserve the existing human-readable output
