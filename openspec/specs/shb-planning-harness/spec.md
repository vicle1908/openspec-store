# shb-planning-harness Specification

## Purpose
Provides a multi-stage autonomous planning harness, schema-backed validation, and durable ticket execution workflows for the Saigon - Hanoi Bank (SHB) agent ecosystem.

## Requirements

### Requirement: Multi-Stage Ticket Planning Workflow
The `shb-agent-harness` system SHALL execute structured multi-stage planning pipelines across ticket analysis, technical design, verification planning, and approval gating using durable LangGraph state graphs.

#### Scenario: Ticket analysis and design execution
- **WHEN** an engineering ticket instruction is submitted to the harness
- **THEN** the harness executes the planning stages sequentially, persisting checkpoint artifacts at each stage boundary

### Requirement: Schema-Backed Claim and Evidence Verification
The system SHALL validate stage deliverables against versioned JSON schemas provided by `shb-ai-harness-skills`, asserting evidence completeness before advancing stage transitions.

#### Scenario: Missing evidence rejection
- **WHEN** a stage execution produces a deliverable missing required verification evidence
- **THEN** the harness validation engine SHALL flag the missing claim and prevent stage advancement

### Requirement: Command-Line Interface Entrypoint
The package SHALL provide an executable command-line interface named `shb-harness` allowing engineers to start, resume, and inspect planning workflows.

#### Scenario: Workflow status check
- **WHEN** an engineer executes `shb-harness status --ticket-id <id>`
- **THEN** the CLI outputs the current active stage, completed checkpoints, and artifact locations
