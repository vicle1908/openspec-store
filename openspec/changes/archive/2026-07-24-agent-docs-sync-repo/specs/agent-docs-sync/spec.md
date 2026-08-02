## ADDED Requirements

### Requirement: CLI commands

The system SHALL provide CLI commands for doc sync operations via Typer.

#### Scenario: Check command
- **WHEN** `docs-sync check` is run from a repo root
- **THEN** it SHALL analyze `git diff --name-only HEAD~1` to detect changed files
- **AND** it SHALL report which docs need updating based on changed source files
- **AND** it SHALL output results in JSON or human-readable format (`--output json|text`)

#### Scenario: Update command
- **WHEN** `docs-sync update` is run
- **THEN** it SHALL auto-update docs based on code changes
- **AND** it SHALL generate doc sections from docstrings and type hints
- **AND** it SHALL support `--dry-run` flag to preview changes without writing
- **AND** write operations SHALL trigger ApprovalGate for user confirmation

#### Scenario: Validate command
- **WHEN** `docs-sync validate` is run
- **THEN** it SHALL check all doc links resolve to existing files
- **AND** it SHALL verify code examples match actual API signatures
- **AND** it SHALL run `openspec validate --strict` for spec files

#### Scenario: Sync command
- **WHEN** `docs-sync sync` is run
- **THEN** it SHALL execute the full pipeline: detect → analyze → generate → validate → report
- **AND** it SHALL support `--durable` flag for crash-recoverable execution via SchedulerEngine
- **AND** it SHALL support `--repo` flag for multi-repo orchestration

### Requirement: Change detection

The system SHALL detect what changed and what docs are affected.

#### Scenario: Source file changed
- **WHEN** a `.py` file in `src/` is modified
- **THEN** the system SHALL check if the file has public API (def/class at module level)
- **AND** it SHALL map the file to affected doc files via doc-mapping.yaml

#### Scenario: Config file changed
- **WHEN** `pyproject.toml` is modified
- **THEN** the system SHALL check for dependency changes
- **AND** it SHALL update dependency documentation

#### Scenario: Spec file changed
- **WHEN** a file in `openspec/specs/` is modified
- **THEN** the system SHALL sync delta specs to main specs
- **AND** spec sync SHALL require approval via ApprovalGate

### Requirement: Doc generation

The system SHALL auto-generate doc content from code.

#### Scenario: Docstring extraction
- **WHEN** a public function has a docstring
- **THEN** the system SHALL extract the docstring for API reference sections

#### Scenario: Type hint extraction
- **WHEN** a function has type hints
- **THEN** the system SHALL extract parameter types for documentation

#### Scenario: Config example generation
- **WHEN** a harness capability is documented
- **THEN** the system SHALL generate config examples from the capability's init signature

### Requirement: Validation

The system SHALL validate doc accuracy.

#### Scenario: Link validation
- **WHEN** a doc contains `[text](path)` links
- **THEN** the system SHALL verify the target file exists for relative links
- **AND** it SHALL check external URLs return HTTP 200 via httpx

#### Scenario: Code example validation
- **WHEN** a doc contains Python code examples
- **THEN** the system SHALL verify referenced classes/functions exist in the codebase

#### Scenario: openspec validation
- **WHEN** the system runs validation
- **THEN** it SHALL run `openspec validate --strict` and report results

### Requirement: Multi-repo support

The system SHALL support syncing docs for any TDT repository.

#### Scenario: Sync agent-core docs
- **WHEN** `docs-sync sync --repo agent-core` is run
- **THEN** it SHALL sync agent-core docs using doc-mapping.yaml

#### Scenario: Sync ai-review docs
- **WHEN** `docs-sync sync --repo ai-review` is run
- **THEN** it SHALL sync ai-review docs using doc-mapping.yaml

#### Scenario: Sync all repos
- **WHEN** `docs-sync sync-all` is run
- **THEN** it SHALL sync docs for all configured TDT repositories
- **AND** it SHALL produce a consolidated report

### Requirement: agent-core integration

The system SHALL use agent-core features for intelligent doc sync.

#### Scenario: BaseAgent usage
- **WHEN** the sync agent runs
- **THEN** it SHALL use BaseAgent with custom tools and flavors

#### Scenario: ToolRegistry usage
- **WHEN** tools are registered
- **THEN** they SHALL be available via ToolRegistry with proper metadata
- **AND** write tools SHALL have `requires_approval=True`

#### Scenario: HookRegistry usage
- **WHEN** the agent runs
- **THEN** it SHALL register hooks for validation, audit, and error recovery
- **AND** hooks SHALL use tool_filter to target specific tools

#### Scenario: Flavor usage
- **WHEN** a mode is selected
- **THEN** the corresponding Flavor SHALL compose prompts, tool_policy, and defaults

#### Scenario: WorkflowBuilder usage
- **WHEN** the sync pipeline runs
- **THEN** it SHALL use WorkflowBuilder for multi-step DAG execution

#### Scenario: Durable execution
- **WHEN** sync is run with `--durable`
- **THEN** it SHALL use SchedulerEngine with @workflow/@step decorators
- **AND** steps SHALL have appropriate max_retries

### Requirement: Observability

The system SHALL provide observability for sync operations.

#### Scenario: OpenTelemetry metrics
- **WHEN** the agent runs
- **THEN** it SHALL emit metrics via otel_metrics hook
- **AND** telemetry_tags from Flavor SHALL be included

#### Scenario: Audit trail
- **WHEN** documents are written
- **THEN** it SHALL log write operations via structured_audit hook
- **AND** audit entries SHALL include timestamp, tool, path, and user

### Requirement: Configuration

The system SHALL be configurable via doc-mapping.yaml.

#### Scenario: Default mappings
- **WHEN** no doc-mapping.yaml exists
- **THEN** the system SHALL use sensible defaults for TDT repos

#### Scenario: Custom mappings
- **WHEN** doc-mapping.yaml exists
- **THEN** the system SHALL use the configured source-to-doc mappings
- **AND** it SHALL support per-repo override files

#### Scenario: Ignore patterns
- **WHEN** doc-mapping.yaml specifies ignore patterns
- **THEN** the system SHALL exclude matching files from sync

### Requirement: Error handling

The system SHALL handle errors gracefully.

#### Scenario: Git command failure
- **WHEN** a git command fails
- **THEN** the on_tool_error hook SHALL retry up to 3 times
- **AND** it SHALL return a clear error message on final failure

#### Scenario: Write permission denied
- **WHEN** validate_write_path hook blocks a write
- **THEN** the system SHALL log the violation
- **AND** it SHALL continue with remaining operations

#### Scenario: Link check timeout
- **WHEN** an external URL times out
- **THEN** the system SHALL mark it as a warning
- **AND** it SHALL not block the sync operation
