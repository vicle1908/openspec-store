## ADDED Requirements

### Requirement: Run-scoped skill instructions and context

`BaseAgent.run` SHALL apply instructions from the skills resolved for that request and SHALL propagate approved `AgentRequest.context` fields into the runtime dependency context without mutating later runs.

#### Scenario: Matched skill instructions

- **WHEN** a request resolves a skill with instructions
- **THEN** those instructions SHALL be present for that run
- **AND** the skill-derived tool policy SHALL be applied

#### Scenario: Instruction isolation

- **WHEN** a second request resolves a different skill set
- **THEN** it SHALL not receive instructions from the first request

#### Scenario: Consumer policy context

- **WHEN** `AgentRequest.context` includes allowed documentation roots and other approved policy fields
- **THEN** the corresponding tool and hook callbacks SHALL receive those fields
- **AND** arbitrary context fields SHALL not override reserved runtime keys

### Requirement: Deferred approval continuation

`AgentRuntime` SHALL preserve the native deferred tool-call identity and SHALL resume a paused run using explicit approved or rejected deferred tool results.

#### Scenario: Approval request pauses

- **WHEN** a tool requiring approval is called
- **THEN** `AgentResult` SHALL report `APPROVAL_NEEDED`
- **AND** each request SHALL retain the upstream tool-call identifier, tool name, arguments, metadata, and continuation association
- **AND** the result SHALL expose an opaque continuation ID equal to the stable upstream run ID
- **AND** it SHALL not expose serialized framework message objects

#### Scenario: Authorized approval resumes

- **WHEN** an authorized caller approves a pending request
- **THEN** resume SHALL load the continuation history from the configured public Harness step store
- **AND** it SHALL supply an approved deferred result through Pydantic AI's `deferred_tool_results` argument
- **AND** the approved tool SHALL execute exactly once
- **AND** the run SHALL continue from its preserved message history

#### Scenario: Rejection resumes safely

- **WHEN** an authorized caller rejects a pending request with a reason
- **THEN** resume SHALL supply a rejected deferred result through Pydantic AI's `deferred_tool_results` argument
- **AND** the protected tool SHALL not execute
- **AND** the model SHALL receive the rejection result

#### Scenario: Invalid continuation

- **WHEN** a decision references an unknown or already-resolved tool-call identifier
- **THEN** resume SHALL reject it without executing a tool

#### Scenario: Durable continuation

- **WHEN** an approval must survive a process restart
- **THEN** the runtime SHALL use a public durable Harness `StepStore`
- **AND** a new process SHALL resume using the same continuation ID

#### Scenario: Process-local continuation

- **WHEN** the configured step store is `InMemoryStepStore`
- **THEN** continuation SHALL be documented and tested as process-local
- **AND** the runtime SHALL not claim restart durability

#### Scenario: No private approval channel

- **WHEN** a paused run resumes
- **THEN** neither `_ApprovalResolutionError` nor an `approved_tools` dependency side channel SHALL determine authorization or continuation

### Requirement: Approval authorization boundary

`agent-core` SHALL accept approval decisions only from a caller that has already authenticated and authorized the approver for the consumer workflow.

#### Scenario: Unauthorized decision

- **WHEN** the consumer cannot establish that the actor is authorized
- **THEN** it SHALL not call runtime resume with that decision
- **AND** the pending workflow SHALL remain paused

### Requirement: BaseAgent public behavior baseline

The stabilization SHALL preserve the documented public behavior of `BaseAgent.run`, streaming, CLI invocation, examples, skills, and result mapping except for the explicitly corrected fail-closed and continuation behavior.

#### Scenario: Golden contract comparison

- **WHEN** the runtime internals change
- **THEN** behavior-level golden tests SHALL compare completed results, usage, iteration limits, skills, tool visibility, hooks, streaming chunks, and approval results
- **AND** any intentional difference SHALL correspond to a requirement in this change
