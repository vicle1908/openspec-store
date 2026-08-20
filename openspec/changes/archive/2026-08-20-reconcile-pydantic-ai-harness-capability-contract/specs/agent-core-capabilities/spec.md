## MODIFIED Requirements

### Requirement: TieredCompaction in AgentRuntime

AgentRuntime SHALL compose TieredCompaction through the public typed capability boundary. The runtime SHALL preserve a supplied target and ordered strategies and SHALL NOT inject a default compaction capability. Any retained internal convenience keyword SHALL remain compatibility-only, undocumented, and unreachable through `BaseAgent` or `build_agent`.

#### Scenario: Default compaction

- **WHEN** AgentRuntime is constructed without a compaction capability
- **THEN** TieredCompaction SHALL NOT be in the capability stack
- **AND** the runtime SHALL not trim or summarize context because of an undocumented default

#### Scenario: Custom target

- **WHEN** a caller supplies TieredCompaction with target_tokens=50,000
- **THEN** TieredCompaction SHALL use 50,000 as the target token count
- **AND** the runtime SHALL preserve the supplied strategy order
- **AND** public-boundary behavior tests SHALL prove the below-target and exceeded-target paths

### Requirement: SpendLimits in AgentRuntime

AgentRuntime SHALL compose SpendLimits through the public typed capability boundary. Any USD budgets SHALL use caller-owned pricing or fail closed for unpriced models; the runtime SHALL NOT inject hidden default caps. Any retained internal convenience keyword SHALL remain compatibility-only, undocumented, and unreachable through `BaseAgent` or `build_agent`.

#### Scenario: Default budgets

- **WHEN** AgentRuntime is constructed without a spend capability
- **THEN** SpendLimits SHALL NOT be in the capability stack
- **AND** no undocumented USD budget SHALL be enforced

#### Scenario: Custom budgets

- **WHEN** a caller supplies SpendLimits with per-run $10.00 and per-day $100.00 budgets
- **THEN** SpendLimits SHALL enforce those caps using a deterministic or approved pricing function
- **AND** unpriced acceptance models SHALL raise or be explicitly priced

#### Scenario: Disabled budgets

- **WHEN** the caller does not supply SpendLimits
- **THEN** SpendLimits SHALL NOT be added implicitly

### Requirement: Planning in AgentRuntime

AgentRuntime SHALL optionally compose Planning with caller-selected subtask and store settings through public typed capability composition. Any retained internal enablement keyword SHALL remain compatibility-only, undocumented, and unreachable through `BaseAgent` or `build_agent`.

#### Scenario: Planning enabled

- **WHEN** a caller supplies Planning(enable_subtasks=True)
- **THEN** Planning SHALL be present with subtask support
- **AND** a public agent run SHALL be able to create and update a disposable plan

#### Scenario: Planning disabled (default)

- **WHEN** a caller omits Planning
- **THEN** Planning SHALL NOT be in the capability stack

### Requirement: Advisor in AgentRuntime

AgentRuntime SHALL optionally compose Advisor only when the caller supplies an explicit advisor capability through typed composition. Advisor construction SHALL not reopen global provider precedence. Any retained internal advisor keyword SHALL remain compatibility-only, undocumented, and unreachable through `BaseAgent` or `build_agent`.

#### Scenario: Advisor enabled

- **WHEN** a caller supplies Advisor(model=<model>, max_uses=3)
- **THEN** Advisor SHALL be present with the supplied model and usage limit
- **AND** a deterministic public run SHALL prove consultation or a documented local fallback

#### Scenario: Advisor disabled (default)

- **WHEN** a caller omits Advisor
- **THEN** Advisor SHALL NOT be in the capability stack

### Requirement: SystemReminders in AgentRuntime

AgentRuntime SHALL compose SystemReminders only when the caller supplies a typed reminder capability. The runtime SHALL NOT add GoalReanchor implicitly; any retained internal compatibility path SHALL remain undocumented and unreachable through `BaseAgent` or `build_agent`.

#### Scenario: SystemReminders always active

- **WHEN** AgentRuntime is constructed without SystemReminders
- **THEN** SystemReminders SHALL NOT be in the capability stack

#### Scenario: Reminders enabled

- **WHEN** a caller supplies SystemReminders(dynamic_reminders=[GoalReanchor()])
- **THEN** the reminder SHALL be inserted at the supported request boundary
- **AND** a multi-request test SHALL prove the goal is re-anchored without duplicate implicit reminders

### Requirement: ConversationSearch factory

`agent_core.sdk.memory` SHALL provide a ConversationSearch composition helper only when it receives a caller-owned snapshot store. The helper SHALL not allocate a disconnected default store and SHALL construct conversation-scoped search by default. An all-store search SHALL require direct explicit upstream composition under a caller-owned single-tenant policy rather than an agent-core helper default.

#### Scenario: Default factory

- **WHEN** `create_conversation_search(store=<caller-owned-store>)` is called
- **THEN** it SHALL return a ConversationSearch backed by SnapshotHistorySource over that exact store
- **AND** the capability SHALL use `scope="conversation"`
- **AND** snapshots written by StepPersistence SHALL be searchable

#### Scenario: Store omitted or unavailable

- **WHEN** shared history is requested without an available caller-owned store
- **THEN** construction SHALL fail before model or tool execution
- **AND** the helper SHALL not substitute a fresh InMemoryStepStore

#### Scenario: Conversation identity is unavailable

- **WHEN** conversation-scoped search runs without a stable conversation identity
- **THEN** the search SHALL return no cross-conversation corpus
- **AND** it SHALL not fall back to `scope="all"`

## ADDED Requirements

### Requirement: One harness capability configuration boundary

The workspace SHALL expose one public harness-capability configuration boundary: typed objects supplied through `BaseAgent` or `build_agent`. Internal compatibility keywords MAY remain temporarily for migration or focused tests, but they SHALL not be projected from `AgentConfig`, AgentSpec compatibility metadata, or public consumer constructors.

#### Scenario: Public typed boundary

- **WHEN** a consumer supplies a typed harness capability through `BaseAgent` or `build_agent`
- **THEN** the capability SHALL be passed through with its identity and configuration preserved
- **AND** no parallel dictionary or convenience-key projection SHALL be required

#### Scenario: Compatibility-only internal keyword

- **WHEN** an internal test or migration shim uses a retained AgentRuntime convenience keyword
- **THEN** the keyword SHALL remain outside public consumer construction and documentation
- **AND** public capability acceptance SHALL not rely on that keyword
