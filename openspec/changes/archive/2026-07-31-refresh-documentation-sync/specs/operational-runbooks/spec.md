## Purpose

Ensure all runbooks are indexed and discoverable.

## ADDED Requirements

### Requirement: Runbook index is complete

`docs/runbooks/README.md` SHALL index all existing runbooks.

#### Scenario: All runbooks indexed
- **WHEN** a developer reads `docs/runbooks/README.md`
- **THEN** they find entries for all 11 runbooks in `docs/runbooks/`

#### Scenario: New runbooks discoverable
- **WHEN** a developer searches for "security" or "temporal" or "knowledge" in `docs/runbooks/README.md`
- **THEN** they find the corresponding runbook entries
