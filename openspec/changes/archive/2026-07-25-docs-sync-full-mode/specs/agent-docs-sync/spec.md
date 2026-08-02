## MODIFIED Requirements

### Requirement: CLI commands

#### Scenario: Full sync command
- **WHEN** `docs-sync sync --full` is run from a repo root
- **THEN** it SHALL run the full pipeline via SchedulerEngine: discover → audit → generate → validate → report
- **AND** it SHALL scan ALL source files (not just git diff)
- **AND** it SHALL classify all source files into Diátaxis quadrants
- **AND** it SHALL audit all existing docs for gaps (missing docs, broken links, Diátaxis violations)
- **AND** it SHALL generate/update docs for identified gaps using GenerationAgent with harness capabilities
- **AND** it SHALL validate all docs (links + Diátaxis rules)
- **AND** it SHALL output a comprehensive report with statistics
- **AND** it SHALL support `--durable` flag for crash-recoverable execution

#### Scenario: Audit command
- **WHEN** `docs-sync audit` is run from a repo root
- **THEN** it SHALL scan ALL source files and classify them
- **AND** it SHALL check ALL docs for broken links and Diátaxis violations
- **AND** it SHALL report gaps without making any changes
- **AND** it SHALL output results in JSON or human-readable format
- **AND** it SHALL NOT invoke the LLM agent (read-only)

#### Scenario: Full sync all repos
- **WHEN** `docs-sync sync-all --full` is run
- **THEN** it SHALL run the full pipeline on each TDT repo via SchedulerEngine
- **AND** it SHALL aggregate results into a cross-repo summary report
- **AND** it SHALL report per-repo and overall documentation health

### Requirement: Gap detection

The system SHALL identify documentation gaps across the entire codebase.

#### Scenario: Source file without docs
- **WHEN** a source file exists but has no matching doc in auto_mapping
- **THEN** it SHALL be reported as a gap with file path and suggested quadrant

#### Scenario: Broken links in docs
- **WHEN** a doc file contains links to non-existent files or anchors
- **THEN** they SHALL be reported with file path, link target, and reason

#### Scenario: Diátaxis violations
- **WHEN** a doc file violates its assigned Diátaxis quadrant rules
- **THEN** it SHALL be reported with file path, violation type, and severity

### Requirement: Comprehensive reporting

The system SHALL produce detailed reports for full mode operations.

#### Scenario: Full mode report
- **WHEN** a full sync or audit completes
- **THEN** the report SHALL include: source files scanned, docs found, gaps identified, links checked, violations found, docs generated/updated
- **AND** it SHALL support JSON output format

### Requirement: Durable execution

The full pipeline SHALL support durable execution via agent-core's SchedulerEngine.

#### Scenario: Durable full sync
- **WHEN** `docs-sync sync --full --durable` is run
- **THEN** each pipeline step SHALL be executed as a SchedulerEngine step
- **AND** steps SHALL have configurable retry counts
- **AND** step results SHALL be persisted for crash recovery
- **AND** the pipeline SHALL resume from last successful step on restart

#### Scenario: Step-level observability
- **WHEN** a full pipeline step completes or fails
- **THEN** the result SHALL be logged with structured logging
- **AND** step duration and status SHALL be tracked

### Requirement: WorkflowBuilder integration

The full pipeline SHALL use agent-core's WorkflowBuilder for DAG-based orchestration.

#### Scenario: DAG construction
- **WHEN** the full pipeline is built
- **THEN** it SHALL use WorkflowBuilder with NodeDescriptor and EdgeDescriptor
- **AND** it SHALL define nodes for each phase: discover, audit, generate, validate, report
- **AND** it SHALL define edges for the sequential flow between phases
- **AND** it SHALL support conditional routing via CommandResult

#### Scenario: WorkflowEngine execution
- **WHEN** the full pipeline is executed
- **THEN** it SHALL compile the DAG via WorkflowEngine
- **AND** it SHALL support PostgresSaver checkpointing when durable mode is enabled
- **AND** it SHALL support subgraphs for complex nested workflows

### Requirement: Harness capabilities integration

The generation phase SHALL leverage agent-core's harness capabilities.

#### Scenario: Planning capability
- **WHEN** the generation phase runs
- **THEN** it SHALL use planning guidance from LlmConfig.planning_guidance
- **AND** it SHALL decompose complex classification tasks into structured plans
- **AND** it SHALL cache plans for repeated execution

#### Scenario: SubAgents capability
- **WHEN** the generation phase runs
- **THEN** it SHALL support delegation of validation tasks to subagents
- **AND** it SHALL inherit parent tools when enabled

#### Scenario: Guardrails capability
- **WHEN** the generation phase runs
- **THEN** it SHALL use InputGuard to block write-intent prompts on read-only agents
- **AND** it SHALL validate write paths against allowed directories

### Requirement: ApprovalGate integration

All write operations SHALL go through agent-core's ApprovalGate.

#### Scenario: User confirmation
- **WHEN** the generation phase writes a doc file
- **THEN** it SHALL trigger ApprovalGate for user confirmation
- **AND** the write SHALL NOT proceed until approved

#### Scenario: Audit trail
- **WHEN** a doc file is written
- **THEN** the write SHALL be logged via HookRegistry (audit_doc_writes hook)
- **AND** the write path SHALL be validated via validate_write_path hook
