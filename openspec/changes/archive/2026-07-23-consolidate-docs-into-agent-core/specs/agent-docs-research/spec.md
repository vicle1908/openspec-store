## ADDED Requirements

### Requirement: Research documentation directory

The system SHALL maintain research and analysis documentation in `agent-core/docs/research/`.

#### Scenario: Directory exists with all research files
- **WHEN** a developer navigates to `agent-core/docs/research/`
- **THEN** the directory SHALL contain framework-comparison, pydanticai-langgraph, feature-mapping, architecture-analysis, best-practices, upgrade-opportunities, and validation-report files

### Requirement: All agent-core docs consolidated

All agent-core-specific documentation SHALL reside in `agent-core/docs/`. No agent-core docs SHALL exist in `tdt-meta/docs/agent-core/`.

#### Scenario: Single source of truth
- **WHEN** a developer looks for agent-core documentation
- **THEN** all docs SHALL be in `agent-core/docs/` with no duplicates in other locations

### Requirement: README entry point

`agent-core/docs/README.md` SHALL provide a brief overview of agent-core and link to all documentation files.

#### Scenario: README contains overview
- **WHEN** a developer opens `agent-core/docs/README.md`
- **THEN** it SHALL contain a one-paragraph description of agent-core and links to all docs including the research/ subdirectory
