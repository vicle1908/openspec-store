# Spec Delta: omniroute-agent-skills

## MODIFIED Requirements

### Requirement: Ecosystem Knowledge Hub and Documentation Synchronization
The repository workspace SHALL maintain an operational reference guide in `docs/omniroute-agent-skills.md` and keep `wiki/entities/omniroute.md` synchronized with the active skills catalog, management authorization model, curl REST invocation patterns, and `omniroute` CLI bridge subcommand recipes.

#### Scenario: Operational guide provides actionable agent recipes
- **WHEN** an agent consults `docs/omniroute-agent-skills.md`
- **THEN** the document details all 23 `omni-*` REST endpoints, expected authentication headers, and copy-paste curl commands
- **AND** the document includes a complete CLI command reference covering the 21 `cli-*` skills executed via `~/.local/bin/omniroute`

#### Scenario: Wiki entity reflects active host CLI bridge governance
- **WHEN** `wiki/entities/omniroute.md` is inspected
- **THEN** it SHALL describe the 21 `cli-*` skills as actively served through `~/.local/bin/omniroute` (`2026-10-15-introduce-omniroute-cli-bridge`) rather than deferred to a future change
