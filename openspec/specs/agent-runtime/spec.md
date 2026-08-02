## Purpose

Defines supported runtime tool, instruction, and continuation controls for consumers.
## Requirements
### Requirement: AR-3: AgentRuntime Tool Restriction

`AgentRuntime` SHALL apply run-scoped tool visibility through supported Pydantic AI toolsets, `PrepareTools`, or supported agent overrides. It SHALL NOT inspect `_function_toolset`, extract private tool objects, or reconstruct the underlying agent to enforce allow/deny policy.

#### Scenario: Run-scoped allowlist

- **WHEN** a request permits a subset of registered tools
- **THEN** only that subset SHALL be exposed for the run
- **AND** the next run SHALL start from its own effective policy

#### Scenario: Skill-derived policy

- **WHEN** a resolved skill narrows tool visibility
- **THEN** the effective official toolset SHALL reflect the intersection of consumer and skill policy

#### Scenario: Tool metadata preservation

- **WHEN** a tool is retained after filtering
- **THEN** its schema, retries, approval metadata, and owning toolset SHALL remain intact

### Requirement: AR-4: AgentRuntime Instructions Extension

`AgentRuntime` SHALL support base instructions and run-scoped instruction contributions through the supported Pydantic AI instruction APIs. It SHALL NOT reconstruct the underlying agent to add request-specific instructions.

#### Scenario: Base instructions

- **WHEN** an agent is constructed
- **THEN** its base instructions SHALL apply to every run

#### Scenario: Run-scoped instructions

- **WHEN** a request contributes skill, flavor, or consumer instructions
- **THEN** those instructions SHALL apply only to that run

#### Scenario: Concurrent runs

- **WHEN** two runs use different instruction contributions concurrently
- **THEN** neither run SHALL observe the other's instructions

### Requirement: Supported upstream run controls

`AgentRuntime` SHALL expose supported run-level controls needed by consumers without private agent mutation.

#### Scenario: Run-level composition

- **WHEN** a consumer supplies supported per-run instructions, toolsets, capabilities, model settings, or event-stream handling
- **THEN** `AgentRuntime` SHALL pass those values through the supported Pydantic AI run API

#### Scenario: Streaming events

- **WHEN** a consumer requests framework events
- **THEN** the runtime SHALL use the supported event-stream API or `ProcessEventStream`
- **AND** it SHALL not derive lifecycle state from private attributes

### Requirement: Native deferred continuation

Deferred tool requests and results SHALL remain native Pydantic AI values through pause and resume; `AgentResult` SHALL be a compatibility projection rather than a second continuation engine.

#### Scenario: Resume with decisions

- **WHEN** approved and rejected deferred results are supplied
- **THEN** the runtime SHALL pass them through `deferred_tool_results`
- **AND** no private sentinel or `approved_tools` side channel SHALL be required

### Requirement: Explicit tool allowlist semantics
The public `agent-core` composition boundary SHALL distinguish an omitted tool allowlist from an explicitly empty allowlist consistently across immutable runtime profiles, flavor/static preparation, and run-scoped preparation.

#### Scenario: Tool allowlist is omitted
- **WHEN** a consumer omits `tools_allowed` or loads a legacy profile in which the field is absent
- **THEN** the runtime SHALL treat the policy as unrestricted by allowlist while still enforcing deny, approval, authority, and toolset policies
- **AND** it SHALL NOT serialize the omission as an explicit empty collection

#### Scenario: Tool allowlist is explicitly empty
- **WHEN** a consumer supplies an explicit empty `tools_allowed` collection
- **THEN** the runtime SHALL expose no registry tools
- **AND** the consumer SHALL NOT need a fabricated sentinel tool name to express deny-all

#### Scenario: Tool allowlist is bounded
- **WHEN** a consumer supplies one or more canonical tool names
- **THEN** only matching tools that also satisfy static deny, approval, authority, and toolset policy SHALL be visible
- **AND** unknown names SHALL NOT broaden access

#### Scenario: Static and run-scoped policies compose
- **WHEN** static and run-scoped allowlists are both present
- **THEN** effective visibility SHALL be their intersection after deny rules
- **AND** an explicit empty policy at either scope SHALL remain deny-all
