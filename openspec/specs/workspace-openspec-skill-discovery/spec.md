# workspace-openspec-skill-discovery Specification

## Purpose
Defines workspace-level discovery of OpenSpec Codex skills without weakening
the managed skill-mirror contract of an individual repository.
## Requirements
### Requirement: OpenSpec Codex skills SHALL be discoverable at workspace scope

The workspace Codex skill surface SHALL contain the same 12 OpenSpec skills as
the canonical managed source in `go-microservices/.agents/skills`.

#### Scenario: A Python repo can read workspace OpenSpec skills

- **GIVEN** a Python repo has no project-local OpenSpec Codex skills
- **WHEN** Codex resolves skills from the workspace surface
- **THEN** all 12 `openspec-*` skills SHALL be readable from
  `~/Developer/.codex/skills`

### Requirement: Project-managed skill mirrors MUST be preserved

Adding workspace skill copies MUST NOT remove or alter the tracked
`go-microservices/.agents/skills` and `.codex/skills` mirror pairs.

#### Scenario: Repository parity validation runs after workspace installation

- **GIVEN** the workspace copies have been installed
- **WHEN** the Go repository's documentation-currency validation checks its
  declared mirror pairs
- **THEN** every declared pair SHALL remain present and byte-for-byte identical

