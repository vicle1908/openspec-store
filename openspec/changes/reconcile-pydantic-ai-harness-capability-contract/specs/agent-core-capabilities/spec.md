## MODIFIED Requirements

### Requirement: TieredCompaction in AgentRuntime

AgentRuntime SHALL compose TieredCompaction only when the caller supplies a typed compaction capability through the public composition boundary. The runtime SHALL preserve the supplied target and ordered strategies and SHALL NOT inject a default compaction capability.

#### Scenario: Default compaction

- **WHEN** AgentRuntime is constructed without a compaction capability
- **THEN** TieredCompaction SHALL NOT be in the capability stack
- **AND** the runtime SHALL not trim or summarize context because of an undocumented default

#### Scenario: Custom target

- **WHEN** a caller supplies TieredCompaction with target_tokens=120,000
- **THEN** TieredCompaction SHALL use 120,000 as the target token count
- **AND** the runtime SHALL preserve the supplied strategy order

#### Scenario: Custom target supplied explicitly

- **WHEN** a caller supplies TieredCompaction with target_tokens=50,000
- **THEN** TieredCompaction SHALL use 50,000 as the target token count
- **AND** public-boundary behavior tests SHALL prove the below-target and exceeded-target paths

### Requirement: SpendLimits in AgentRuntime

AgentRuntime SHALL compose SpendLimits only when the caller supplies a typed spend capability through the public composition boundary. Any USD budgets SHALL use caller-owned pricing or fail closed for unpriced models; the runtime SHALL NOT inject hidden default caps.

#### Scenario: Default budgets

- **WHEN** AgentRuntime is constructed without a spend capability
- **THEN** SpendLimits SHALL NOT be in the capability stack
- **AND** no undocumented USD budget SHALL be enforced

#### Scenario: Custom budgets

- **WHEN** a caller supplies SpendLimits with per-run $5.00 and per-day $100.00 budgets
- **THEN** SpendLimits SHALL enforce those caps using a deterministic or approved pricing function
- **AND** unpriced acceptance models SHALL raise or be explicitly priced

#### Scenario: Custom budget supplied explicitly

- **WHEN** a caller supplies a per-run budget of $10.00
- **THEN** SpendLimits SHALL enforce the $10.00 cap

#### Scenario: Disabled budgets

- **WHEN** the caller does not supply SpendLimits
- **THEN** SpendLimits SHALL NOT be added implicitly

### Requirement: Planning in AgentRuntime

AgentRuntime SHALL optionally compose Planning with caller-selected subtask and store settings through public typed capability composition.

#### Scenario: Planning enabled

- **WHEN** a caller supplies Planning(enable_subtasks=True)
- **THEN** Planning SHALL be present with subtask support
- **AND** a public agent run SHALL be able to create and update a disposable plan

#### Scenario: Planning disabled (default)

- **WHEN** a caller omits Planning
- **THEN** Planning SHALL NOT be in the capability stack

### Requirement: Advisor in AgentRuntime

AgentRuntime SHALL optionally compose Advisor only when the caller supplies an explicit advisor model through typed capability composition. Advisor construction SHALL not reopen global provider precedence.

#### Scenario: Advisor enabled

- **WHEN** a caller supplies Advisor(model=<model>, max_uses=3)
- **THEN** Advisor SHALL be present with the supplied model and usage limit
- **AND** a deterministic public run SHALL prove consultation or a documented local fallback

#### Scenario: Advisor disabled (default)

- **WHEN** a caller omits Advisor
- **THEN** Advisor SHALL NOT be in the capability stack

### Requirement: SystemReminders in AgentRuntime

AgentRuntime SHALL compose SystemReminders only when the caller supplies a typed reminder capability. The runtime SHALL NOT add GoalReanchor implicitly.

#### Scenario: SystemReminders always active

- **WHEN** AgentRuntime is constructed without SystemReminders
- **THEN** SystemReminders SHALL NOT be in the capability stack

#### Scenario: Reminders enabled

- **WHEN** a caller supplies SystemReminders(dynamic_reminders=[GoalReanchor()])
- **THEN** the reminder SHALL be inserted at the supported request boundary
- **AND** a multi-request test SHALL prove the goal is re-anchored without duplicate implicit reminders

### Requirement: ConversationSearch factory

`agent_core.sdk.memory` SHALL provide a ConversationSearch composition helper only when it receives a caller-owned snapshot store. The helper SHALL not allocate a disconnected default store.

#### Scenario: Default factory

- **WHEN** `create_conversation_search(store=<caller-owned-store>)` is called
- **THEN** it SHALL return a ConversationSearch backed by SnapshotHistorySource over that exact store
- **AND** snapshots written by StepPersistence SHALL be searchable

#### Scenario: Store omitted or unavailable

- **WHEN** shared history is requested without an available caller-owned store
- **THEN** construction SHALL fail before model or tool execution
- **AND** the helper SHALL not substitute a fresh InMemoryStepStore
