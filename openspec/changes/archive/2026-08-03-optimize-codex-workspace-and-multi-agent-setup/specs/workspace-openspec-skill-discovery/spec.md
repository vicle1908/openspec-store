## MODIFIED Requirements

### Requirement: OpenSpec Codex skills SHALL be discoverable at workspace scope

The workspace Codex skill surface SHALL contain the same 12 OpenSpec skills as
the canonical managed source in `go-microservices/.agents/skills`.

#### Scenario: A Python repo can read workspace OpenSpec skills

- **GIVEN** a Python repo has no project-local OpenSpec Codex skills
- **WHEN** Codex resolves skills from the workspace surface
- **THEN** all 12 `openspec-*` skills SHALL be readable from `~/Developer/.fable-5`

### Requirement: Project-managed skill mirrors MUST be preserved

Adding or refreshing the workspace-root discovery surface MUST NOT remove or alter the tracked `go-microservices/.agents/skills` and `.fable-5` OpenSpec mirror pairs.

#### Scenario: Repository parity validation runs after workspace installation

- **GIVEN** the workspace copies have been installed
- **WHEN** the Go repository's documentation-currency validation checks its declared mirror pairs
- **THEN** all pairs SHALL report identical digests
