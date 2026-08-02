## Purpose

This specification defines requirements for Agent Docs Harness.

## Requirements

### Requirement: Harness integration documentation

The system SHALL provide documentation for all 10 pydantic-ai-harness capabilities wired via `harness_config`.

#### Scenario: Harness guide exists
- **WHEN** a developer opens `agent-core/docs/harness-integration.md`
- **THEN** it SHALL document all 10 capabilities with config examples

#### Scenario: Each capability documented
- **WHEN** a developer reads `harness-integration.md`
- **THEN** it SHALL have sections for: context_compaction, guardrails, step_persistence, subagents, planning, repo_context, output_overflow, cache_monitoring, limit_warnings, docs_access

### Requirement: Context compaction documentation

`harness-integration.md` SHALL document compaction strategies and their config fields.

#### Scenario: Compaction strategies
- **WHEN** a developer reads the compaction section
- **THEN** it SHALL show `strategy: "summarizing"` (default) and `strategy: "sliding_window"` with `max_messages` and `max_tokens` fields

#### Scenario: Compaction sub-options
- **WHEN** a developer reads the compaction section
- **THEN** it SHALL document `clamp_oversized`, `clear_tool_results`, and `deduplicate_reads` boolean flags

### Requirement: Guardrails documentation

`harness-integration.md` SHALL document InputGuard with configurable guard functions.

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

`harness-integration.md` SHALL document subagents, planning, repo_context, output_overflow, cache_monitoring, limit_warnings, and docs_access.

#### Scenario: Each capability has example
- **WHEN** a developer reads each capability section
- **THEN** it SHALL show the config key and a minimal example

### Requirement: Configuration docs harness section

`configuration.md` SHALL include a `harness_config` section summarizing available capabilities.

#### Scenario: Summary table
- **WHEN** a developer reads `configuration.md`
- **THEN** it SHALL have a table listing all 10 harness capabilities with one-line descriptions and link to `harness-integration.md`
