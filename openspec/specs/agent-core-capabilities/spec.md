# agent-core-capabilities Specification

## Purpose
TBD - created by archiving change upgrade-harness-23. Update Purpose after archive.

## Requirements

### Requirement: TieredCompaction in AgentRuntime

AgentRuntime SHALL compose TieredCompaction with three tiers: DeduplicateFileReads, ClearToolResults, and SummarizingCompaction. The target_tokens parameter SHALL default to 120,000.

#### Scenario: Default compaction
- **WHEN** AgentRuntime is constructed without target_tokens
- **THEN** TieredCompaction SHALL use 120,000 as the target token count

#### Scenario: Custom target
- **WHEN** AgentRuntime is constructed with target_tokens=50,000
- **THEN** TieredCompaction SHALL use 50,000 as the target token count

### Requirement: SpendLimits in AgentRuntime

AgentRuntime SHALL compose SpendLimits with Budget instances for per-run and per-day USD caps. Default per-run cap is $5.00; default per-day cap is $100.00.

#### Scenario: Default budgets
- **WHEN** AgentRuntime is constructed with default spend limits
- **THEN** SpendLimits SHALL enforce $5.00 per-run and $100.00 per-day caps

#### Scenario: Custom budgets
- **WHEN** AgentRuntime is constructed with spend_limit_per_run_usd=10.0
- **THEN** SpendLimits SHALL enforce $10.00 per-run cap

#### Scenario: Disabled budgets
- **WHEN** AgentRuntime is constructed with spend_limit_per_run_usd=None
- **THEN** SpendLimits SHALL NOT be added to the capability stack

### Requirement: Planning in AgentRuntime

AgentRuntime SHALL optionally compose Planning with subtask support.

#### Scenario: Planning enabled
- **WHEN** AgentRuntime is constructed with enable_planning=True
- **THEN** Planning(enable_subtasks=True) SHALL be appended to capabilities

#### Scenario: Planning disabled (default)
- **WHEN** AgentRuntime is constructed without enable_planning
- **THEN** Planning SHALL NOT be in the capability stack

### Requirement: Advisor in AgentRuntime

AgentRuntime SHALL optionally compose Advisor with a cheaper model for decision review.

#### Scenario: Advisor enabled
- **WHEN** AgentRuntime is constructed with advisor_model=<model>
- **THEN** Advisor(model=<model>, max_uses=3) SHALL be appended to capabilities

#### Scenario: Advisor disabled (default)
- **WHEN** AgentRuntime is constructed without advisor_model
- **THEN** Advisor SHALL NOT be in the capability stack

### Requirement: SystemReminders in AgentRuntime

AgentRuntime SHALL always compose SystemReminders with GoalReanchor as a dynamic reminder.

#### Scenario: SystemReminders always active
- **WHEN** AgentRuntime is constructed
- **THEN** SystemReminders(dynamic_reminders=[GoalReanchor()]) SHALL be in the capability stack

### Requirement: ConversationSearch factory

agent_core.sdk.memory SHALL provide create_conversation_search() factory that returns a ConversationSearch capability backed by SnapshotHistorySource.

#### Scenario: Default factory
- **WHEN** create_conversation_search() is called
- **THEN** it SHALL return a ConversationSearch with InMemoryStepStore and default parameters
