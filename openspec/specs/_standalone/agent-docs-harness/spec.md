## Purpose

This specification defines requirements for Agent Docs Harness.

## Requirements

### Requirement: Harness integration documentation

The system SHALL provide documentation for all pydantic-ai-harness capabilities wired via `agent_core.sdk.build_agent(..., capabilities=[...])`.

#### Scenario: Harness guide exists
- **WHEN** a developer opens `agent-core/docs/harness-integration.md`
- **THEN** it SHALL document all capabilities with module paths and class references

#### Scenario: Each capability documented
- **WHEN** a developer reads `harness-integration.md`
- **THEN** it SHALL have entries for: TieredCompaction, SpendLimits, Advisor, SystemReminders, ConversationSearch, guardrails, planning, subagents, step_persistence, repo_context, tool_output_limits, cache_monitoring, limit_warnings, docs_access, dynamic_workflow, filesystem, shell

### Requirement: Context compaction documentation

`harness-integration.md` SHALL document compaction strategies and their config fields.

#### Scenario: Compaction strategies
- **WHEN** a developer reads the compaction section
- **THEN** it SHALL show `strategy: "summarizing"` (default) and `strategy: "sliding_window"` with `max_messages` and `max_tokens` fields

#### Scenario: Compaction sub-options
- **WHEN** a developer reads the compaction section
- **THEN** it SHALL document `clamp_oversized`, `clear_tool_results`, and `deduplicate_reads` boolean flags

### Requirement: Guardrails documentation

`harness-integration.md` SHALL document InputGuardrail with configurable guard functions.

#### Scenario: Default guard
- **WHEN** a developer reads the guardrails section
- **THEN** it SHALL explain that `{}` creates an allow-all guard

#### Scenario: Custom guard
- **WHEN** a developer reads the guardrails section
- **THEN** it SHALL show how to pass a custom guard function via `guardrails["guard"]`

### Requirement: Step persistence documentation

`harness-integration.md` SHALL document StepPersistence with store options.

#### Scenario: In-memory store
- **WHEN** a developer reads the persistence section
- **THEN** it SHALL show `{}` config uses `InMemoryStepStore`

#### Scenario: File store
- **WHEN** a developer reads the persistence section
- **THEN** it SHALL show `store_path: "/path/to/store"` uses `FileStepStore`

### Requirement: Other capabilities documentation

`harness-integration.md` SHALL document TieredCompaction, SpendLimits, Advisor, SystemReminders, ConversationSearch, subagents, planning, repo_context, tool_output_limits, cache_monitoring, limit_warnings, docs_access, dynamic_workflow, filesystem, and shell.

#### Scenario: Each capability has example
- **WHEN** a developer reads each capability section
- **THEN** it SHALL show the public module path, representative classes, and usage pattern

### Requirement: Configuration docs harness section

`configuration.md` SHALL include a section summarizing available harness capabilities.

#### Scenario: Summary table
- **WHEN** a developer reads `configuration.md`
- **THEN** it SHALL have a table listing harness capabilities with one-line descriptions and link to `harness-integration.md`
