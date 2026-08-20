## MODIFIED Requirements

### Requirement: TieredCompaction in AgentRuntime

AgentRuntime SHALL compose a default `TieredCompaction` capability with a
120,000-token target when the caller omits compaction. A caller-supplied typed
compaction capability SHALL override that default while preserving its target
and ordered strategies. Any retained internal convenience keyword SHALL
remain compatibility-only, undocumented, and unreachable through `BaseAgent`
or `build_agent`.

#### Scenario: Default compaction

- **WHEN** AgentRuntime is constructed without a compaction capability
- **THEN** TieredCompaction SHALL be present with the documented 120,000-token target
- **AND** the runtime SHALL apply the default through the public typed capability boundary

#### Scenario: Explicit compaction override

- **WHEN** a caller supplies TieredCompaction with target_tokens=50,000 and ordered strategies
- **THEN** TieredCompaction SHALL use 50,000 as the target token count
- **AND** the runtime SHALL preserve the supplied strategy order
- **AND** public-boundary behavior tests SHALL prove the below-target and exceeded-target paths

#### Scenario: Custom target

- **WHEN** a caller supplies TieredCompaction with target_tokens=50,000
- **THEN** TieredCompaction SHALL use 50,000 as the target token count
- **AND** the runtime SHALL preserve the supplied strategy order
- **AND** public-boundary behavior tests SHALL prove the below-target and exceeded-target paths

#### Scenario: Explicit compaction disablement is not implicit

- **WHEN** a caller supplies an explicit supported disablement for compaction
- **THEN** the runtime SHALL honor that disablement
- **AND** it SHALL not silently replace the caller's choice with a second capability

### Requirement: SpendLimits in AgentRuntime

AgentRuntime SHALL compose a default SpendLimits capability with a $5 per-run
and $100 per-day budget when the caller omits spend limits. A caller-supplied
typed SpendLimits capability SHALL override those defaults. Explicit `None`
values for the spend defaults SHALL disable the corresponding default budget.
Any USD budgets SHALL use caller-owned pricing or fail closed for unpriced
models. Any retained internal convenience keyword SHALL remain
compatibility-only, undocumented, and unreachable through `BaseAgent` or
`build_agent`.

#### Scenario: Default budgets

- **WHEN** AgentRuntime is constructed without a spend capability
- **THEN** SpendLimits SHALL be present with a $5 per-run and $100 per-day budget
- **AND** budget evaluation SHALL use an approved or caller-owned pricing function

#### Scenario: Custom budgets

- **WHEN** a caller supplies SpendLimits with per-run $10.00 and per-day $100.00 budgets
- **THEN** SpendLimits SHALL enforce those caller-selected caps
- **AND** unpriced acceptance models SHALL raise or be explicitly priced

#### Scenario: Disabled budgets

- **WHEN** the caller supplies `None` for a spend default
- **THEN** the corresponding default budget SHALL not be installed
- **AND** the runtime SHALL not substitute the documented default for that value

### Requirement: Planning in AgentRuntime

AgentRuntime SHALL optionally compose Planning with caller-selected subtask and
store settings through public typed capability composition. Planning SHALL be
absent by default. Any retained internal enablement keyword SHALL remain
compatibility-only, undocumented, and unreachable through `BaseAgent` or
`build_agent`.

#### Scenario: Planning enabled

- **WHEN** a caller supplies Planning(enable_subtasks=True)
- **THEN** Planning SHALL be present with subtask support
- **AND** a public agent run SHALL be able to create and update a disposable plan

#### Scenario: Planning disabled (default)

- **WHEN** a caller omits Planning
- **THEN** Planning SHALL not be in the capability stack

### Requirement: Advisor in AgentRuntime

AgentRuntime SHALL compose Advisor only when the caller supplies an explicit
advisor capability with a usable model. Advisor construction SHALL not reopen
global provider precedence. Advisor SHALL be disabled when the capability is
absent, its model is absent, or the caller explicitly supplies `None`. Any
retained internal advisor keyword SHALL remain compatibility-only,
undocumented, and unreachable through `BaseAgent` or `build_agent`.

#### Scenario: Advisor enabled

- **WHEN** a caller supplies Advisor(model=<model>, max_uses=3)
- **THEN** Advisor SHALL be present with the supplied model and usage limit
- **AND** a deterministic public run SHALL prove consultation or a documented local fallback

#### Scenario: Advisor disabled by omission or None

- **WHEN** a caller omits Advisor, supplies an absent model, or supplies `None`
- **THEN** Advisor SHALL not be in the capability stack
- **AND** no provider precedence resolution SHALL be reopened to fabricate one

#### Scenario: Advisor disabled (default)

- **WHEN** a caller omits Advisor
- **THEN** Advisor SHALL not be in the capability stack

### Requirement: SystemReminders in AgentRuntime

AgentRuntime SHALL compose a default SystemReminders capability containing
GoalReanchor when the caller omits reminders. A caller-supplied typed reminder
capability SHALL replace that default at the supported request boundary. Any
retained internal compatibility path SHALL remain undocumented and unreachable
through `BaseAgent` or `build_agent`.

#### Scenario: System reminders default

- **WHEN** AgentRuntime is constructed without SystemReminders
- **THEN** SystemReminders SHALL be present with the documented GoalReanchor behavior
- **AND** the runtime SHALL not insert duplicate implicit reminders across requests

#### Scenario: SystemReminders always active

- **WHEN** AgentRuntime is constructed without SystemReminders
- **THEN** SystemReminders SHALL be present with GoalReanchor as the documented default

#### Scenario: Reminders enabled or overridden

- **WHEN** a caller supplies SystemReminders(dynamic_reminders=[GoalReanchor()]) or another typed reminder capability
- **THEN** the supplied reminder configuration SHALL be preserved at the supported request boundary
- **AND** a multi-request test SHALL prove the goal is re-anchored without duplicate implicit reminders

#### Scenario: Reminders enabled

- **WHEN** a caller supplies SystemReminders(dynamic_reminders=[GoalReanchor()])
- **THEN** the reminder SHALL be preserved at the supported request boundary
- **AND** a multi-request test SHALL prove the goal is re-anchored without duplicate implicit reminders
