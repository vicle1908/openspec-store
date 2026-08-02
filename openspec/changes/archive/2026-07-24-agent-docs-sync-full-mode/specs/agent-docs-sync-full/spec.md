## ADDED Requirements

### Requirement: Full Mode

The system SHALL provide full mode for comprehensive documentation synchronization.

#### Scenario: --full flag
- **WHEN** `docs-sync sync --full` is run
- **THEN** the system SHALL read all source code, deployment configs, skills
- **AND** it SHALL generate comprehensive documentation
- **AND** it SHALL use context compaction for large codebases

#### Scenario: Context compaction
- **WHEN** full mode runs
- **THEN** the system SHALL use SummarizingCompaction
- **AND** it SHALL use ClampOversizedMessages
- **AND** it SHALL use DeduplicateFileReads
- **AND** it SHALL stay within context limits

#### Scenario: Full mode workflow
- **WHEN** full mode runs
- **THEN** it SHALL execute: discovery → analysis → generation → validation
- **AND** it SHALL read pyproject.toml, skills, deployment configs
- **AND** it SHALL generate/update ALL documentation

### Requirement: Full Mode Tools

The system SHALL provide tools for reading project configuration.

#### Scenario: Read pyproject
- **WHEN** agent needs project metadata
- **THEN** it SHALL use ReadPyprojectTool
- **AND** it SHALL extract dependencies, config, scripts

#### Scenario: Read skill
- **WHEN** agent needs skill definitions
- **THEN** it SHALL use ReadSkillTool
- **AND** it SHALL read .agents/skills/**/*.md

#### Scenario: Read deployment
- **WHEN** agent needs deployment info
- **THEN** it SHALL use ReadDeploymentTool
- **AND** it SHALL read Dockerfile, docker-compose.yaml

### Requirement: Full Mode Output

The system SHALL generate comprehensive documentation.

#### Scenario: README update
- **WHEN** full mode runs
- **THEN** it SHALL update README.md with project overview
- **AND** it SHALL include installation, usage, configuration

#### Scenario: API docs update
- **WHEN** full mode runs
- **THEN** it SHALL update docs/api/*.md with API reference
- **AND** it SHALL include all public functions and classes

#### Scenario: Deployment docs
- **WHEN** full mode runs
- **THEN** it SHALL generate docs/deployment.md
- **AND** it SHALL include Dockerfile and docker-compose instructions
